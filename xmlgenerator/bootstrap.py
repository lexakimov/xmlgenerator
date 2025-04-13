import logging

from lxml import etree
from xmlschema import XMLSchema

import xmlgenerator
from xmlgenerator import configuration, validation, randomization, substitution, generator
from xmlgenerator.arguments import parse_args
from xmlgenerator.configuration import load_config
from xmlgenerator.generator import XmlGenerator
from xmlgenerator.randomization import Randomizer
from xmlgenerator.substitution import Substitutor
from xmlgenerator.validation import XmlValidator

# TODO Generator - обработка стандартных xsd типов
# TODO кастомные переменные для локального контекста
# TODO валидация по Schematron
# TODO типизировать
# TODO Почистить и перевести комментарии
# TODO Дописать тесты

logging.basicConfig(level=logging.WARN, format='%(asctime)s [%(name)-26s] %(levelname)-6s - %(message)s')

logger = logging.getLogger('xmlgenerator.bootstrap')


def main():
    try:
        _main()
    except KeyboardInterrupt as ex:
        logger.info('processing interrupted')


def _main():
    args, xsd_files, output_path = parse_args()
    _setup_loggers(args)

    if output_path:
        logger.debug('specified output path: %s', output_path.absolute())
    else:
        logger.debug('output path is not specified. Generated xml will be written to stdout')

    config = load_config(args.config_yaml)

    randomizer = Randomizer(args.seed)
    substitutor = Substitutor(randomizer)
    generator = XmlGenerator(randomizer, substitutor)
    validator = XmlValidator(args.validation, args.fail_fast)

    logger.debug('found %s schemas', len(xsd_files))
    for xsd_file in xsd_files:
        logger.info('processing schema: %s', xsd_file.name)

        # get configuration override for current schema
        local_config = config.get_for_file(xsd_file.name)

        # Reset context for current schema
        substitutor.reset_context(xsd_file.name, local_config)

        # Load XSD schema
        xsd_schema = XMLSchema(xsd_file)  # loglevel='DEBUG'
        # Generate XML document
        xml_root = generator.generate_xml(xsd_schema, local_config)

        # Marshall to string
        xml_str = etree.tostring(xml_root, encoding=args.encoding, pretty_print=args.pretty)
        decoded = xml_str.decode('cp1251' if args.encoding == 'windows-1251' else args.encoding)

        # Print out to console
        if not output_path:
            logger.debug('print xml document to stdout')
            print(decoded)

        # Validation (if enabled)
        validator.validate(xsd_schema, decoded)

        # Get output filename for current schema (without extension)
        xml_filename = substitutor.get_output_filename()

        # Export XML to file
        if output_path:
            output_file = output_path
            if output_path.is_dir():
                output_file = output_path / f'{xml_filename}.xml'
            logger.debug('save xml document as %s', output_file.absolute())
            with open(output_file, 'wb') as f:
                f.write(xml_str)


def _setup_loggers(args):
    log_level = logging.DEBUG if args.debug else logging.INFO
    logger.setLevel(log_level)
    configuration.logger.setLevel(log_level)
    validation.logger.setLevel(log_level)
    xmlgenerator.generator.logger.setLevel(log_level)
    substitution.logger.setLevel(log_level)
    randomization.logger.setLevel(log_level)


if __name__ == "__main__":
    main()
