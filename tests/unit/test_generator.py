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
local_config = GeneratorConfig()


def log_xml(generated_xml):
    print(etree.tostring(generated_xml, pretty_print=True).decode('utf-8'))


def value(schema_path, xpath) -> list[str]:
    xsd_schema = XMLSchema(schema_path)
    generated_xml = generator.generate_xml(xsd_schema, local_config)
    log_xml(generated_xml)
    return generated_xml.xpath(xpath)


class TestSimple:
    class TestBuiltInTypes:

        def test_string(self):
            xsd_schema = XMLSchema(f"data/simple/types_built_in/string.xsd")
            generated_xml = generator.generate_xml(xsd_schema, local_config)
            log_xml(generated_xml)
            generated_value = generated_xml.xpath("/root/text()")
            assert generated_value
            assert re.match("\w+", generated_value[0])

        def test_boolean(self):
            xsd_schema = XMLSchema(f"data/simple/types_built_in/boolean.xsd")
            generated_xml = generator.generate_xml(xsd_schema, local_config)
            log_xml(generated_xml)
            generated_value = generated_xml.xpath("/root/text()")
            assert generated_value
            assert re.match("true|false", generated_value[0])

        def test_decimal(self):
            xsd_schema = XMLSchema(f"data/simple/types_built_in/decimal.xsd")
            generated_xml = generator.generate_xml(xsd_schema, local_config)
            log_xml(generated_xml)
            generated_value = generated_xml.xpath("/root/text()")
            assert generated_value
            assert re.match("[0-9-.]+", generated_value[0])

        def test_float(self):
            xsd_schema = XMLSchema(f"data/simple/types_built_in/float.xsd")
            generated_xml = generator.generate_xml(xsd_schema, local_config)
            log_xml(generated_xml)
            generated_value = generated_xml.xpath("/root/text()")
            assert generated_value
            assert re.match("[0-9-.]+", generated_value[0])

        def test_double(self):
            xsd_schema = XMLSchema(f"data/simple/types_built_in/double.xsd")
            generated_xml = generator.generate_xml(xsd_schema, local_config)
            log_xml(generated_xml)
            generated_value = generated_xml.xpath("/root/text()")
            assert generated_value
            assert re.match("[0-9-.]+", generated_value[0])

        @pytest.mark.parametrize("xsd", [
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
        def test_built_in_types_in_tags(self, xsd):
            xsd_schema = XMLSchema(f"data/simple/types_built_in/{xsd}")
            generated_xml = generator.generate_xml(xsd_schema, local_config)
            log_xml(generated_xml)
            generated_value = generated_xml.xpath("/root/text()")
            assert generated_value


class TestComplex:
    class TestAttributes:

        class TestBuiltInTypes:

            def test_string(self):
                generated_value = value(
                    "data/complex/attributes/types_built_in/string.xsd",
                    "/root/@attributeValue"
                )
                assert generated_value
                assert re.match("\w+", generated_value[0])

            def test_boolean(self):
                generated_value = value(
                    "data/complex/attributes/types_built_in/boolean.xsd",
                    "/root/@attributeValue"
                )
                assert generated_value
                assert re.match("true|false", generated_value[0])

            def test_decimal(self):
                generated_value = value(
                    "data/complex/attributes/types_built_in/decimal.xsd",
                    "/root/@attributeValue"
                )
                assert generated_value
                assert re.match("[0-9-.]+", generated_value[0])

            def test_float(self):
                generated_value = value(
                    "data/complex/attributes/types_built_in/float.xsd",
                    "/root/@attributeValue"
                )
                assert generated_value
                assert re.match("[0-9-.]+", generated_value[0])

            def test_double(self):
                generated_value = value(
                    "data/complex/attributes/types_built_in/double.xsd",
                    "/root/@attributeValue"
                )
                assert generated_value
                assert re.match("[0-9-.]+", generated_value[0])

            @pytest.mark.parametrize("xsd", [
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
            def test_built_in_types_in_attributes(self, xsd):
                generated_value = value(
                    f"data/complex/attributes/types_built_in/{xsd}.xsd",
                    "/root/@attributeValue"
                )
                assert generated_value

        class TestBuiltInRestrictedTypes:

            def test_string_length(self):
                generated_value = value(
                    "data/complex/attributes/types_built_in_restricted/string_length.xsd",
                    "/root/@attributeValue"
                )
                assert len(generated_value[0]) == 10

            @pytest.mark.flaky(reruns=10)
            def test_string_length_min_max(self):
                generated_value = value(
                    "data/complex/attributes/types_built_in_restricted/string_length_min_max.xsd",
                    "/root/@attributeValue"
                )
                assert len(generated_value[0]) in range(10, 21)

            @pytest.mark.flaky(reruns=10)
            def test_string_enumeration(self):
                generated_value = value(
                    "data/complex/attributes/types_built_in_restricted/string_enumeration.xsd",
                    "/root/@attributeValue"
                )
                valid_values = ['red', 'green', 'blue']
                assert generated_value[0] in valid_values

            @pytest.mark.flaky(reruns=10)
            def test_string_pattern(self):
                generated_value = value(
                    "data/complex/attributes/types_built_in_restricted/string_pattern.xsd",
                    "/root/@attributeValue"
                )
                assert re.match(r'[A-Z]{2}\d{3}', generated_value[0])

            def test_string_white_space(self):
                generated_value = value(
                    "data/complex/attributes/types_built_in_restricted/string_whitespace.xsd",
                    "/root/@attributeValue"
                )
                assert ' ' not in generated_value[0]

            def test_decimal_total_digits(self):
                generated_value = value(
                    "data/complex/attributes/types_built_in_restricted/decimal_total_digits.xsd",
                    "/root/@attributeValue"
                )
                assert len(generated_value[0]) == 5

            def test_decimal_fraction_digits(self):
                generated_value = value(
                    "data/complex/attributes/types_built_in_restricted/decimal_fraction_digits.xsd",
                    "/root/@attributeValue"
                )
                decimal_part = generated_value[0].split('.')[1]
                assert len(decimal_part) <= 2

            def test_float_pattern(self):
                generated_value = value(
                    "data/complex/attributes/types_built_in_restricted/float_pattern.xsd",
                    "/root/@attributeValue"
                )
                assert re.match(r'[-+]?[0-9]*\.?[0-9]+([eE][-+]?[0-9]+)?', generated_value[0])

            @pytest.mark.flaky(reruns=10)
            def test_float_enumeration(self):
                generated_value = value(
                    "data/complex/attributes/types_built_in_restricted/float_enumeration.xsd",
                    "/root/@attributeValue"
                )
                valid_values = ['1.5', '2.5', '3.5']
                assert generated_value[0] in valid_values

            def test_float_whitespace(self):
                generated_value = value(
                    "data/complex/attributes/types_built_in_restricted/float_whitespace.xsd",
                    "/root/@attributeValue"
                )
                assert ' ' not in generated_value[0]

            @pytest.mark.flaky(reruns=10)
            def test_float_inclusive(self):
                generated_value = value(
                    "data/complex/attributes/types_built_in_restricted/float_inclusive.xsd",
                    "/root/@attributeValue"
                )
                assert 0.0 <= float(generated_value[0]) <= 100.0

            @pytest.mark.flaky(reruns=10)
            def test_float_exclusive(self):
                generated_value = value(
                    "data/complex/attributes/types_built_in_restricted/float_exclusive.xsd",
                    "/root/@attributeValue"
                )
                assert -1.0 < float(generated_value[0]) < 101.0

            def test_double_pattern(self):
                generated_value = value(
                    "data/complex/attributes/types_built_in_restricted/double_pattern.xsd",
                    "/root/@attributeValue"
                )
                assert re.match(r'[-+]?[0-9]*\.?[0-9]+([eE][-+]?[0-9]+)?', generated_value[0])

            @pytest.mark.flaky(reruns=10)
            def test_double_enumeration(self):
                generated_value = value(
                    "data/complex/attributes/types_built_in_restricted/double_enumeration.xsd",
                    "/root/@attributeValue"
                )
                valid_values = ['1.5', '2.5', '3.5']
                assert generated_value[0] in valid_values

            def test_double_whitespace(self):
                generated_value = value(
                    "data/complex/attributes/types_built_in_restricted/double_whitespace.xsd",
                    "/root/@attributeValue"
                )
                assert ' ' not in generated_value[0]

            @pytest.mark.flaky(reruns=10)
            def test_double_inclusive(self):
                generated_value = value(
                    "data/complex/attributes/types_built_in_restricted/double_inclusive.xsd",
                    "/root/@attributeValue"
                )
                assert 0.0 <= float(generated_value[0]) <= 100.0

            @pytest.mark.flaky(reruns=10)
            def test_double_exclusive(self):
                generated_value = value(
                    "data/complex/attributes/types_built_in_restricted/double_exclusive.xsd",
                    "/root/@attributeValue"
                )
                assert -1.0 < float(generated_value[0]) < 101.0

            def test_date_min_max(self):
                generated_value = value(
                    "data/complex/attributes/types_built_in_restricted/date_inclusive_min_max.xsd",
                    "/root/@attributeValue"
                )
                date_value = datetime.strptime(generated_value[0], '%Y-%m-%d')
                assert datetime(2020, 1, 1) <= date_value <= datetime(2025, 12, 31)

        class TestDerivedRestrictedTypes:

            def test_integer_inclusive_min_max(self):
                generated_value = value(
                    "data/complex/attributes/types_derived_restricted/integer_inclusive_min_max.xsd",
                    "/root/@attributeValue")
                assert 10 <= int(generated_value[0]) <= 100

    class TestAll:

        def test_occurs_optional(self):
            xsd_schema = XMLSchema("data/complex/all/occurs_optional.xsd")
            counts = {
                "FirstName": [],
                "LastName": [],
            }
            for _ in range(100):
                generated_xml = generator.generate_xml(xsd_schema, local_config)
                counts['FirstName'].append(len(generated_xml.xpath("/root/FirstName/text()")))
                counts['LastName'].append(len(generated_xml.xpath("/root/LastName/text()")))

            first_name_unique_counts = set(counts['FirstName'])
            last_name_unique_counts = set(counts['LastName'])
            # TODO
            assert len(first_name_unique_counts) == 2, "Опциональный элемент всегда генерируется одинаково"
            assert len(last_name_unique_counts) == 2, "Опциональный элемент всегда генерируется одинаково"

        def test_occurs_required(self):
            xsd_schema = XMLSchema("data/complex/all/occurs_required.xsd")
            counts = {
                "FirstName": [],
                "LastName": [],
            }
            for _ in range(100):
                generated_xml = generator.generate_xml(xsd_schema, local_config)
                counts['FirstName'].append(len(generated_xml.xpath("/root/FirstName/text()")))
                counts['LastName'].append(len(generated_xml.xpath("/root/LastName/text()")))

            first_name_unique_counts = set(counts['FirstName'])
            last_name_unique_counts = set(counts['LastName'])

            assert len(first_name_unique_counts) == 2, "Опциональный элемент всегда генерируется одинаково"
            assert len(last_name_unique_counts) == 1, "Опциональный элемент всегда генерируется одинаково"

    class TestChoice:

        def test_occurs_0_1_variations(self):
            xsd_schema = XMLSchema("data/complex/choice/occurs_0_1.xsd")
            counts = []
            for _ in range(100):
                generated_xml = generator.generate_xml(xsd_schema, local_config)
                counts.append(len(generated_xml.findall("optional")))
            unique_counts = set(counts)
            assert len(unique_counts) == 2, "Опциональный элемент всегда генерируется одинаково"

        def test_occurs_0_3_variations(self):
            xsd_schema = XMLSchema("data/complex/choice/occurs_0_3.xsd")
            counts = []
            for _ in range(100):
                generated_xml = generator.generate_xml(xsd_schema, local_config)
                counts.append(len(generated_xml.findall("zeroToThree")))
            unique_counts = set(counts)
            assert len(unique_counts) == 4, "Опциональный элемент всегда генерируется одинаково"
            for count in unique_counts:
                assert 0 <= count <= 3

        def test_occurs_1_1(self):
            xsd_schema = XMLSchema("data/complex/choice/occurs_1_1.xsd")
            counts = []
            for _ in range(100):
                generated_xml = generator.generate_xml(xsd_schema, local_config)
                counts.append(len(generated_xml.findall("required")))
            unique_counts = set(counts)
            assert len(unique_counts) == 1
            assert list(unique_counts)[0] == 1

        def test_occurs_2_5(self):
            xsd_schema = XMLSchema("data/complex/choice/occurs_2_5.xsd")
            counts = []
            for _ in range(100):
                generated_xml = generator.generate_xml(xsd_schema, local_config)
                counts.append(len(generated_xml.findall("twoToFive")))
            unique_counts = set(counts)
            assert len(unique_counts) == 4
            for count in unique_counts:
                assert 2 <= count <= 5

        def test_occurs_unbounded_at_least_one_element(self):
            xsd_schema = XMLSchema("data/complex/choice/occurs_unbounded.xsd")
            counts = []
            for _ in range(100):
                generated_xml = generator.generate_xml(xsd_schema, local_config)
                counts.append(len(generated_xml.findall("atLeastOne")))

            assert 20 < len(set(counts)) <= 100, \
                f"Элемент atLeastOne всегда генерируется с одинаковым количеством экземпляров"

        def test_occurs_unbounded_zero_or_more_elements(self):
            xsd_schema = XMLSchema("data/complex/choice/occurs_unbounded.xsd")
            counts = []
            for _ in range(100):
                generated_xml = generator.generate_xml(xsd_schema, local_config)
                counts.append(len(generated_xml.findall("zeroOrMore")))

            assert 20 < len(set(counts)) <= 100, \
                f"Элемент zeroOrMore всегда генерируется с одинаковым количеством экземпляров"

    class TestSequence:

        def test_occurs_0_1_variations(self):
            xsd_schema = XMLSchema("data/complex/sequence/occurs_0_1.xsd")
            counts = []
            for _ in range(100):
                generated_xml = generator.generate_xml(xsd_schema, local_config)
                counts.append(len(generated_xml.findall("optional")))
            unique_counts = set(counts)
            assert len(unique_counts) == 2, "Опциональный элемент всегда генерируется одинаково"

        def test_occurs_0_3_variations(self):
            xsd_schema = XMLSchema("data/complex/sequence/occurs_0_3.xsd")
            counts = []
            for _ in range(100):
                generated_xml = generator.generate_xml(xsd_schema, local_config)
                counts.append(len(generated_xml.findall("zeroToThree")))
            unique_counts = set(counts)
            assert len(unique_counts) == 4, "Опциональный элемент всегда генерируется одинаково"
            for count in unique_counts:
                assert 0 <= count <= 3

        def test_occurs_1_1(self):
            xsd_schema = XMLSchema("data/complex/sequence/occurs_1_1.xsd")
            counts = []
            for _ in range(100):
                generated_xml = generator.generate_xml(xsd_schema, local_config)
                counts.append(len(generated_xml.findall("required")))
            unique_counts = set(counts)
            assert len(unique_counts) == 1
            assert list(unique_counts)[0] == 1

        def test_occurs_2_5(self):
            xsd_schema = XMLSchema("data/complex/sequence/occurs_2_5.xsd")
            counts = []
            for _ in range(100):
                generated_xml = generator.generate_xml(xsd_schema, local_config)
                counts.append(len(generated_xml.findall("twoToFive")))
            unique_counts = set(counts)
            assert len(unique_counts) == 4
            for count in unique_counts:
                assert 2 <= count <= 5

        def test_occurs_unbounded_at_least_one_element(self):
            xsd_schema = XMLSchema("data/complex/sequence/occurs_unbounded.xsd")
            counts = []
            for _ in range(100):
                generated_xml = generator.generate_xml(xsd_schema, local_config)
                counts.append(len(generated_xml.findall("atLeastOne")))

            assert 20 < len(set(counts)) <= 100, \
                f"Элемент atLeastOne всегда генерируется с одинаковым количеством экземпляров"

        def test_occurs_unbounded_zero_or_more_elements(self):
            xsd_schema = XMLSchema("data/complex/sequence/occurs_unbounded.xsd")
            counts = []
            for _ in range(100):
                generated_xml = generator.generate_xml(xsd_schema, local_config)
                counts.append(len(generated_xml.findall("zeroOrMore")))

            assert 20 < len(set(counts)) <= 100, \
                f"Элемент zeroOrMore всегда генерируется с одинаковым количеством экземпляров"
