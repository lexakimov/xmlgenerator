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


@pytest.fixture
def randomizer():
    """Фикстура для создания генератора случайных значений."""
    return Randomizer()


@pytest.fixture
def substitutor(randomizer):
    """Фикстура для создания подстановщика значений."""
    return Substitutor(randomizer)


@pytest.fixture
def generator(randomizer, substitutor):
    """Фикстура для создания генератора XML."""
    return XmlGenerator(randomizer, substitutor)


@pytest.fixture
def config():
    """Фикстура для создания конфигурации генератора."""
    return GeneratorConfig()


def log_xml(generated_xml):
    """Выводит сгенерированный XML в консоль для отладки."""
    print(etree.tostring(generated_xml, pretty_print=True).decode('utf-8'))


def value(schema_path, xpath, generator, config) -> list[str]:
    """
    Генерирует XML по схеме и извлекает значение по XPath.
    
    Args:
        schema_path: Путь к XSD схеме
        xpath: XPath выражение для извлечения значения
        generator: Генератор XML
        config: Конфигурация генератора
        
    Returns:
        Список найденных значений
    """
    xsd_schema = XMLSchema(schema_path)
    generated_xml = generator.generate_xml(xsd_schema, config)
    log_xml(generated_xml)
    return generated_xml.xpath(xpath)


class TestSimple:
    """Тесты для простых типов данных в XML."""

    class TestBuiltInTypes:
        """Тесты для встроенных типов данных."""

        def test_string(self, generator, config):
            """Проверяет генерацию строковых значений."""
            xsd_schema = XMLSchema(f"data/simple/types_built_in/string.xsd")
            generated_xml = generator.generate_xml(xsd_schema, config)
            log_xml(generated_xml)
            generated_value = generated_xml.xpath("/root/text()")
            assert generated_value
            assert re.match("\w+", generated_value[0])

        def test_boolean(self, generator, config):
            """Проверяет генерацию булевых значений."""
            xsd_schema = XMLSchema(f"data/simple/types_built_in/boolean.xsd")
            generated_xml = generator.generate_xml(xsd_schema, config)
            log_xml(generated_xml)
            generated_value = generated_xml.xpath("/root/text()")
            assert generated_value
            assert re.match("true|false", generated_value[0])

        def test_decimal(self, generator, config):
            xsd_schema = XMLSchema(f"data/simple/types_built_in/decimal.xsd")
            generated_xml = generator.generate_xml(xsd_schema, config)
            log_xml(generated_xml)
            generated_value = generated_xml.xpath("/root/text()")
            assert generated_value
            assert re.match("[0-9-.]+", generated_value[0])

        def test_float(self, generator, config):
            xsd_schema = XMLSchema(f"data/simple/types_built_in/float.xsd")
            generated_xml = generator.generate_xml(xsd_schema, config)
            log_xml(generated_xml)
            generated_value = generated_xml.xpath("/root/text()")
            assert generated_value
            assert re.match("[0-9-.]+", generated_value[0])

        def test_double(self, generator, config):
            xsd_schema = XMLSchema(f"data/simple/types_built_in/double.xsd")
            generated_xml = generator.generate_xml(xsd_schema, config)
            log_xml(generated_xml)
            generated_value = generated_xml.xpath("/root/text()")
            assert generated_value
            assert re.match("[0-9-.]+", generated_value[0])

        @pytest.mark.skip(reason="unimplemented")
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
        def test_built_in_types_in_tags(self, generator, config, xsd):
            xsd_schema = XMLSchema(f"data/simple/types_built_in/{xsd}")
            generated_xml = generator.generate_xml(xsd_schema, config)
            log_xml(generated_xml)
            generated_value = generated_xml.xpath("/root/text()")
            assert generated_value


class TestComplex:
    class TestAttributes:

        class TestBuiltInTypes:

            def test_string(self, generator, config):
                xsd_schema = XMLSchema("data/complex/attributes/types_built_in/string.xsd")
                generated_xml = generator.generate_xml(xsd_schema, config)
                log_xml(generated_xml)
                generated_value = generated_xml.xpath("/root/@attributeValue")
                assert generated_value
                assert re.match("\w+", generated_value[0])

            def test_boolean(self, generator, config):
                xsd_schema = XMLSchema("data/complex/attributes/types_built_in/boolean.xsd")
                generated_xml = generator.generate_xml(xsd_schema, config)
                log_xml(generated_xml)
                generated_value = generated_xml.xpath("/root/@attributeValue")
                assert generated_value
                assert re.match("true|false", generated_value[0])

            def test_decimal(self, generator, config):
                xsd_schema = XMLSchema("data/complex/attributes/types_built_in/decimal.xsd")
                generated_xml = generator.generate_xml(xsd_schema, config)
                log_xml(generated_xml)
                generated_value = generated_xml.xpath("/root/@attributeValue")
                assert generated_value
                assert re.match("[0-9-.]+", generated_value[0])

            def test_float(self, generator, config):
                xsd_schema = XMLSchema("data/complex/attributes/types_built_in/float.xsd")
                generated_xml = generator.generate_xml(xsd_schema, config)
                log_xml(generated_xml)
                generated_value = generated_xml.xpath("/root/@attributeValue")
                assert generated_value
                assert re.match("[0-9-.]+", generated_value[0])

            def test_double(self, generator, config):
                xsd_schema = XMLSchema("data/complex/attributes/types_built_in/double.xsd")
                generated_xml = generator.generate_xml(xsd_schema, config)
                log_xml(generated_xml)
                generated_value = generated_xml.xpath("/root/@attributeValue")
                assert generated_value
                assert re.match("[0-9-.]+", generated_value[0])

            @pytest.mark.skip(reason="unimplemented")
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
            def test_built_in_types_in_attributes(self, generator, config, xsd):
                xsd_schema = XMLSchema(f"data/complex/attributes/types_built_in/{xsd}.xsd")
                generated_xml = generator.generate_xml(xsd_schema, config)
                log_xml(generated_xml)
                generated_value = generated_xml.xpath("/root/@attributeValue")
                assert generated_value

        class TestBuiltInRestrictedTypes:

            def test_string_length(self, generator, config):
                xsd_schema = XMLSchema("data/complex/attributes/types_built_in_restricted/string_length.xsd")
                generated_xml = generator.generate_xml(xsd_schema, config)
                log_xml(generated_xml)
                generated_value = generated_xml.xpath("/root/@attributeValue")
                assert len(generated_value[0]) == 10

            @pytest.mark.flaky(reruns=10)
            def test_string_length_min_max(self, generator, config):
                xsd_schema = XMLSchema("data/complex/attributes/types_built_in_restricted/string_length_min_max.xsd")
                generated_xml = generator.generate_xml(xsd_schema, config)
                log_xml(generated_xml)
                generated_value = generated_xml.xpath("/root/@attributeValue")
                assert len(generated_value[0]) in range(10, 21)

            @pytest.mark.flaky(reruns=10)
            def test_string_enumeration(self, generator, config):
                xsd_schema = XMLSchema("data/complex/attributes/types_built_in_restricted/string_enumeration.xsd")
                generated_xml = generator.generate_xml(xsd_schema, config)
                log_xml(generated_xml)
                generated_value = generated_xml.xpath("/root/@attributeValue")
                valid_values = ['red', 'green', 'blue']
                assert generated_value[0] in valid_values

            @pytest.mark.flaky(reruns=10)
            def test_string_pattern(self, generator, config):
                xsd_schema = XMLSchema("data/complex/attributes/types_built_in_restricted/string_pattern.xsd")
                generated_xml = generator.generate_xml(xsd_schema, config)
                log_xml(generated_xml)
                generated_value = generated_xml.xpath("/root/@attributeValue")
                assert re.match(r'[A-Z]{2}\d{3}', generated_value[0])

            def test_string_white_space(self, generator, config):
                xsd_schema = XMLSchema("data/complex/attributes/types_built_in_restricted/string_whitespace.xsd")
                generated_xml = generator.generate_xml(xsd_schema, config)
                log_xml(generated_xml)
                generated_value = generated_xml.xpath("/root/@attributeValue")
                assert ' ' not in generated_value[0]

            def test_decimal_total_digits(self, generator, config):
                xsd_schema = XMLSchema("data/complex/attributes/types_built_in_restricted/decimal_total_digits.xsd")
                generated_xml = generator.generate_xml(xsd_schema, config)
                log_xml(generated_xml)
                generated_value = generated_xml.xpath("/root/@attributeValue")
                assert len(generated_value[0]) == 5

            def test_decimal_fraction_digits(self, generator, config):
                xsd_schema = XMLSchema("data/complex/attributes/types_built_in_restricted/decimal_fraction_digits.xsd")
                generated_xml = generator.generate_xml(xsd_schema, config)
                log_xml(generated_xml)
                generated_value = generated_xml.xpath("/root/@attributeValue")
                decimal_part = generated_value[0].split('.')[1]
                assert len(decimal_part) <= 2

            def test_float_pattern(self, generator, config):
                xsd_schema = XMLSchema("data/complex/attributes/types_built_in_restricted/float_pattern.xsd")
                generated_xml = generator.generate_xml(xsd_schema, config)
                log_xml(generated_xml)
                generated_value = generated_xml.xpath("/root/@attributeValue")
                assert re.match(r'[-+]?[0-9]*\.?[0-9]+([eE][-+]?[0-9]+)?', generated_value[0])

            @pytest.mark.flaky(reruns=10)
            def test_float_enumeration(self, generator, config):
                xsd_schema = XMLSchema("data/complex/attributes/types_built_in_restricted/float_enumeration.xsd")
                generated_xml = generator.generate_xml(xsd_schema, config)
                log_xml(generated_xml)
                generated_value = generated_xml.xpath("/root/@attributeValue")
                valid_values = ['1.5', '2.5', '3.5']
                assert generated_value[0] in valid_values

            def test_float_whitespace(self, generator, config):
                xsd_schema = XMLSchema("data/complex/attributes/types_built_in_restricted/float_whitespace.xsd")
                generated_xml = generator.generate_xml(xsd_schema, config)
                log_xml(generated_xml)
                generated_value = generated_xml.xpath("/root/@attributeValue")
                assert ' ' not in generated_value[0]

            @pytest.mark.flaky(reruns=10)
            def test_float_inclusive(self, generator, config):
                xsd_schema = XMLSchema("data/complex/attributes/types_built_in_restricted/float_inclusive.xsd")
                generated_xml = generator.generate_xml(xsd_schema, config)
                log_xml(generated_xml)
                generated_value = generated_xml.xpath("/root/@attributeValue")
                assert 0.0 <= float(generated_value[0]) <= 100.0

            @pytest.mark.flaky(reruns=10)
            def test_float_exclusive(self, generator, config):
                xsd_schema = XMLSchema("data/complex/attributes/types_built_in_restricted/float_exclusive.xsd")
                generated_xml = generator.generate_xml(xsd_schema, config)
                log_xml(generated_xml)
                generated_value = generated_xml.xpath("/root/@attributeValue")
                assert -1.0 < float(generated_value[0]) < 101.0

            def test_double_pattern(self, generator, config):
                xsd_schema = XMLSchema("data/complex/attributes/types_built_in_restricted/double_pattern.xsd")
                generated_xml = generator.generate_xml(xsd_schema, config)
                log_xml(generated_xml)
                generated_value = generated_xml.xpath("/root/@attributeValue")
                assert re.match(r'[-+]?[0-9]*\.?[0-9]+([eE][-+]?[0-9]+)?', generated_value[0])

            @pytest.mark.flaky(reruns=10)
            def test_double_enumeration(self, generator, config):
                xsd_schema = XMLSchema("data/complex/attributes/types_built_in_restricted/double_enumeration.xsd")
                generated_xml = generator.generate_xml(xsd_schema, config)
                log_xml(generated_xml)
                generated_value = generated_xml.xpath("/root/@attributeValue")
                valid_values = ['1.5', '2.5', '3.5']
                assert generated_value[0] in valid_values

            def test_double_whitespace(self, generator, config):
                xsd_schema = XMLSchema("data/complex/attributes/types_built_in_restricted/double_whitespace.xsd")
                generated_xml = generator.generate_xml(xsd_schema, config)
                log_xml(generated_xml)
                generated_value = generated_xml.xpath("/root/@attributeValue")
                assert ' ' not in generated_value[0]

            @pytest.mark.flaky(reruns=10)
            def test_double_inclusive(self, generator, config):
                xsd_schema = XMLSchema("data/complex/attributes/types_built_in_restricted/double_inclusive.xsd")
                generated_xml = generator.generate_xml(xsd_schema, config)
                log_xml(generated_xml)
                generated_value = generated_xml.xpath("/root/@attributeValue")
                assert 0.0 <= float(generated_value[0]) <= 100.0

            @pytest.mark.flaky(reruns=10)
            def test_double_exclusive(self, generator, config):
                xsd_schema = XMLSchema("data/complex/attributes/types_built_in_restricted/double_exclusive.xsd")
                generated_xml = generator.generate_xml(xsd_schema, config)
                log_xml(generated_xml)
                generated_value = generated_xml.xpath("/root/@attributeValue")
                assert -1.0 < float(generated_value[0]) < 101.0

            def test_date_min_max(self, generator, config):
                xsd_schema = XMLSchema("data/complex/attributes/types_built_in_restricted/date_inclusive_min_max.xsd")
                generated_xml = generator.generate_xml(xsd_schema, config)
                log_xml(generated_xml)
                generated_value = generated_xml.xpath("/root/@attributeValue")
                date_value = datetime.strptime(generated_value[0], '%Y-%m-%d')
                assert datetime(2020, 1, 1) <= date_value <= datetime(2025, 12, 31)

        class TestDerivedRestrictedTypes:

            def test_integer_inclusive_min_max(self, generator, config):
                xsd_schema = XMLSchema("data/complex/attributes/types_derived_restricted/integer_inclusive_min_max.xsd")
                generated_xml = generator.generate_xml(xsd_schema, config)
                log_xml(generated_xml)
                generated_value = generated_xml.xpath("/root/@attributeValue")
                assert 10 <= int(generated_value[0]) <= 100

    class TestAll:

        def test_occurs_optional(self, generator, config):
            xsd_schema = XMLSchema("data/complex/all/occurs_optional.xsd")
            counts = {
                "FirstName": [],
                "LastName": [],
            }
            for _ in range(100):
                generated_xml = generator.generate_xml(xsd_schema, config)
                counts['FirstName'].append(len(generated_xml.xpath("/root/FirstName/text()")))
                counts['LastName'].append(len(generated_xml.xpath("/root/LastName/text()")))

            first_name_unique_counts = set(counts['FirstName'])
            last_name_unique_counts = set(counts['LastName'])

            assert len(first_name_unique_counts) == 2, "Опциональный элемент всегда генерируется одинаково"
            assert len(last_name_unique_counts) == 2, "Опциональный элемент всегда генерируется одинаково"
            for i in range(100):
                if counts['LastName'][i] == 0:
                    assert counts['FirstName'][i] == 0

        def test_occurs_required(self, generator, config):
            xsd_schema = XMLSchema("data/complex/all/occurs_required.xsd")
            counts = {
                "FirstName": [],
                "LastName": [],
            }
            for _ in range(100):
                generated_xml = generator.generate_xml(xsd_schema, config)
                counts['FirstName'].append(len(generated_xml.xpath("/root/FirstName/text()")))
                counts['LastName'].append(len(generated_xml.xpath("/root/LastName/text()")))

            first_name_unique_counts = set(counts['FirstName'])
            last_name_unique_counts = set(counts['LastName'])

            assert len(first_name_unique_counts) == 2, "Опциональный элемент всегда генерируется одинаково"
            assert len(last_name_unique_counts) == 1, "Опциональный элемент всегда генерируется одинаково"

    class TestChoice:

        def test_occurs_0_1_variations(self, generator, config):
            xsd_schema = XMLSchema("data/complex/choice/occurs_0_1.xsd")
            counts = []
            for _ in range(100):
                generated_xml = generator.generate_xml(xsd_schema, config)
                counts.append(len(generated_xml.findall("optional")))
            unique_counts = set(counts)
            assert len(unique_counts) == 2, "Опциональный элемент всегда генерируется одинаково"

        def test_occurs_0_3_variations(self, generator, config):
            xsd_schema = XMLSchema("data/complex/choice/occurs_0_3.xsd")
            counts = []
            for _ in range(100):
                generated_xml = generator.generate_xml(xsd_schema, config)
                counts.append(len(generated_xml.findall("zeroToThree")))
            unique_counts = set(counts)
            assert len(unique_counts) == 4, "Опциональный элемент всегда генерируется одинаково"
            for count in unique_counts:
                assert 0 <= count <= 3

        def test_occurs_1_1(self, generator, config):
            xsd_schema = XMLSchema("data/complex/choice/occurs_1_1.xsd")
            counts = []
            for _ in range(100):
                generated_xml = generator.generate_xml(xsd_schema, config)
                counts.append(len(generated_xml.findall("required")))
            unique_counts = set(counts)
            assert len(unique_counts) == 1
            assert list(unique_counts)[0] == 1

        def test_occurs_2_5(self, generator, config):
            xsd_schema = XMLSchema("data/complex/choice/occurs_2_5.xsd")
            counts = []
            for _ in range(100):
                generated_xml = generator.generate_xml(xsd_schema, config)
                counts.append(len(generated_xml.findall("twoToFive")))
            unique_counts = set(counts)
            assert len(unique_counts) == 4
            for count in unique_counts:
                assert 2 <= count <= 5

        def test_occurs_unbounded_at_least_one_element(self, generator, config):
            xsd_schema = XMLSchema("data/complex/choice/occurs_unbounded.xsd")
            counts = []
            for _ in range(100):
                generated_xml = generator.generate_xml(xsd_schema, config)
                counts.append(len(generated_xml.findall("atLeastOne")))

            s = set(counts)
            assert 0 not in s
            assert 5 < len(s) <= 11, \
                f"Элемент atLeastOne всегда генерируется с одинаковым количеством экземпляров"

        def test_occurs_unbounded_zero_or_more_elements(self, generator, config):
            xsd_schema = XMLSchema("data/complex/choice/occurs_unbounded.xsd")
            counts = []
            for _ in range(100):
                generated_xml = generator.generate_xml(xsd_schema, config)
                counts.append(len(generated_xml.findall("zeroOrMore")))

            assert 5 < len(set(counts)) <= 10, \
                f"Элемент zeroOrMore всегда генерируется с одинаковым количеством экземпляров"

    class TestSequence:

        def test_group_1_1__element_0_1(self, generator, config):
            xsd_schema = XMLSchema("data/complex/sequence/scenario_01_optional_element.xsd")
            counts_by_occurs = {}
            for _ in range(100):
                generated_xml = generator.generate_xml(xsd_schema, config)
                count = int(generated_xml.xpath("count(/root/optionalItem)"))
                counts_by_occurs[count] = (counts_by_occurs.get(count) or 0) + 1

            assert counts_by_occurs[0] >= 10
            assert counts_by_occurs[1] >= 10
            assert len(counts_by_occurs) == 2

        def test_group_1_1__element_2_5(self, generator, config):
            xsd_schema = XMLSchema("data/complex/sequence/scenario_02_required_range_element.xsd")
            counts_by_occurs = {}
            for _ in range(100):
                generated_xml = generator.generate_xml(xsd_schema, config)
                count = int(generated_xml.xpath("count(/root/rangedItem)"))
                counts_by_occurs[count] = (counts_by_occurs.get(count) or 0) + 1

            assert min(counts_by_occurs) == 2
            assert max(counts_by_occurs) == 5
            assert len(counts_by_occurs) == 4

            assert counts_by_occurs[2] >= 10
            assert counts_by_occurs[3] >= 10
            assert counts_by_occurs[4] >= 10
            assert counts_by_occurs[5] >= 10

        def test_group_1_1__element_0_unbounded(self, generator, config):
            xsd_schema = XMLSchema("data/complex/sequence/scenario_03_unbounded_element.xsd")
            counts_by_occurs = {}
            for _ in range(100):
                generated_xml = generator.generate_xml(xsd_schema, config)
                count = int(generated_xml.xpath("count(/root/unboundedItem)"))
                counts_by_occurs[count] = (counts_by_occurs.get(count) or 0) + 1

            assert min(counts_by_occurs) == 0
            assert max(counts_by_occurs) == 10
            assert len(counts_by_occurs) == 11
            assert counts_by_occurs[0] >= 1
            assert counts_by_occurs[10] >= 1

        def test_group_0_1__element_1_1__0_1(self, generator, config):
            xsd_schema = XMLSchema("data/complex/sequence/scenario_04_optional_sequence.xsd")
            counts_by_occurs_item_a = {}  # required
            counts_by_occurs_item_b = {}  # optional
            for _ in range(100):
                generated_xml = generator.generate_xml(xsd_schema, config)
                count_a = int(generated_xml.xpath("count(/root/itemA)"))
                count_b = int(generated_xml.xpath("count(/root/itemB)"))
                counts_by_occurs_item_a[count_a] = (counts_by_occurs_item_a.get(count_a) or 0) + 1
                counts_by_occurs_item_b[count_b] = (counts_by_occurs_item_b.get(count_b) or 0) + 1

            assert counts_by_occurs_item_a[1] < 100, "группа не опциональна"
            assert counts_by_occurs_item_a[1] > counts_by_occurs_item_b[1], "optional больше чем reqiured"

        def test_group_1_2__element_1_1__1_1(self, generator, config):
            xsd_schema = XMLSchema("data/complex/sequence/scenario_05_repeating_sequence_range.xsd")
            counts_by_occurs_item_k = {}  # required
            counts_by_occurs_item_v = {}  # optional
            for _ in range(100):
                generated_xml = generator.generate_xml(xsd_schema, config)
                count_a = int(generated_xml.xpath("count(/root/key)"))
                count_b = int(generated_xml.xpath("count(/root/value)"))
                counts_by_occurs_item_k[count_a] = (counts_by_occurs_item_k.get(count_a) or 0) + 1
                counts_by_occurs_item_v[count_b] = (counts_by_occurs_item_v.get(count_b) or 0) + 1

            assert counts_by_occurs_item_k[1] > 0
            assert counts_by_occurs_item_k[2] > 0
            assert counts_by_occurs_item_k[3] > 0
            assert counts_by_occurs_item_k[1] + counts_by_occurs_item_k[2] + counts_by_occurs_item_k[3] == 100
            assert len(counts_by_occurs_item_k) == 3

            assert counts_by_occurs_item_v[1] > 0
            assert counts_by_occurs_item_v[2] > 0
            assert counts_by_occurs_item_v[3] > 0
            assert counts_by_occurs_item_v[1] + counts_by_occurs_item_v[2] + counts_by_occurs_item_v[3] == 100
            assert len(counts_by_occurs_item_v) == 3

            assert counts_by_occurs_item_k[1] == counts_by_occurs_item_v[1]
            assert counts_by_occurs_item_k[2] == counts_by_occurs_item_v[2]
            assert counts_by_occurs_item_k[3] == counts_by_occurs_item_v[3]

        def test_group_1_unbounded__element_1_1__0_1(self, generator, config):
            xsd_schema = XMLSchema("data/complex/sequence/scenario_06_optional_in_repeating_seq.xsd")
            counts_by_occurs_item_req = {}  # required
            counts_by_occurs_item_opt = {}  # optional
            for _ in range(100):
                generated_xml = generator.generate_xml(xsd_schema, config)
                count_req = int(generated_xml.xpath("count(/root/mandatoryInSeq)"))
                count_opt = int(generated_xml.xpath("count(/root/optionalInSeq)"))
                counts_by_occurs_item_req[count_req] = (counts_by_occurs_item_req.get(count_req) or 0) + 1
                counts_by_occurs_item_opt[count_opt] = (counts_by_occurs_item_opt.get(count_opt) or 0) + 1

            assert min(counts_by_occurs_item_req) == 1
            assert max(counts_by_occurs_item_req) == 10
            assert len(counts_by_occurs_item_req) == 10

            assert min(counts_by_occurs_item_opt) == 0
            assert max(counts_by_occurs_item_opt) <= 10
            assert len(counts_by_occurs_item_opt) < 10

        def test_group_1_1__element_0_0__0_1(self, generator, config):
            xsd_schema = XMLSchema("data/complex/sequence/scenario_07_forbidden_element.xsd")
            counts_by_occurs_item_opt = {}  # required
            counts_by_occurs_item_forb = {}  # optional
            for _ in range(100):
                generated_xml = generator.generate_xml(xsd_schema, config)
                count_opt = int(generated_xml.xpath("count(/root/allowedItem)"))
                count_forb = int(generated_xml.xpath("count(/root/forbiddenItem)"))
                counts_by_occurs_item_opt[count_opt] = (counts_by_occurs_item_opt.get(count_opt) or 0) + 1
                counts_by_occurs_item_forb[count_forb] = (counts_by_occurs_item_forb.get(count_forb) or 0) + 1

            assert min(counts_by_occurs_item_opt) == 0
            assert max(counts_by_occurs_item_opt) == 1
            assert counts_by_occurs_item_opt[0] > 10
            assert counts_by_occurs_item_opt[1] > 10
            assert counts_by_occurs_item_opt[0] + counts_by_occurs_item_opt[1] == 100

            assert min(counts_by_occurs_item_forb) == 0
            assert max(counts_by_occurs_item_forb) == 0
            assert counts_by_occurs_item_forb[0] == 100
