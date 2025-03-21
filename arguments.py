import sys
from argparse import ArgumentParser, HelpFormatter
from pathlib import Path

'''
# печать help
xmlgenerator

xmlgenerator test.xsd               # генерация из одного файла, вывод в stdout (только xml)

xmlgenerator *.xsd                  # генерация из n файлов, вывод в stdout (только xml)
xmlgenerator path/
xmlgenerator path/*.xsd

xmlgenerator -o test.xml test.xsd   # генерация из одного файла, вывод в файл

xmlgenerator -o out_dir/ test.xsd   # генерация из одного файла, вывод в директорию

xmlgenerator -o out_dir/ *.xsd      # генерация из n файлов, вывод в директорию
xmlgenerator -o out_dir/ path/
xmlgenerator -o out_dir/ path/*.xsd


# xsdxmlgen
# xmlgen
# genxml
# genxmlfromxsd
# xmlgenerator
# xsdgenxml
# xsdtoxml
# xml_
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

    parser = MyParser(
        prog='xmlgenerator',
        description='Generates XML documents from XSD schemas',
        formatter_class=CustomHelpFormatter
        #epilog='Text at the bottom of help'
    )

    parser.add_argument(
        nargs='+',
        metavar="xsd",
        dest="source_paths",
        help="paths to xsd schema(s) or directory with xsd schemas"
    )
    parser.add_argument(
        "-c", "--config",
        metavar="<config.yml>",
        dest="config_yaml",
        help="pass yaml configuration file"
    )
    parser.add_argument(
        "-o", "--output",
        metavar="<output.xml>",
        dest="output_xml",
        help="save output to dir or file"
    )
    parser.add_argument(
        "-p", "--pretty",
        action="store_true",
        help="prettify output XML"
    )
    parser.add_argument(
        "-e", "--encoding",
        metavar="<encoding>",
        choices=["utf-8", "windows-1251"],
        default="utf-8",
        help="output XML encoding (utf-8, windows-1251, default is utf-8)"
    )
    parser.add_argument(
        "-d", "--debug",
        action="store_true",
        help="enable debug mode"
    )
    parser.add_argument(
        "-v", "--version",
        action='version',
        version='%(prog)s 0.1.0',
        help="shows current version"
    )
    parser.add_argument(
        "--seed",
        metavar="<seed>",
        help="set randomization seed"
    )

    args = parser.parse_args()

    # Собираем все .xsd файлы
    xsd_files = []
    for source_path in args.source_paths:
        path = Path(source_path)
        if path.is_dir():
            # Добавляем только файлы с расширением .xsd (без учета регистра)
            xsd_files.extend(path.glob('*.[xX][sS][dD]'))
        elif path.is_file() and path.suffix.lower() == '.xsd':
            # Если это файл с расширением .xsd, добавляем его
            xsd_files.append(path)

    # Сортируем файлы по имени
    xsd_files.sort()

    if not xsd_files:
        parser.error("No source xsd schemas provided.")

    # Обработка пути вывода
    output_path = Path(args.output_xml) if args.output_xml else None

    # Проверка: если несколько XSD файлов, то output должен быть директорией
    if len(xsd_files) > 1 and output_path and not (output_path.is_dir() or args.output_xml.endswith(('/', '\\'))):
        parser.error("Option -o/--output must be a directory when multiple source xsd schemas are provided.")

    # Создание директории, если output указан как директория
    if output_path and (output_path.is_dir() or args.output_xml.endswith(('/', '\\'))):
        output_path.mkdir(parents=True, exist_ok=True)

    return args, xsd_files, output_path
