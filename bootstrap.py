#!/usr/bin/python3

import re

from lxml import etree
from xmlschema import XMLSchema

from arguments import parse_args
from configuration import load_config, default_config
from generator import XmlGenerator
from randomization import Randomizer
from substitution import Substitutor
from validation import XmlValidator


def main():
    args, xsd_files, output_path = parse_args()

    config = load_config(args.config_yaml) if args.config_yaml else default_config()
    output_conf = config.output
    global_conf = config.global_
    local_configs = config.specific

    print(f"Найдено схем: {len(xsd_files)}")

    randomizer = Randomizer()
    substitutor = Substitutor(randomizer)
    generator = XmlGenerator(global_conf, randomizer, substitutor)
    validator = XmlValidator(output_conf.post_validate, output_conf.fail_fast)

    for xsd_file in xsd_files:
        randomizer.reset_context()
        print(f"Processing schema: {xsd_file.name}")

        # get configuration override for current schema
        config_local = _get_local_config(local_configs, xsd_file.name)
        # Generate a filename for the XML file based on the XSD schema name (without extension)
        xml_filename = substitutor.make_filename(xsd_file.name)

        # Load XSD schema
        xsd_schema = XMLSchema(xsd_file)  # loglevel='DEBUG'
        # Generate XML document
        xml_root = generator.generate_xml(xsd_schema, config_local)

        # Marshall to string
        xml_str = etree.tostring(xml_root, encoding=output_conf.encoding, pretty_print=args.pretty)
        decoded = xml_str.decode('cp1251' if output_conf.encoding == 'windows-1251' else output_conf.encoding)

        # Print out to console
        if not output_path:
            print(decoded)

        # Validation (if enabled)
        validator.validate(xsd_schema, decoded)

        # Export XML to file
        if output_path:
            output_file = output_path
            if output_path.is_dir():
                output_file = output_path / f'{xml_filename}.xml'
            with open(output_file, 'wb') as f:
                f.write(xml_str)
            print(f"Saved document: {output_file.name}")


def _get_local_config(local_configs, xsd_name):
    config_local = None
    for pattern, conf in local_configs.items():
        if re.match(pattern, xsd_name):
            config_local = conf
            break
    return config_local


if __name__ == "__main__":
    main()
