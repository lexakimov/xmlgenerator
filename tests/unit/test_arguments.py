import os
import shlex
import sys
from pathlib import Path
from unittest.mock import patch

import pytest

import tests
from xmlgenerator import __version__
from xmlgenerator.arguments import parse_args

os.chdir(os.path.dirname(os.path.abspath(tests.__file__)))


def parse(cmd_line):
    test_args = shlex.split(cmd_line)
    with patch.object(sys, 'argv', test_args):
        return parse_args()


class TestStandardArgs:

    def test_no_args(self, capsys):
        with pytest.raises(SystemExit) as excinfo:
            parse('')

        captured = capsys.readouterr()
        assert excinfo.value.code == 2
        assert 'usage: xmlgenerator [-h]' in captured.out
        assert 'error: the following arguments are required: xsd' in captured.err

    def test_parse_args_help(self, capsys):
        with pytest.raises(SystemExit) as excinfo:
            parse('program -h')

        captured = capsys.readouterr()
        assert excinfo.value.code == 0
        assert 'usage: xmlgenerator [-h]' in captured.out
        assert not captured.err

    def test_parse_args_version(self, capsys):
        with pytest.raises(SystemExit) as excinfo:
            parse('program -V')

        captured = capsys.readouterr()
        assert excinfo.value.code == 0
        assert f'xmlgenerator {__version__}' in captured.out
        assert not captured.err


class TestOneSchema:

    def test_parse_args__one_schema__not_exists(self, capsys):
        with pytest.raises(SystemExit) as excinfo:
            parse('program ../not_existing.xsd')

        captured = capsys.readouterr()
        assert excinfo.value.code == 2
        assert 'usage: xmlgenerator [-h]' in captured.out
        assert 'error: file ../not_existing.xsd doesn\'t exists.' in captured.err

    def test_parse_args__one_schema__exists(self, capsys):
        args, xsd_files, output_path = parse('program data/simple_schemas/schema_1.xsd')

        assert args.debug is False
        assert args.config_yaml is None
        assert args.encoding == 'utf-8'
        assert args.output_path is None
        assert args.pretty is False
        assert args.seed is None
        assert args.ignore_validation_errors is False
        assert len(xsd_files) is 1
        assert output_path is None

        captured = capsys.readouterr()
        assert not captured.out
        assert not captured.err

    def test_parse_args__one_schema__twice(self, capsys):
        args, xsd_files, output_path = parse('program data/simple_schemas/schema_1.xsd data/simple_schemas/schema_1.xsd')

        assert args.debug is False
        assert args.config_yaml is None
        assert args.encoding == 'utf-8'
        assert args.output_path is None
        assert args.pretty is False
        assert args.seed is None
        assert args.ignore_validation_errors is False
        assert len(xsd_files) is 1
        assert output_path is None

        captured = capsys.readouterr()
        assert not captured.out
        assert not captured.err

    def test_parse_args__one_schema__check_output_is_file(self, capsys):
        args, xsd_files, output_path = parse('program -o out.xml data/simple_schemas/schema_1.xsd')

        assert output_path is not None
        assert not output_path.exists()
        assert args.config_yaml is None

    def test_parse_args__one_schema__output_points_to_existing_file(self, capsys, tmp_path):
        existing_file = tmp_path / "existing"
        existing_file.write_text("data")

        args, xsd_files, output_path = parse(f'program -o {existing_file} data/simple_schemas/schema_1.xsd')

        assert output_path == existing_file
        assert existing_file.exists()

    def test_parse_args__one_schema__output_points_to_existing_directory(self, capsys, tmp_path):
        existing_dir = tmp_path / "existing"
        existing_dir.mkdir()
        args, xsd_files, output_path = parse(f'program -o {existing_dir} data/simple_schemas/schema_1.xsd')
        assert output_path == existing_dir
        assert existing_dir.exists()

    def test_parse_args__one_schema__create_output_folder(self, capsys):
        assert not Path("output_dir").exists()
        parse('program -o output_dir/ data/simple_schemas/schema_1.xsd')
        assert Path("output_dir").exists()
        Path("output_dir").rmdir()

    def test_parse_args__one_schema__create_output_folder_without_trailing_slash(self, capsys):
        assert not Path("output_dir").exists()
        parse('program -o output_dir data/simple_schemas/schema_1.xsd')
        assert Path("output_dir").exists()
        Path("output_dir").rmdir()


class TestTwoSchemas:

    def test_parse_args__two_schemas__exists(self, capsys):
        args, xsd_files, output_path = parse('program data/simple_schemas/schema_1.xsd data/simple_schemas/schema_2.xsd')

        assert args.debug is False
        assert args.config_yaml is None
        assert args.encoding == 'utf-8'
        assert args.output_path is None
        assert args.pretty is False
        assert args.seed is None
        assert args.ignore_validation_errors is False
        assert len(xsd_files) is 2
        assert output_path is None

        captured = capsys.readouterr()
        assert not captured.out
        assert not captured.err

    def test_parse_args__two_schemas__check_output_is_dir(self, capsys):
        with pytest.raises(SystemExit) as excinfo:
            parse('program -o out.xml data/simple_schemas/schema_1.xsd data/simple_schemas/schema_2.xsd')

        captured = capsys.readouterr()
        assert excinfo.value.code == 2
        assert 'usage: xmlgenerator [-h]' in captured.out
        assert 'error: option -o/--output must be a directory when multiple schemas are provided.' in captured.err

    def test_parse_args__two_schemas__create_output_folder(self, capsys):
        assert not Path("output_dir").exists()
        parse('program -o output_dir/ data/simple_schemas/schema_1.xsd data/simple_schemas/schema_2.xsd')
        assert Path("output_dir").exists()
        Path("output_dir").rmdir()

    def test_parse_args__two_schemas__create_output_folder_without_trailing_slash(self, capsys):
        assert not Path("output_dir").exists()
        parse('program -o output_dir data/simple_schemas/schema_1.xsd data/simple_schemas/schema_2.xsd')
        assert Path("output_dir").exists()
        Path("output_dir").rmdir()

    def test_parse_args__two_schemas__create_output_folder_with_suffix_and_slash(self, capsys):
        assert not Path("output.dir").exists()
        parse('program -o output.dir/ data/simple_schemas/schema_1.xsd data/simple_schemas/schema_2.xsd')
        assert Path("output.dir").exists()
        Path("output.dir").rmdir()

    def test_parse_args__two_schemas__output_points_to_existing_directory(self, capsys, tmp_path):
        existing_dir = tmp_path / "existing"
        existing_dir.mkdir()
        parse(f'program -o {existing_dir} data/simple_schemas/schema_1.xsd data/simple_schemas/schema_2.xsd')
        assert existing_dir.exists()

    def test_parse_args__two_schemas__output_points_to_existing_file(self, capsys, tmp_path):
        existing_file = tmp_path / "existing"
        existing_file.write_text("data")

        with pytest.raises(SystemExit) as excinfo:
            parse(f'program -o {existing_file} data/simple_schemas/schema_1.xsd data/simple_schemas/schema_2.xsd')

        captured = capsys.readouterr()
        assert excinfo.value.code == 2
        assert f'error: option -o/--output points to existing file {existing_file}. It must be a directory when multiple schemas are provided.' in captured.err


class TestInputFolder:

    def test_parse_args__folder_empty(self, capsys):
        with pytest.raises(SystemExit) as excinfo:
            parse('program ./')

        captured = capsys.readouterr()
        assert excinfo.value.code == 2
        assert 'usage: xmlgenerator [-h]' in captured.out
        assert 'error: no source xsd schemas provided.' in captured.err

    def test_parse_args__folder__not_empty(self, capsys):
        args, xsd_files, output_path = parse('program data/simple_schemas/')

        assert args.debug is False
        assert args.config_yaml is None
        assert args.encoding == 'utf-8'
        assert args.output_path is None
        assert args.pretty is False
        assert args.seed is None
        assert args.ignore_validation_errors is False
        assert len(xsd_files) is 2
        assert 'schema_1.xsd' in [v.name for v in xsd_files]
        assert 'schema_2.xsd' in [v.name for v in xsd_files]
        assert output_path is None
        captured = capsys.readouterr()
        assert not captured.out
        assert not captured.err


class TestConfigFile:

    def test_parse_args__config_file_is_empty(self, capsys):
        args, xsd_files, output_path = parse('program -c data/config_empty.yaml data/simple_schemas/schema_1.xsd')

        assert args.config_yaml is not None
        assert args.ignore_validation_errors is False

    def test_parse_args__ignore_validation_errors_flag(self, capsys):
        args, xsd_files, output_path = parse('program -i data/simple_schemas/schema_1.xsd')

        assert args.ignore_validation_errors is True

    def test_parse_args__config_file_not_exists(self, capsys):
        with pytest.raises(SystemExit) as excinfo:
            parse('program -c not_exists.yml data/simple_schemas/schema_1.xsd')

        captured = capsys.readouterr()
        assert excinfo.value.code == 2
        assert 'usage: xmlgenerator [-h]' in captured.out
        assert 'configuration file not_exists.yml does not exist.' in captured.err


class TestNamespaceAliases:

    def test_parse_args__default_value(self, capsys):
        args, xsd_files, output_path = parse('program data/simple_schemas/schema_1.xsd')

        assert args.ns_aliases is not None
        assert isinstance(args.ns_aliases, dict)
        assert len(args.ns_aliases) is 0

    def test_parse_args__one_flag(self, capsys):
        args, xsd_files, output_path = parse('program -n alias=ns data/simple_schemas/schema_1.xsd')

        assert args.ns_aliases == {"alias": "ns"}

    def test_parse_args__two_flags(self, capsys):
        args, xsd_files, output_path = parse('program -n alias1=ns1 -n alias2=ns2 data/simple_schemas/schema_1.xsd')

        assert args.ns_aliases == {"alias1": "ns1", "alias2": "ns2"}

    def test_parse_args__duplicated_flags(self, capsys):
        with pytest.raises(SystemExit) as excinfo:
            parse('program -n alias1=ns -n alias2=ns data/simple_schemas/schema_1.xsd')

        captured = capsys.readouterr()
        assert excinfo.value.code == 2
        assert 'usage: xmlgenerator [-h]' in captured.out
        assert 'multiple aliases passed for namespace "ns". Check the use of -n/--namespace flags.' in captured.err
