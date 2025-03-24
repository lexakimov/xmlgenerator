import os
import shlex
import sys
from pathlib import Path
from unittest.mock import patch

import pytest

import tests
from xmlgenerator.arguments import parse_args

os.chdir(os.path.dirname(os.path.abspath(tests.__file__)))

def parse(cmd_line):
    test_args = shlex.split(cmd_line)
    with patch.object(sys, 'argv', test_args):
        return parse_args()


def test_no_args(capsys):
    with pytest.raises(SystemExit) as excinfo:
        parse('')

    captured = capsys.readouterr()
    assert excinfo.value.code == 2
    assert 'usage: xmlgenerator [-h]' in captured.out
    assert 'error: the following arguments are required: xsd' in captured.err


def test_parse_args_help(capsys):
    with pytest.raises(SystemExit) as excinfo:
        parse('program -h')

    captured = capsys.readouterr()
    assert excinfo.value.code == 0
    assert 'usage: xmlgenerator [-h]' in captured.out
    assert not captured.err


def test_parse_args_version(capsys):
    with pytest.raises(SystemExit) as excinfo:
        parse('program -V')

    captured = capsys.readouterr()
    assert excinfo.value.code == 0
    assert 'xmlgenerator 0.1.0' in captured.out
    assert not captured.err


def test_parse_args_01(capsys):
    with pytest.raises(SystemExit) as excinfo:
        parse('program ../not_existing.xsd')

    captured = capsys.readouterr()
    assert excinfo.value.code == 2
    assert 'usage: xmlgenerator [-h]' in captured.out
    assert 'error: file ../not_existing.xsd doesn\'t exists.' in captured.err


def test_parse_args_02(capsys):
    args, xsd_files, output_path = parse('program data/existing_1.xsd')

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


def test_parse_args_02_1(capsys):
    args, xsd_files, output_path = parse('program data/existing_1.xsd data/existing_2.xsd')

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


def test_parse_args_02_2(capsys):
    args, xsd_files, output_path = parse('program data/existing_1.xsd data/existing_1.xsd')

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


def test_parse_args_03(capsys):
    args, xsd_files, output_path = parse('program data/')

    assert args.debug is False
    assert args.config_yaml is None
    assert args.encoding == 'utf-8'
    assert args.output_path is None
    assert args.pretty is False
    assert args.seed is None
    assert len(xsd_files) is 2
    assert [v.name for v in xsd_files] == ['existing_1.xsd', 'existing_2.xsd']
    assert output_path is None
    captured = capsys.readouterr()
    assert not captured.out
    assert not captured.err


def test_parse_args_04(capsys):
    with pytest.raises(SystemExit) as excinfo:
        parse('program ./')

    captured = capsys.readouterr()
    assert excinfo.value.code == 2
    assert 'usage: xmlgenerator [-h]' in captured.out
    assert 'error: no source xsd schemas provided.' in captured.err


def test_parse_args_05(capsys):
    args, xsd_files, output_path = parse('program -o out.xml data/existing_1.xsd')

    assert output_path is not None
    assert args.config_yaml is None


def test_parse_args_06(capsys):
    with pytest.raises(SystemExit) as excinfo:
        parse('program -o out.xml data/existing_1.xsd data/existing_2.xsd')

    captured = capsys.readouterr()
    assert excinfo.value.code == 2
    assert 'usage: xmlgenerator [-h]' in captured.out
    assert 'error: option -o/--output must be a directory when multiple source xsd schemas are provided.' in captured.err


def test_parse_args_07(capsys):
    assert not Path("output_dir").exists()
    parse('program -o output_dir/ data/existing_1.xsd data/existing_2.xsd')
    assert Path("output_dir").exists()
    Path("output_dir").rmdir()


def test_parse_args_08(capsys):
    args, xsd_files, output_path = parse('program -c data/config_empty.yaml data/existing_1.xsd')

    assert args.config_yaml is not None


def test_parse_args_09(capsys):
    with pytest.raises(SystemExit) as excinfo:
        parse('program -c not_exists.yml data/existing_1.xsd')

    captured = capsys.readouterr()
    assert excinfo.value.code == 2
    assert 'usage: xmlgenerator [-h]' in captured.out
    assert 'configuration file not_exists.yml does not exist.' in captured.err
