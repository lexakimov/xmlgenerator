#!/usr/bin/python3

import re
from pathlib import Path

from lxml import etree
from xmlschema import XMLSchema

from arguments import parse_args
from cofiguration import load_config
from generator import XmlGenerator
from substitution import init_id_file
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

    generator = XmlGenerator(global_conf)
    validator = XmlValidator(output_conf.post_validate, output_conf.fail_fast)

    for xsd_name in source_conf.file_names:
        print(f"Схема: {xsd_name}")
        xsd_schema_filename = source_conf.directory + xsd_name
        config_local = get_local_config(local_configs, xsd_name)

        # извлекаем префикс
        id_file = init_id_file(xsd_name)

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
        with open(f'{output_conf.directory}/{id_file}.xml', 'wb') as f:
            f.write(xml_str)


def get_local_config(local_configs, xsd_name):
    config_local = None
    for pattern, conf in local_configs.items():
        if re.match(pattern, xsd_name):
            config_local = conf
            break
    return config_local


if __name__ == "__main__":
    main()
