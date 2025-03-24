from lxml import etree
from xmlschema import XMLSchema

from xmlgenerator.arguments import parse_args
from xmlgenerator.configuration import load_config
from xmlgenerator.generator import XmlGenerator
from xmlgenerator.randomization import Randomizer
from xmlgenerator.substitution import Substitutor
from xmlgenerator.validation import XmlValidator


def main():
    args, xsd_files, output_path = parse_args()

    config = load_config(args.config_yaml)

    print(f"Найдено схем: {len(xsd_files)}")

    randomizer = Randomizer(args.seed)
    substitutor = Substitutor(randomizer)
    generator = XmlGenerator(randomizer, substitutor)
    validator = XmlValidator(args.validation, args.fail_fast)

    for xsd_file in xsd_files:
        randomizer.reset_context()
        print(f"Processing schema: {xsd_file.name}")

        # get configuration override for current schema
        config_local = config.get_for_file(xsd_file.name)
        # Generate a filename for the XML file based on the XSD schema name (without extension)
        xml_filename = substitutor.make_filename(xsd_file.name)

        # Load XSD schema
        xsd_schema = XMLSchema(xsd_file)  # loglevel='DEBUG'
        # Generate XML document
        xml_root = generator.generate_xml(xsd_schema, config_local)

        # Marshall to string
        xml_str = etree.tostring(xml_root, encoding=args.encoding, pretty_print=args.pretty)
        decoded = xml_str.decode('cp1251' if args.encoding == 'windows-1251' else args.encoding)

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

if __name__ == "__main__":
    main()
