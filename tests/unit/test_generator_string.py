import os
import re

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
