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
            assert re.match(r"\w+", generated_value[0])

        def test_boolean(self, generator, config):
            """Проверяет генерацию булевых значений."""
            xsd_schema = XMLSchema(f"data/simple/types_built_in/boolean.xsd")
            generated_xml = generator.generate_xml(xsd_schema, config)
            log_xml(generated_xml)
            generated_value = generated_xml.xpath("/root/text()")
            assert generated_value
            assert re.match(r"true|false", generated_value[0])

        def test_decimal(self, generator, config):
            xsd_schema = XMLSchema(f"data/simple/types_built_in/decimal.xsd")
            generated_xml = generator.generate_xml(xsd_schema, config)
            log_xml(generated_xml)
            generated_value = generated_xml.xpath("/root/text()")
            assert generated_value
            assert re.match(r"[0-9-.]+", generated_value[0])

        def test_float(self, generator, config):
            xsd_schema = XMLSchema(f"data/simple/types_built_in/float.xsd")
            generated_xml = generator.generate_xml(xsd_schema, config)
            log_xml(generated_xml)
            generated_value = generated_xml.xpath("/root/text()")
            assert generated_value
            assert re.match(r"[0-9-.]+", generated_value[0])

        def test_double(self, generator, config):
            xsd_schema = XMLSchema(f"data/simple/types_built_in/double.xsd")
            generated_xml = generator.generate_xml(xsd_schema, config)
            log_xml(generated_xml)
            generated_value = generated_xml.xpath("/root/text()")
            assert generated_value
            assert re.match(r"[0-9-.]+", generated_value[0])

        def test_datetime(self, generator, config):
            xsd_schema = XMLSchema(f"data/simple/types_built_in/datetime.xsd")
            generated_xml = generator.generate_xml(xsd_schema, config)
            log_xml(generated_xml)
            generated_value = generated_xml.xpath("/root/text()")
            assert generated_value
            assert re.match(r"[1,2][9,0]\d\d-\d\d-\d\dT\d\d:\d\d:\d\d$", generated_value[0])

        def test_date(self, generator, config):
            xsd_schema = XMLSchema(f"data/simple/types_built_in/date.xsd")
            generated_xml = generator.generate_xml(xsd_schema, config)
            log_xml(generated_xml)
            generated_value = generated_xml.xpath("/root/text()")
            assert generated_value
            assert re.match(r"[1,2][9,0]\d\d-\d\d-\d\d$", generated_value[0])

        def test_time(self, generator, config):
            xsd_schema = XMLSchema(f"data/simple/types_built_in/time.xsd")
            generated_xml = generator.generate_xml(xsd_schema, config)
            log_xml(generated_xml)
            generated_value = generated_xml.xpath("/root/text()")
            assert generated_value
            assert re.match(r"^\d\d:\d\d:\d\d$", generated_value[0])

        def test_gyearmonth(self, generator, config):
            xsd_schema = XMLSchema(f"data/simple/types_built_in/gyearmonth.xsd")
            generated_xml = generator.generate_xml(xsd_schema, config)
            log_xml(generated_xml)
            generated_value = generated_xml.xpath("/root/text()")
            assert generated_value
            assert re.match(r"^\d\d\d\d-\d\d$", generated_value[0])

        def test_gyear(self, generator, config):
            xsd_schema = XMLSchema(f"data/simple/types_built_in/gyear.xsd")
            generated_xml = generator.generate_xml(xsd_schema, config)
            log_xml(generated_xml)
            generated_value = generated_xml.xpath("/root/text()")
            assert generated_value
            assert re.match(r"^\d\d\d\d$", generated_value[0])

        def test_gmonthday(self, generator, config):
            xsd_schema = XMLSchema(f"data/simple/types_built_in/gmonthday.xsd")
            generated_xml = generator.generate_xml(xsd_schema, config)
            log_xml(generated_xml)
            generated_value = generated_xml.xpath("/root/text()")
            assert generated_value
            assert re.match(r"^--\d\d-\d\d$", generated_value[0])

        def test_gday(self, generator, config):
            xsd_schema = XMLSchema(f"data/simple/types_built_in/gday.xsd")
            generated_xml = generator.generate_xml(xsd_schema, config)
            log_xml(generated_xml)
            generated_value = generated_xml.xpath("/root/text()")
            assert generated_value
            assert re.match(r"^---\d\d$", generated_value[0])

        def test_gmonth(self, generator, config):
            xsd_schema = XMLSchema(f"data/simple/types_built_in/gmonth.xsd")
            generated_xml = generator.generate_xml(xsd_schema, config)
            log_xml(generated_xml)
            generated_value = generated_xml.xpath("/root/text()")
            assert generated_value
            assert re.match(r"^--\d\d--$", generated_value[0])

        @pytest.mark.skip(reason="not yet implemented")
        @pytest.mark.parametrize("xsd", [
            'duration.xsd',
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
                assert re.match(r"\w+", generated_value[0])

            def test_boolean(self, generator, config):
                xsd_schema = XMLSchema("data/complex/attributes/types_built_in/boolean.xsd")
                generated_xml = generator.generate_xml(xsd_schema, config)
                log_xml(generated_xml)
                generated_value = generated_xml.xpath("/root/@attributeValue")
                assert generated_value
                assert re.match(r"true|false", generated_value[0])

            def test_decimal(self, generator, config):
                xsd_schema = XMLSchema("data/complex/attributes/types_built_in/decimal.xsd")
                generated_xml = generator.generate_xml(xsd_schema, config)
                log_xml(generated_xml)
                generated_value = generated_xml.xpath("/root/@attributeValue")
                assert generated_value
                assert re.match(r"[0-9-.]+", generated_value[0])

            def test_float(self, generator, config):
                xsd_schema = XMLSchema("data/complex/attributes/types_built_in/float.xsd")
                generated_xml = generator.generate_xml(xsd_schema, config)
                log_xml(generated_xml)
                generated_value = generated_xml.xpath("/root/@attributeValue")
                assert generated_value
                assert re.match(r"[0-9-.]+", generated_value[0])

            def test_double(self, generator, config):
                xsd_schema = XMLSchema("data/complex/attributes/types_built_in/double.xsd")
                generated_xml = generator.generate_xml(xsd_schema, config)
                log_xml(generated_xml)
                generated_value = generated_xml.xpath("/root/@attributeValue")
                assert generated_value
                assert re.match(r"[0-9-.]+", generated_value[0])

            def test_datetime(self, generator, config):
                xsd_schema = XMLSchema(f"data/complex/attributes/types_built_in/datetime.xsd")
                generated_xml = generator.generate_xml(xsd_schema, config)
                log_xml(generated_xml)
                generated_value = generated_xml.xpath("/root/@attributeValue")
                assert generated_value
                assert re.match(r"[1,2][9,0]\d\d-\d\d-\d\dT\d\d:\d\d:\d\d$", generated_value[0])

            def test_date(self, generator, config):
                xsd_schema = XMLSchema(f"data/complex/attributes/types_built_in/date.xsd")
                generated_xml = generator.generate_xml(xsd_schema, config)
                log_xml(generated_xml)
                generated_value = generated_xml.xpath("/root/@attributeValue")
                assert generated_value
                assert re.match(r"[1,2][9,0]\d\d-\d\d-\d\d$", generated_value[0])

            def test_time(self, generator, config):
                xsd_schema = XMLSchema(f"data/complex/attributes/types_built_in/time.xsd")
                generated_xml = generator.generate_xml(xsd_schema, config)
                log_xml(generated_xml)
                generated_value = generated_xml.xpath("/root/@attributeValue")
                assert generated_value
                assert re.match(r"^\d\d:\d\d:\d\d$", generated_value[0])

            def test_gyearmonth(self, generator, config):
                xsd_schema = XMLSchema(f"data/complex/attributes/types_built_in/gyearmonth.xsd")
                generated_xml = generator.generate_xml(xsd_schema, config)
                log_xml(generated_xml)
                generated_value = generated_xml.xpath("/root/@attributeValue")
                assert generated_value
                assert re.match(r"^\d\d\d\d-\d\d$", generated_value[0])

            def test_gyear(self, generator, config):
                xsd_schema = XMLSchema(f"data/complex/attributes/types_built_in/gyear.xsd")
                generated_xml = generator.generate_xml(xsd_schema, config)
                log_xml(generated_xml)
                generated_value = generated_xml.xpath("/root/@attributeValue")
                assert generated_value
                assert re.match(r"^\d\d\d\d$", generated_value[0])

            def test_gmonthday(self, generator, config):
                xsd_schema = XMLSchema(f"data/complex/attributes/types_built_in/gmonthday.xsd")
                generated_xml = generator.generate_xml(xsd_schema, config)
                log_xml(generated_xml)
                generated_value = generated_xml.xpath("/root/@attributeValue")
                assert generated_value
                assert re.match(r"^--\d\d-\d\d$", generated_value[0])

            def test_gday(self, generator, config):
                xsd_schema = XMLSchema(f"data/complex/attributes/types_built_in/gday.xsd")
                generated_xml = generator.generate_xml(xsd_schema, config)
                log_xml(generated_xml)
                generated_value = generated_xml.xpath("/root/@attributeValue")
                assert generated_value
                assert re.match(r"^---\d\d$", generated_value[0])

            def test_gmonth(self, generator, config):
                xsd_schema = XMLSchema(f"data/complex/attributes/types_built_in/gmonth.xsd")
                generated_xml = generator.generate_xml(xsd_schema, config)
                log_xml(generated_xml)
                generated_value = generated_xml.xpath("/root/@attributeValue")
                assert generated_value
                assert re.match(r"^--\d\d--$", generated_value[0])

            @pytest.mark.skip(reason="not yet implemented")
            @pytest.mark.parametrize("xsd", [
                'duration.xsd',
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

            def test_string_length_min_max(self, generator, config):
                xsd_schema = XMLSchema("data/complex/attributes/types_built_in_restricted/string_length_min_max.xsd")
                generated_xml = generator.generate_xml(xsd_schema, config)
                log_xml(generated_xml)
                generated_value = generated_xml.xpath("/root/@attributeValue")
                assert len(generated_value[0]) in range(10, 21)

            def test_string_enumeration(self, generator, config):
                xsd_schema = XMLSchema("data/complex/attributes/types_built_in_restricted/string_enumeration.xsd")
                generated_xml = generator.generate_xml(xsd_schema, config)
                log_xml(generated_xml)
                generated_value = generated_xml.xpath("/root/@attributeValue")
                valid_values = ['red', 'green', 'blue']
                assert generated_value[0] in valid_values

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

            def test_float_inclusive(self, generator, config):
                xsd_schema = XMLSchema("data/complex/attributes/types_built_in_restricted/float_inclusive.xsd")
                generated_xml = generator.generate_xml(xsd_schema, config)
                log_xml(generated_xml)
                generated_value = generated_xml.xpath("/root/@attributeValue")
                assert 0.0 <= float(generated_value[0]) <= 100.0

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

            def test_double_inclusive(self, generator, config):
                xsd_schema = XMLSchema("data/complex/attributes/types_built_in_restricted/double_inclusive.xsd")
                generated_xml = generator.generate_xml(xsd_schema, config)
                log_xml(generated_xml)
                generated_value = generated_xml.xpath("/root/@attributeValue")
                assert 0.0 <= float(generated_value[0]) <= 100.0

            def test_double_exclusive(self, generator, config):
                xsd_schema = XMLSchema("data/complex/attributes/types_built_in_restricted/double_exclusive.xsd")
                generated_xml = generator.generate_xml(xsd_schema, config)
                log_xml(generated_xml)
                generated_value = generated_xml.xpath("/root/@attributeValue")
                assert -1.0 < float(generated_value[0]) < 101.0

            @pytest.mark.skip(reason="not yet implemented")
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
            counts_by_occurs_a = {}
            counts_by_occurs_b = {}
            counts_by_occurs_c = {}

            for _ in range(100):
                generated_xml = generator.generate_xml(xsd_schema, config)
                count_a = int(generated_xml.xpath("count(/root/FirstName)"))
                count_b = int(generated_xml.xpath("count(/root/LastName)"))
                count_c = int(generated_xml.xpath("count(/root/MiddleName)"))
                counts_by_occurs_a[count_a] = (counts_by_occurs_a.get(count_a) or 0) + 1
                counts_by_occurs_b[count_b] = (counts_by_occurs_b.get(count_b) or 0) + 1
                counts_by_occurs_c[count_c] = (counts_by_occurs_c.get(count_c) or 0) + 1

            assert counts_by_occurs_b[0] == counts_by_occurs_c[0]
            assert counts_by_occurs_b[1] == counts_by_occurs_c[1]
            assert counts_by_occurs_a[0] > counts_by_occurs_b[0]
            assert counts_by_occurs_a[0] + counts_by_occurs_a[1] == 100
            assert counts_by_occurs_b[0] + counts_by_occurs_b[1] == 100
            assert counts_by_occurs_c[0] + counts_by_occurs_c[1] == 100

        def test_occurs_required(self, generator, config):
            xsd_schema = XMLSchema("data/complex/all/occurs_required.xsd")
            counts_by_occurs_a = {}
            counts_by_occurs_b = {}
            counts_by_occurs_c = {}

            for _ in range(100):
                generated_xml = generator.generate_xml(xsd_schema, config)
                count_a = int(generated_xml.xpath("count(/root/FirstName)"))
                count_b = int(generated_xml.xpath("count(/root/LastName)"))
                count_c = int(generated_xml.xpath("count(/root/MiddleName)"))
                counts_by_occurs_a[count_a] = (counts_by_occurs_a.get(count_a) or 0) + 1
                counts_by_occurs_b[count_b] = (counts_by_occurs_b.get(count_b) or 0) + 1
                counts_by_occurs_c[count_c] = (counts_by_occurs_c.get(count_c) or 0) + 1

            assert min(counts_by_occurs_a) == 0
            assert max(counts_by_occurs_a) == 1
            assert counts_by_occurs_a[0] + counts_by_occurs_a[1] == 100

            assert min(counts_by_occurs_b) == 1
            assert counts_by_occurs_b[1] == 100

            assert min(counts_by_occurs_c) == 1
            assert counts_by_occurs_c[1] == 100

    class TestChoice:

        def test_group_0_1__elements_required(self, generator, config):
            xsd_schema = XMLSchema("data/complex/choice/scenario_01_choice_0_1_elements_required.xsd")
            counts_by_occurs_a = {}
            counts_by_occurs_b = {}
            for _ in range(100):
                generated_xml = generator.generate_xml(xsd_schema, config)
                count_a = int(generated_xml.xpath("count(/root/optionA)"))
                count_b = int(generated_xml.xpath("count(/root/optionB)"))
                counts_by_occurs_a[count_a] = (counts_by_occurs_a.get(count_a) or 0) + 1
                counts_by_occurs_b[count_b] = (counts_by_occurs_b.get(count_b) or 0) + 1

            assert min(counts_by_occurs_a) == 0
            assert max(counts_by_occurs_a) == 1
            assert len(counts_by_occurs_a) == 2
            assert counts_by_occurs_a[0] >= 10
            assert counts_by_occurs_a[1] >= 10
            assert counts_by_occurs_a[0] + counts_by_occurs_a[1] == 100

            assert min(counts_by_occurs_b) == 0
            assert max(counts_by_occurs_b) == 1
            assert len(counts_by_occurs_b) == 2
            assert counts_by_occurs_b[0] >= 10
            assert counts_by_occurs_b[1] >= 10
            assert counts_by_occurs_b[0] + counts_by_occurs_b[1] == 100

        def test_group_1_unbounded__element_0_1(self, generator, config):
            xsd_schema = XMLSchema("data/complex/choice/scenario_02_choice_1_unbounded.xsd")
            counts_by_occurs_info = {}
            counts_by_occurs_warn = {}
            counts_by_occurs_err = {}
            for _ in range(100):
                generated_xml = generator.generate_xml(xsd_schema, config)
                count_info = int(generated_xml.xpath("count(/root/info)"))
                count_warn = int(generated_xml.xpath("count(/root/warning)"))
                count_err = int(generated_xml.xpath("count(/root/error)"))
                counts_by_occurs_info[count_info] = (counts_by_occurs_info.get(count_info) or 0) + 1
                counts_by_occurs_warn[count_warn] = (counts_by_occurs_warn.get(count_warn) or 0) + 1
                counts_by_occurs_err[count_err] = (counts_by_occurs_err.get(count_err) or 0) + 1

            assert min(counts_by_occurs_info) == 0
            assert max(counts_by_occurs_info) > 1
            assert sum(counts_by_occurs_info.values()) == 100

            assert min(counts_by_occurs_warn) == 0
            assert max(counts_by_occurs_warn) > 1
            assert sum(counts_by_occurs_warn.values()) == 100

            assert min(counts_by_occurs_err) == 0
            assert max(counts_by_occurs_err) > 1
            assert sum(counts_by_occurs_err.values()) == 100

        def test_group_3_3__min_conflict(self, generator, config):
            xsd_schema = XMLSchema("data/complex/choice/scenario_03_choice_3_3_min_conflict.xsd")
            counts_by_occurs_1 = {}
            counts_by_occurs_2 = {}
            counts_by_occurs_3 = {}
            for _ in range(100):
                generated_xml = generator.generate_xml(xsd_schema, config)
                count_1 = int(generated_xml.xpath("count(/root/partA)"))
                count_2 = int(generated_xml.xpath("count(/root/partB)"))
                count_3 = int(generated_xml.xpath("count(/root/partC)"))
                counts_by_occurs_1[count_1] = (counts_by_occurs_1.get(count_1) or 0) + 1
                counts_by_occurs_2[count_2] = (counts_by_occurs_2.get(count_2) or 0) + 1
                counts_by_occurs_3[count_3] = (counts_by_occurs_3.get(count_3) or 0) + 1

            assert min(counts_by_occurs_1) == 0
            assert max(counts_by_occurs_1) > 1
            assert sum(counts_by_occurs_1.values()) == 100

            assert min(counts_by_occurs_2) == 0
            assert max(counts_by_occurs_2) > 1
            assert sum(counts_by_occurs_2.values()) == 100

            assert min(counts_by_occurs_3) == 0
            assert max(counts_by_occurs_3) > 1
            assert sum(counts_by_occurs_3.values()) == 100

        def test_group_1_2__element_forbidden(self, generator, config):
            xsd_schema = XMLSchema("data/complex/choice/scenario_04_choice_1_2_element_forbidden.xsd")
            counts_by_occurs_1 = {}
            counts_by_occurs_2 = {}
            counts_by_occurs_3 = {}
            for _ in range(100):
                generated_xml = generator.generate_xml(xsd_schema, config)
                count_1 = int(generated_xml.xpath("count(/root/allowed)"))
                count_2 = int(generated_xml.xpath("count(/root/forbidden)"))
                count_3 = int(generated_xml.xpath("count(/root/alsoAllowed)"))
                counts_by_occurs_1[count_1] = (counts_by_occurs_1.get(count_1) or 0) + 1
                counts_by_occurs_2[count_2] = (counts_by_occurs_2.get(count_2) or 0) + 1
                counts_by_occurs_3[count_3] = (counts_by_occurs_3.get(count_3) or 0) + 1

            assert min(counts_by_occurs_1) == 0
            assert max(counts_by_occurs_1) > 1
            assert sum(counts_by_occurs_1.values()) == 100

            assert min(counts_by_occurs_2) == 0
            assert max(counts_by_occurs_2) == 0
            assert sum(counts_by_occurs_2.values()) == 100

            assert min(counts_by_occurs_3) == 0
            assert max(counts_by_occurs_3) > 1
            assert sum(counts_by_occurs_3.values()) == 100

        def test_group_1_5__element_optional(self, generator, config):
            xsd_schema = XMLSchema("data/complex/choice/scenario_05_choice_1_5_elements_optional.xsd")
            counts_by_occurs_1 = {}
            counts_by_occurs_2 = {}
            counts_by_occurs_3 = {}
            for _ in range(100):
                generated_xml = generator.generate_xml(xsd_schema, config)
                count_1 = int(generated_xml.xpath("count(/root/opt1)"))
                count_2 = int(generated_xml.xpath("count(/root/opt2)"))
                count_3 = int(generated_xml.xpath("count(/root/opt3)"))
                counts_by_occurs_1[count_1] = (counts_by_occurs_1.get(count_1) or 0) + 1
                counts_by_occurs_2[count_2] = (counts_by_occurs_2.get(count_2) or 0) + 1
                counts_by_occurs_3[count_3] = (counts_by_occurs_3.get(count_3) or 0) + 1

            assert min(counts_by_occurs_1) == 0
            assert max(counts_by_occurs_1) > 1
            assert sum(counts_by_occurs_1.values()) == 100

            assert min(counts_by_occurs_2) == 0
            assert max(counts_by_occurs_2) > 1
            assert sum(counts_by_occurs_2.values()) == 100

            assert min(counts_by_occurs_3) == 0
            assert max(counts_by_occurs_3) > 1
            assert sum(counts_by_occurs_3.values()) == 100

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
            assert len(counts_by_occurs_item_opt) <= 10

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
