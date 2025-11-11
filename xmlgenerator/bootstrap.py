import logging

from lxml import etree
from xmlschema import XMLSchema

import xmlgenerator
from xmlgenerator.arguments import parse_args
from xmlgenerator.configuration import load_config
from xmlgenerator.generator import XmlGenerator, get_ns_map
from xmlgenerator.randomization import Randomizer
from xmlgenerator.substitution import ExpressionSyntaxError, Substitutor
from xmlgenerator.validation import XmlValidator

# TODO кастомные переменные для локального контекста
# TODO типизировать
# TODO Почистить и перевести комментарии
# TODO Дописать тесты

# TODO _generate_duration
# TODO _generate_base64_binary
# TODO _generate_any_uri
# TODO _generate_qname
# TODO _generate_notation

# TODO _generate_language
# TODO _generate_name
# TODO _generate_nc_name
# TODO _generate_normalized_string
# TODO _generate_token
# TODO _generate_id
# TODO _generate_idref
# TODO _generate_idrefs
# TODO _generate_entity
# TODO _generate_entities
# TODO _generate_nmtoken
# TODO _generate_nmtokens

logging.basicConfig(level=logging.WARN, format='%(asctime)s [%(name)-26s] %(levelname)-6s - %(message)s')

logger = logging.getLogger('xmlgenerator.bootstrap')


def main():
    try:
        _main()
    except ExpressionSyntaxError as ex:
        _log_expression_error(ex)
        exit(1)
    except KeyboardInterrupt as ex:
        logger.info('processing interrupted')


def _main():
    args, xsd_files, output_path = parse_args()
    _setup_loggers(args)

    if output_path:
        logger.debug('specified output path: %s', output_path.absolute())
    else:
        logger.debug('output path is not specified. Generated XML document will be written to stdout')

    config = load_config(args.config_yaml)

    randomizer = Randomizer(args.seed)
    substitutor = Substitutor(randomizer, config.variables)
    generator = XmlGenerator(randomizer, substitutor)
    validator = XmlValidator(args.validation, args.ignore_validation_errors)

    total_count = len(xsd_files)
    logger.debug('found %s schema(s)', total_count)
    for index, xsd_file in enumerate(xsd_files):
        logger.info('processing schema %s of %s: %s', index + 1, total_count, xsd_file.as_uri())

        # get configuration override for current schema
        local_config = config.get_for_file(xsd_file.name)

        # load XSD schema
        xsd_schema = XMLSchema(xsd_file)  # loglevel='DEBUG'

        # get namespace mapping
        ns_map = get_ns_map(xsd_schema, args.ns_aliases)

        root_elements_count = len(xsd_schema.root_elements)
        if root_elements_count > 1:
            logger.debug('schema "%s" contains %s root elements', xsd_file.name, root_elements_count)

        for xsd_root_element in xsd_schema.root_elements:
            # Reset context for current schema and root element
            substitutor.reset_context(xsd_file.name, xsd_root_element.local_name, local_config)
            # Generate XML document
            xml_root = generator.generate_xml(xsd_root_element, local_config, ns_map)
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
                output_file = output_file.absolute()
                logger.debug('save xml document as %s', output_file.as_uri())
                if output_file.exists():
                    logger.warning('file %s already exists and will be overwritten', output_file.as_uri())
                with open(output_file, 'wb') as f:
                    f.write(xml_str)


def _setup_loggers(args):
    logging.addLevelName(logging.WARNING, 'WARN')
    log_level = logging.DEBUG if args.debug else logging.INFO
    logger.setLevel(log_level)
    xmlgenerator.configuration.logger.setLevel(log_level)
    xmlgenerator.validation.logger.setLevel(log_level)
    xmlgenerator.generator.logger.setLevel(log_level)
    xmlgenerator.substitution.logger.setLevel(log_level)
    xmlgenerator.randomization.logger.setLevel(log_level)


def _log_expression_error(exc: ExpressionSyntaxError) -> None:
    pointer_line = ' ' * exc.position + '^ ' + exc.description
    logger.error('Failed to parse expression:')
    logger.error('%s', exc.expression)
    logger.error('%s', pointer_line)


if __name__ == "__main__":
    main()
