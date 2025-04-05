import sys
from argparse import ArgumentParser, HelpFormatter
from pathlib import Path


class MyParser(ArgumentParser):
    def error(self, message):
        sys.stderr.write('error: %s\n' % message)
        self.print_help()
        sys.exit(2)


class CustomHelpFormatter(HelpFormatter):
    def __init__(self, prog):
        super().__init__(prog, max_help_position=36, width=120)


def parse_args():
    parser = MyParser(
        prog='xmlgenerator',
        description='Generates XML documents from XSD schemas',
        formatter_class=CustomHelpFormatter
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
        dest="output_path",
        help="save output to dir or file"
    )
    parser.add_argument(
        "-p", "--pretty",
        action="store_true",
        help="prettify output XML"
    )
    parser.add_argument(
        "-v", "--validation",
        metavar="<validation>",
        choices=["none", "schema", "schematron"],
        default="schema",
        help="validate generated XML document (none, schema, schematron, default is schema)"
    )
    parser.add_argument(
        "-ff", "--fail-fast",
        action="store_true",
        default="true",
        help="terminate execution on validation error (default is true)"
    )
    parser.add_argument(
        "-e", "--encoding",
        metavar="<encoding>",
        choices=["utf-8", "windows-1251"],
        default="utf-8",
        help="output XML encoding (utf-8, windows-1251, default is utf-8)"
    )
    parser.add_argument(
        "--seed",
        metavar="<seed>",
        help="set randomization seed"
    )
    parser.add_argument(
        "-d", "--debug",
        action="store_true",
        help="enable debug mode"
    )
    parser.add_argument(
        "-V", "--version",
        action='version',
        version='%(prog)s 0.1.0',
        help="shows current version"
    )

    args = parser.parse_args()

    if args.config_yaml:
        config_path = Path(args.config_yaml)
        if not config_path.exists() or not config_path.is_file():
            parser.error(f"configuration file {config_path} does not exist.")

    # Собираем все .xsd файлы
    xsd_files = _collect_xsd_files(args.source_paths, parser)

    # Обработка пути вывода
    output_path = Path(args.output_path) if args.output_path else None

    # Проверка: если несколько XSD файлов, то output должен быть директорией
    if len(xsd_files) > 1 and output_path and not (output_path.is_dir() or args.output_path.endswith(('/', '\\'))):
        parser.error("option -o/--output must be a directory when multiple source xsd schemas are provided.")

    # Создание директории, если output указан как директория
    if output_path and (output_path.is_dir() or args.output_path.endswith(('/', '\\'))):
        output_path.mkdir(parents=True, exist_ok=True)

    return args, xsd_files, output_path


def _collect_xsd_files(source_paths, parser):
    xsd_files = []
    for source_path in source_paths:
        path = Path(source_path).resolve()
        if path.is_dir():
            xsd_files.extend(path.glob('*.[xX][sS][dD]'))
        elif path.is_file() and path.suffix.lower() == '.xsd':
            xsd_files.append(path)
        elif not path.exists() and path.suffix.lower() == '.xsd':
            parser.error(f"file {source_path} doesn't exists.")
    if not xsd_files:
        parser.error("no source xsd schemas provided.")
    xsd_files = list(set(xsd_files))
    xsd_files.sort()
    return xsd_files
