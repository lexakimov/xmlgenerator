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
        assert len(xsd_files) is 1
        assert output_path is None

        captured = capsys.readouterr()
        assert not captured.out
        assert not captured.err

    def test_parse_args__one_schema__check_output_is_file(self, capsys):
        args, xsd_files, output_path = parse('program -o out.xml data/simple_schemas/schema_1.xsd')

        assert output_path is not None
        assert args.config_yaml is None


class TestTwoSchemas:

    def test_parse_args__two_schemas__exists(self, capsys):
        args, xsd_files, output_path = parse('program data/simple_schemas/schema_1.xsd data/simple_schemas/schema_2.xsd')

        assert args.debug is False
        assert args.config_yaml is None
        assert args.encoding == 'utf-8'
        assert args.output_path is None
        assert args.pretty is False
        assert args.seed is None
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
        assert 'error: option -o/--output must be a directory when multiple source xsd schemas are provided.' in captured.err

    def test_parse_args__two_schemas__create_output_folder(self, capsys):
        assert not Path("output_dir").exists()
        parse('program -o output_dir/ data/simple_schemas/schema_1.xsd data/simple_schemas/schema_2.xsd')
        assert Path("output_dir").exists()
        Path("output_dir").rmdir()


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

    def test_parse_args__config_file_not_exists(self, capsys):
        with pytest.raises(SystemExit) as excinfo:
            parse('program -c not_exists.yml data/simple_schemas/schema_1.xsd')

        captured = capsys.readouterr()
        assert excinfo.value.code == 2
        assert 'usage: xmlgenerator [-h]' in captured.out
        assert 'configuration file not_exists.yml does not exist.' in captured.err
