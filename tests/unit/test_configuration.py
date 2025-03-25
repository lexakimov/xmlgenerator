import os

import tests
import xmlgenerator.configuration as conf

os.chdir(os.path.dirname(os.path.abspath(tests.__file__)))


def test_load_config_none():
    configuration = conf.load_config(None)

    assert configuration

    assert configuration.global_
    assert configuration.global_.randomization
    assert configuration.global_.randomization.max_occurs is None
    assert configuration.global_.randomization.probability is None
    assert configuration.global_.source_filename is None
    assert configuration.global_.output_filename is None
    assert configuration.global_.value_override is not None
    assert len(configuration.global_.value_override) == 0

    assert configuration.specific is not None
    assert len(configuration.specific) == 0


def test_load_config_empty():
    configuration = conf.load_config('data/config_empty.yaml')
    assert configuration


def test_load_config_non_empty():
    configuration = conf.load_config('data/config_non_empty.yaml')
    assert configuration

    assert configuration.specific is not None
    assert len(configuration.specific) == 3

    assert configuration.specific['Schema_01']
    assert configuration.specific['Schema_01'].randomization is not None
    assert configuration.specific['Schema_01'].value_override is not None

    assert configuration.specific['Schema_02']
    assert configuration.specific['Schema_02'].randomization is not None
    assert configuration.specific['Schema_02'].value_override is not None

    assert configuration.specific['Schema_03']
    assert configuration.specific['Schema_03'].randomization is not None
    assert configuration.specific['Schema_03'].value_override is not None


def test_load_config_non_empty_get_override_1():
    configuration = conf.load_config('data/config_non_empty.yaml')

    config = configuration.get_for_file("Schema_01")
    assert config
    assert config.value_override is not None
    assert len(config.value_override) == 3
    assert config.value_override["Фамилия"] == "last_name-1"
    assert config.value_override["Имя"] == "first_name-2"
    assert config.value_override["Отчество"] == "middle_name-2"


def test_load_config_non_empty_get_override_2():
    configuration = conf.load_config('data/config_non_empty.yaml')

    config = configuration.get_for_file("Schema_02")
    assert config
    assert config.value_override is not None
    assert len(config.value_override) == 2
    assert config.value_override["Фамилия"] == "last_name-1"
    assert config.value_override["Имя"] is None


def test_load_config_non_empty_get_override_3():
    configuration = conf.load_config('data/config_non_empty.yaml')

    config = configuration.get_for_file("Schema_03")
    assert config
    assert config.value_override is not None
    assert len(config.value_override) == 2
    assert config.value_override["Фамилия"] == "last_name-1"
    assert config.value_override["Имя"] == "first_name-1"


def test_load_config_non_empty_get_override_4():
    configuration = conf.load_config('data/config_non_empty.yaml')

    config = configuration.get_for_file("Schema_04")
    assert config
    assert config.value_override is not None
    assert len(config.value_override) == 2
    assert config.value_override["Фамилия"] == "last_name-1"
    assert config.value_override["Имя"] == "first_name-1"
