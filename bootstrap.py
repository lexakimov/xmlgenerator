#!/usr/bin/python3

import re
from pathlib import Path

from lxml import etree
from xmlschema import XMLSchema

from arguments import parse_args
from configuration import load_config
from generator import XmlGenerator
from randomization import Randomizer
from substitution import Substitutor
from validation import XmlValidator


def main():
    args = parse_args()
    config = load_config(args.config_yaml)
    source_conf = config.source
    output_conf = config.output
    global_conf = config.global_
    local_configs = config.specific

    print(f"Найдено схем: {len(source_conf.file_names)}")
    Path(output_conf.directory).mkdir(parents=True, exist_ok=True)

    randomizer = Randomizer()
    substitutor = Substitutor(randomizer)
    generator = XmlGenerator(global_conf, randomizer, substitutor)
    validator = XmlValidator(output_conf.post_validate, output_conf.fail_fast)

    for xsd_name in source_conf.file_names:
        randomizer.reset_context()
        print(f"Processing schema: {xsd_name}")
        xsd_schema_filename = source_conf.directory + xsd_name
        # get configuration override for current schema
        config_local = _get_local_config(local_configs, xsd_name)
        # Generate a filename for the XML file based on the XSD schema name (without extension)
        xml_filename = substitutor.make_filename(xsd_name)

        # Load XSD schema
        xsd_schema = XMLSchema(xsd_schema_filename, )  # loglevel='DEBUG'
        # Generate XML document
        xml_root = generator.generate_xml(xsd_schema, config_local)

        # Marshall to string
        xml_str = etree.tostring(xml_root, encoding=output_conf.encoding, pretty_print=output_conf.pretty)
        decoded = xml_str.decode('cp1251' if output_conf.encoding == 'windows-1251' else output_conf.encoding)

        # Print out to console
        if output_conf.log_result:
            print(decoded)

        # Validation (if enabled)
        validator.validate(xsd_schema, decoded)

        # Export XML to file
        with open(f'{output_conf.directory}/{xml_filename}.xml', 'wb') as f:
            f.write(xml_str)


def _get_local_config(local_configs, xsd_name):
    config_local = None
    for pattern, conf in local_configs.items():
        if re.match(pattern, xsd_name):
            config_local = conf
            break
    return config_local


if __name__ == "__main__":
    main()
