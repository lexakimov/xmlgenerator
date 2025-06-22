import logging
import sys
from argparse import ArgumentParser, HelpFormatter
from pathlib import Path

import shtab

logger = logging.getLogger(__name__)


class MyParser(ArgumentParser):
    def error(self, message):
        sys.stderr.write('error: %s\n' % message)
        self.print_help()
        sys.exit(2)


class CustomHelpFormatter(HelpFormatter):
    def __init__(self, prog):
        super().__init__(prog, max_help_position=36, width=120)


def _get_parser():
    parser = MyParser(
        prog='xmlgenerator',
        description='Generates XML documents from XSD schemas',
        formatter_class=CustomHelpFormatter
    )

    source_arg = parser.add_argument(
        nargs='+',
        metavar="xsd",
        dest="source_paths",
        help="paths to xsd schema(s) or directory with xsd schemas"
    )
    config_arg = parser.add_argument(
        "-c", "--config",
        metavar="<config.yml>",
        dest="config_yaml",
        help="pass a YAML configuration file"
    )
    parser.add_argument(
        "-l", "--locale",
        metavar="<locale>",
        default="en_US",
        help="locale for the randomizer (default: %(default)s)"
    )
    output_arg = parser.add_argument(
        "-o", "--output",
        metavar="<output.xml>",
        dest="output_path",
        help="save the output to a directory or file"
    )
    parser.add_argument(
        "-p", "--pretty",
        action="store_true",
        help="prettify the output XML"
    )
    parser.add_argument(
        "-v", "--validation",
        metavar="<validation>",
        choices=["none", "schema", "schematron"],
        default="schema",
        help="validate the generated XML document (none, schema, schematron; default: %(default)s)"
    )
    parser.add_argument(
        "-ff", "--fail-fast",
        action="store_true",
        default="true",
        help="terminate execution on a validation error (default: %(default)s)"
    )
    parser.add_argument(
        "-e", "--encoding",
        metavar="<encoding>",
        choices=["utf-8", "windows-1251"],
        default="utf-8",
        help="the output XML encoding (utf-8, windows-1251; default: %(default)s)"
    )
    parser.add_argument(
        "-s", "--seed",
        metavar="<seed>",
        help="set the randomization seed"
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
        help="show the current version"
    )

    # add shell completions
    config_arg.complete = shtab.FILE
    source_arg.complete = shtab.FILE
    output_arg.complete = shtab.FILE
    shtab.add_argument_to(parser, ["-C", "--completion"], "print a shell completion script (bash, zsh, tcsh)")
    completion_act = [a for a in parser._actions if a.dest == 'completion']
    if completion_act:
        completion_act[0].metavar = '<shell>'

    return parser


def parse_args():
    parser = _get_parser()
    args = parser.parse_args()

    # setup logger
    log_level = logging.DEBUG if args.debug else logging.INFO
    logger.setLevel(log_level)

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
