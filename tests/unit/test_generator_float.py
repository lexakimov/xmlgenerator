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


def test_restriction_float_pattern():
    xsd_schema = XMLSchema("data/types_built_in_restricted/float_pattern.xsd")
    local_config = GeneratorConfig()
    generated_xml = generator.generate_xml(xsd_schema, local_config)
    xml_str = etree.tostring(generated_xml, pretty_print=True)
    generated_value = re.sub("<root attributeValue=\"|\"/>\s", "", xml_str.decode('utf-8'))
    assert re.match(r'[-+]?[0-9]*\.?[0-9]+([eE][-+]?[0-9]+)?', generated_value)


@pytest.mark.flaky(reruns=10)
def test_restriction_float_enumeration():
    xsd_schema = XMLSchema("data/types_built_in_restricted/float_enumeration.xsd")
    local_config = GeneratorConfig()
    generated_xml = generator.generate_xml(xsd_schema, local_config)
    xml_str = etree.tostring(generated_xml, pretty_print=True)
    generated_value = re.sub("<root attributeValue=\"|\"/>\s", "", xml_str.decode('utf-8'))
    valid_values = ['1.5', '2.5', '3.5']
    assert generated_value in valid_values


def test_restriction_float_whitespace():
    xsd_schema = XMLSchema("data/types_built_in_restricted/float_whitespace.xsd")
    local_config = GeneratorConfig()
    generated_xml = generator.generate_xml(xsd_schema, local_config)
    xml_str = etree.tostring(generated_xml, pretty_print=True)
    generated_value = re.sub("<root attributeValue=\"|\"/>\s", "", xml_str.decode('utf-8'))
    assert ' ' not in generated_value


@pytest.mark.flaky(reruns=10)
def test_restriction_float_inclusive():
    xsd_schema = XMLSchema("data/types_built_in_restricted/float_inclusive.xsd")
    local_config = GeneratorConfig()
    generated_xml = generator.generate_xml(xsd_schema, local_config)
    xml_str = etree.tostring(generated_xml, pretty_print=True)
    generated_value = float(re.sub("<root attributeValue=\"|\"/>\s", "", xml_str.decode('utf-8')))
    assert 0.0 <= generated_value <= 100.0


@pytest.mark.flaky(reruns=10)
def test_restriction_float_exclusive():
    xsd_schema = XMLSchema("data/types_built_in_restricted/float_exclusive.xsd")
    local_config = GeneratorConfig()
    generated_xml = generator.generate_xml(xsd_schema, local_config)
    xml_str = etree.tostring(generated_xml, pretty_print=True)
    generated_value = float(re.sub("<root attributeValue=\"|\"/>\s", "", xml_str.decode('utf-8')))
    assert -1.0 < generated_value < 101.0
