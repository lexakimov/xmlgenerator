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


@pytest.mark.parametrize("xsd", [
    'string.xsd',
    'boolean.xsd',
    'decimal.xsd',
    'float.xsd',
    'double.xsd',
    'duration.xsd',
    'datetime.xsd',
    'time.xsd',
    'date.xsd',
    'gyearmonth.xsd',
    'gyear.xsd',
    'gmonthday.xsd',
    'gday.xsd',
    'gmonth.xsd',
    'hexbinary.xsd',
    'base64binary.xsd',
    'anyuri.xsd',
    'qname.xsd',
    'notation.xsd',
])
def test_built_in_types(xsd):
    xsd_schema = XMLSchema(f"data/types_built_in/{xsd}")
    local_config = GeneratorConfig()
    generated_xml = generator.generate_xml(xsd_schema, local_config)
    xml_str = etree.tostring(generated_xml, pretty_print=True)
    print(xml_str)
    generated_value = re.sub("<root attributeValue=\"|\"/>\s", "", xml_str.decode('utf-8'))
    print(generated_value)


