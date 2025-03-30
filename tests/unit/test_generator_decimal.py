import os
import re

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
