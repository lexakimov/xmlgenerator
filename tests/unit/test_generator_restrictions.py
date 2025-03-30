import os
import re
from datetime import datetime

import pytest
from lxml import etree
from xmlschema import XMLSchema

import tests
from xmlgenerator.configuration import GeneratorConfig
from xmlgenerator.generator import XmlGenerator
from xmlgenerator.randomization import Randomizer
from xmlgenerator.substitution import Substitutor

os.chdir(os.path.dirname(os.path.abspath(tests.__file__)))

randomizer = Randomizer()
substitutor = Substitutor(randomizer)
generator = XmlGenerator(randomizer, substitutor)


def test_restriction_string_length():
    xsd_schema = XMLSchema(f"data/types_built_in_restricted/string_length.xsd")
    local_config = GeneratorConfig()
    generated_xml = generator.generate_xml(xsd_schema, local_config)
    xml_str = etree.tostring(generated_xml, pretty_print=True)
    print(xml_str)
    generated_value = re.sub("<root attributeValue=\"|\"/>\s", "", xml_str.decode('utf-8'))
    assert len(generated_value) == 10


@pytest.mark.flaky(reruns=10)
def test_restriction_string_length_min_max():
    xsd_schema = XMLSchema(f"data/types_built_in_restricted/string_length_min_max.xsd")
    local_config = GeneratorConfig()
    generated_xml = generator.generate_xml(xsd_schema, local_config)
    xml_str = etree.tostring(generated_xml, pretty_print=True)
    print(xml_str)
    generated_value = re.sub("<root attributeValue=\"|\"/>\s", "", xml_str.decode('utf-8'))
    assert len(generated_value) in range(10, 21)


@pytest.mark.flaky(reruns=10)
def test_restriction_string_enumeration():
    xsd_schema = XMLSchema("data/types_built_in_restricted/string_enumeration.xsd")
    local_config = GeneratorConfig()
    generated_xml = generator.generate_xml(xsd_schema, local_config)
    xml_str = etree.tostring(generated_xml, pretty_print=True)
    generated_value = re.sub("<root attributeValue=\"|\"/>\s", "", xml_str.decode('utf-8'))
    valid_values = ['red', 'green', 'blue']
    assert generated_value in valid_values


@pytest.mark.flaky(reruns=10)
def test_restriction_string_pattern():
    xsd_schema = XMLSchema("data/types_built_in_restricted/string_pattern.xsd")
    local_config = GeneratorConfig()
    generated_xml = generator.generate_xml(xsd_schema, local_config)
    xml_str = etree.tostring(generated_xml, pretty_print=True)
    generated_value = re.sub("<root attributeValue=\"|\"/>\s", "", xml_str.decode('utf-8'))
    assert re.match(r'[A-Z]{2}\d{3}', generated_value)


def test_restriction_string_white_space():
    xsd_schema = XMLSchema("data/types_built_in_restricted/string_whitespace.xsd")
    local_config = GeneratorConfig()
    generated_xml = generator.generate_xml(xsd_schema, local_config)
    xml_str = etree.tostring(generated_xml, pretty_print=True)
    generated_value = re.sub("<root attributeValue=\"|\"/>\s", "", xml_str.decode('utf-8'))
    assert ' ' not in generated_value


def test_restriction_integer_inclusive_min_max():
    xsd_schema = XMLSchema("data/types_built_in_restricted/integer_inclusive_min_max.xsd")
    local_config = GeneratorConfig()
    generated_xml = generator.generate_xml(xsd_schema, local_config)
    xml_str = etree.tostring(generated_xml, pretty_print=True)
    generated_value = int(re.sub("<root attributeValue=\"|\"/>\s", "", xml_str.decode('utf-8')))
    assert 10 <= generated_value <= 100


def test_restriction_decimal_total_digits():
    xsd_schema = XMLSchema("data/types_built_in_restricted/decimal_total_digits.xsd")
    local_config = GeneratorConfig()
    generated_xml = generator.generate_xml(xsd_schema, local_config)
    xml_str = etree.tostring(generated_xml, pretty_print=True)
    generated_value = re.sub("<root attributeValue=\"|\"/>\s", "", xml_str.decode('utf-8'))
    assert len(generated_value) == 5


def test_restriction_decimal_fraction_digits():
    xsd_schema = XMLSchema("data/types_built_in_restricted/decimal_fraction_digits.xsd")
    local_config = GeneratorConfig()
    generated_xml = generator.generate_xml(xsd_schema, local_config)
    xml_str = etree.tostring(generated_xml, pretty_print=True)
    generated_value = re.sub("<root attributeValue=\"|\"/>\s", "", xml_str.decode('utf-8'))
    decimal_part = generated_value.split('.')[1]
    assert len(decimal_part) <= 2


def test_restriction_date_min_max():
    xsd_schema = XMLSchema("data/types_built_in_restricted/date_inclusive_min_max.xsd")
    local_config = GeneratorConfig()
    generated_xml = generator.generate_xml(xsd_schema, local_config)
    xml_str = etree.tostring(generated_xml, pretty_print=True)
    generated_value = re.sub("<root attributeValue=\"|\"/>\s", "", xml_str.decode('utf-8'))
    date_value = datetime.strptime(generated_value, '%Y-%m-%d')
    min_date = datetime(2020, 1, 1)
    max_date = datetime(2025, 12, 31)
    assert min_date <= date_value <= max_date
