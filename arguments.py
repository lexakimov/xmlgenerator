import sys
from argparse import ArgumentParser, HelpFormatter

'''
# Печать help
xmlgenerator

# Генерация из одного файла, вывод в stdout (только XML)
xmlgenerator -s test.xsd

# Генерация из ОДНОГО файла, вывод в stdout (только XML) + глобальные параметры
xmlgenerator -s test.xsd -c config.yml

# Генерация из одного файла, вывод в файл (только XML)
xmlgenerator -s test.xsd -o test.xml

# Генерация из одного файла, вывод в файл (только XML) + глобальные параметры
xmlgenerator -s test.xsd -o test.xml -c config.yml

# Источники должны быть описаны в конфигурационном файле. Вывод в stdout (только XML).
xmlgenerator -c config.yml

'''

def parse_args():
    class MyParser(ArgumentParser):
        def error(self, message):
            sys.stderr.write('error: %s\n' % message)
            self.print_help()
            sys.exit(2)

    class CustomHelpFormatter(HelpFormatter):
        def __init__(self, prog):
            super().__init__(prog, max_help_position=36, width=120)

    # xsdxmlgen
    # xmlgen
    # genxml
    # genxmlfromxsd
    # xmlgenerator
    # xsdgenxml
    # xsdtoxml
    # xml_
    parser = MyParser(
        prog='xmlgenerator',
        description='Generates XML documents from XSD schemas',
        formatter_class=CustomHelpFormatter
        #epilog='Text at the bottom of help'
    )

    parser.add_argument("-s", "--schema", metavar="<source.xsd>", dest="source_xsd", help="select the source xsd schema")
    parser.add_argument("-o", "--output", metavar="<output.xml>", dest="output_xml", help="save result to file")
    parser.add_argument("-c", "--config", metavar="<config.yml>", dest="config_yaml", help="pass yaml configuration file")
    parser.add_argument("-d", "--debug", action="store_true", help="enable debug mode")
    parser.add_argument("-v", "--version", action='version', version='%(prog)s 0.1.0', help="shows current version")
    parser.add_argument("--seed", help="set randomization seed")

    return parser.parse_args()
