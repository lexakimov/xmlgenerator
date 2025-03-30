import os
import re
from datetime import datetime

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
