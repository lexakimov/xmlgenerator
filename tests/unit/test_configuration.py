import os

import tests
import xmlgenerator.configuration as conf

os.chdir(os.path.dirname(os.path.abspath(tests.__file__)))


def test_load_config_no_file():
    configuration = conf.load_config(None)

    assert configuration
    assert configuration.global_
    assert configuration.global_.randomization
    assert configuration.global_.randomization.max_occurs is None
    assert configuration.global_.randomization.probability is None
    assert configuration.global_.source_filename == '(?P<extracted>.*).(xsd|XSD)'
    assert configuration.global_.output_filename == '{{ source_filename }}_{{ uuid }}'
    assert configuration.global_.value_override is not None
    assert len(configuration.global_.value_override) == 0
    assert configuration.specific is not None
    assert len(configuration.specific) == 0


def test_load_config_empty_file():
    configuration = conf.load_config('data/config_empty.yaml')

    assert configuration
    assert configuration.global_
    assert configuration.global_.source_filename == '(?P<extracted>.*).(xsd|XSD)'
    assert configuration.global_.output_filename == '{{ source_filename }}_{{ uuid }}'
    assert configuration.specific is not None
    assert len(configuration.specific) == 0


def test_load_config_non_empty():
    configuration = conf.load_config('data/config_value_override.yaml')

    assert configuration
    assert configuration.specific is not None
    assert len(configuration.specific) == 3
    assert configuration.specific['Schema_01']
    assert configuration.specific['Schema_01'].source_filename == 'from local - Schema_01 (source)'
    assert configuration.specific['Schema_01'].output_filename is None
    assert configuration.specific['Schema_01'].randomization is not None
    assert configuration.specific['Schema_01'].value_override is not None

    assert configuration.specific['Schema_02']
    assert configuration.specific['Schema_02'].source_filename == 'from local - Schema_02 (source)'
    assert configuration.specific['Schema_02'].output_filename == 'from local - Schema_02 (output)'
    assert configuration.specific['Schema_02'].randomization is not None
    assert configuration.specific['Schema_02'].value_override is not None

    assert configuration.specific['Schema_03']
    assert configuration.specific['Schema_03'].source_filename is None
    assert configuration.specific['Schema_03'].output_filename is None
    assert configuration.specific['Schema_03'].randomization is not None
    assert configuration.specific['Schema_03'].value_override is not None


def test_get_for_file_merge_local_and_global_1():
    configuration = conf.load_config('data/config_value_override.yaml')
    config = configuration.get_for_file("Schema_01")

    assert config
    assert config.source_filename == 'from local - Schema_01 (source)'
    assert config.output_filename == '{{ source_filename }}_{{ uuid }}'
    assert config.value_override is not None
    assert len(config.value_override) == 3
    assert config.value_override["Фамилия"] == "last_name-1"
    assert config.value_override["Имя"] == "first_name-2"
    assert config.value_override["Отчество"] == "middle_name-2"


def test_get_for_file_merge_local_and_global_2():
    configuration = conf.load_config('data/config_value_override.yaml')
    config = configuration.get_for_file("Schema_02")

    assert config
    assert config.source_filename == 'from local - Schema_02 (source)'
    assert config.output_filename == 'from local - Schema_02 (output)'
    assert config.value_override is not None
    assert len(config.value_override) == 2
    assert config.value_override["Фамилия"] == "last_name-1"
    assert config.value_override["Имя"] is None


def test_get_for_file_merge_local_and_global_3():
    configuration = conf.load_config('data/config_value_override.yaml')
    config = configuration.get_for_file("Schema_03")

    assert config
    assert config.source_filename == 'pattern from global (source)'
    assert config.output_filename == '{{ source_filename }}_{{ uuid }}'
    assert config.value_override is not None
    assert len(config.value_override) == 2
    assert config.value_override["Фамилия"] == "last_name-1"
    assert config.value_override["Имя"] == "first_name-1"


def test_get_for_file_merge_local_and_global_4():
    configuration = conf.load_config('data/config_value_override.yaml')
    config = configuration.get_for_file("Schema_04")

    assert config
    assert config.source_filename == 'pattern from global (source)'
    assert config.output_filename == '{{ source_filename }}_{{ uuid }}'
    assert config.value_override is not None
    assert len(config.value_override) == 2
    assert config.value_override["Фамилия"] == "last_name-1"
    assert config.value_override["Имя"] == "first_name-1"


def test_load_config_overlapping_patterns():
    configuration = conf.load_config('data/config_overlapping_patterns.yaml')

    config = configuration.get_for_file("Schema_ABC")
    assert config.output_filename == "pattern1"

    # Should use the config from the first matching pattern 'Schema_.*'
    config = configuration.get_for_file("Schema_A")
    assert config.output_filename == "pattern2"

    # Should use the config from the first matching pattern 'Schema_.*'
    config = configuration.get_for_file("Schema_B")
    assert config.output_filename == "pattern2"
