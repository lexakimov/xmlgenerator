import os

import pytest

import tests
from xmlgenerator.configuration import GeneratorConfig
from xmlgenerator.randomization import Randomizer
from xmlgenerator.substitution import (
    ExpressionSyntaxError,
    Substitutor,
    _extract_arguments,
    _parse_subexpressions, )

os.chdir(os.path.dirname(os.path.abspath(tests.__file__)))


class TestExpressionParsing:

    def test_empty_string_returns_empty_list(self):
        assert _parse_subexpressions('') == []

    def test_no_placeholders_returns_empty_list(self):
        assert _parse_subexpressions('plain text without placeholders') == []

    def test_parse_function_without_arguments(self):
        subexpressions = _parse_subexpressions('{{ uuid }}')
        assert len(subexpressions) == 1
        se = subexpressions[0]
        assert se.function == 'uuid'
        assert se.argument is None
        assert se.modifier is None

    def test_parse_function_with_arguments_and_modifier(self):
        expression = "{{ func( 'farg') |  kek lol    }}     "
        subexpressions = _parse_subexpressions(expression)
        assert len(subexpressions) == 1
        se = subexpressions[0]
        assert se.function == 'func'
        assert se.argument == "'farg'"
        assert se.modifier == 'kek lol'
        assert se.start == 0
        assert se.end == expression.index('}}') + 2

    def test_parse_function_with_empty_arguments(self):
        se = _parse_subexpressions('{{ func() }}')[0]
        assert se.function == 'func'
        assert se.argument == ''
        assert se.modifier is None

    def test_parse_does_not_split_on_pipe_inside_arguments(self):
        expression = '{{ regex("([0-9]{7,10}|abc)") | global }}'
        se = _parse_subexpressions(expression)[0]
        assert se.function == 'regex'
        assert se.argument == '"([0-9]{7,10}|abc)"'
        assert se.modifier == 'global'

    def test_parse_multiple_placeholders(self):
        expression = " pre text {{ func( 'farg') |  kek lol    }} dsdsdsd {{ func2( 'f2arg') |  kek#lol    }}     "
        subexpressions = _parse_subexpressions(expression)
        assert len(subexpressions) == 2

        assert subexpressions[0].function == 'func'
        assert subexpressions[0].argument == "'farg'"
        assert subexpressions[0].modifier == 'kek lol'
        assert subexpressions[0].start == 10
        assert subexpressions[0].end == expression.index('}}') + 2

        assert subexpressions[1].function == 'func2'
        assert subexpressions[1].argument == "'f2arg'"
        assert subexpressions[1].modifier == 'kek#lol'
        assert subexpressions[1].start == expression.index('{{', subexpressions[0].end)
        assert subexpressions[1].end == expression.rfind('}}') + 2

    @pytest.mark.parametrize(('expression', 'message', 'position'), [
        pytest.param("{{ }}", "placeholder is empty", 2, id="placeholder_empty"),
        pytest.param("{{ | local }}", "function name is missing", 3, id="function_missing"),
        pytest.param("{{ func( }}", "missing closing ')' for placeholder", 0, id="missing_closing_parenthesis"),
        pytest.param("{{ func('a') }", "missing closing '}}'", 14, id="missing_closing_braces"),
        pytest.param(" {{ func() |   }}", "modifier is empty", 12, id="modifier_empty"),
        pytest.param("{{ email('ru_RU') ) }}", "unexpected ')'", 18, id="unexpected_closing_parenthesis"),
        pytest.param("{{ func(arg) trailing }}", "unexpected text after arguments", 13, id="unexpected_text_after_arguments"),
        pytest.param('{{ "unterminated }}', "unterminated quote in placeholder", 0, id="unterminated_quote"),
        pytest.param("{{ func arg }}", "unexpected text after function name 'func'", 8, id="unexpected_text_after_function_name"),
    ])
    def test_expression_errors(self, expression, message, position):
        with pytest.raises(ExpressionSyntaxError) as excinfo:
            _parse_subexpressions(expression)

        error = excinfo.value
        assert error.expression == expression
        assert error.description == message
        assert error.position == position

    def test_arguments_must_start_with_parenthesis(self):
        with pytest.raises(ExpressionSyntaxError) as excinfo:
            _extract_arguments(start=0, text=" arg)", absolute_offset=2)

        error = excinfo.value
        assert error.expression is None
        assert error.description == "arguments must start with '('"
        assert error.position == 2


class TestFunctions:

    @pytest.mark.parametrize(
        "function, expected", [
            ('root_element', 'someRootElement'),
            ('source_filename', 'filename-123'),
            ('source_extracted', 'extracted-123'),
            ('output_filename', 'output-123'),
            ('uuid', 'ebd05eb7-3677-44a5-b2df-6035d3c17334'),
            ("regex('[0-9]{7,10}')", '57366923'),
            ('regex("[0-9]{7,10}")', '57366923'),
            ("any('A', \"B\", C)", 'A'),
            ["number(0, 10)", "3"],
            ('date("2010-01-01", "2025-01-01")', '20141009'),

            ('first_name', 'Ronald'),
            ('last_name', 'Wilcox'),
            ('middle_name', 'Ronald'),
            ('phone_number', '857.536.6923'),
            ('email', 'samanthastewart@example.org'),

            ('first_name("ru_RU")', 'Еремей'),
            ('last_name("ru_RU")', 'Шарапов'),
            ('middle_name("ru_RU")', 'Гордеевич'),
            ('phone_number("ru_RU")', '+7 (573) 669-2368'),
            ('email("ru_RU")', 'lukagorshkov@example.org'),

            ('country', 'Sweden'),
            ('city', 'West Troy'),
            ('street', 'Samantha Island'),
            ('house_number', '57366'),
            ('postcode', '28388'),
            ('administrative_unit', 'Indiana'),

            ('country("ru_RU")', 'Израиль'),
            ('city("ru_RU")', 'Катав-Ивановск'),
            ('street("ru_RU")', 'ш. Сахалинское'),
            ('house_number("ru_RU")', '85'),
            ('postcode("ru_RU")', '573669'),
            ('administrative_unit("ru_RU")', 'Магаданская обл.'),

            ('company_name', 'Morse LLC'),
            ('bank_name', 'Morse LLC'),

            ('company_name("ru_RU")', 'ИП «Кузнецова Колесников»'),
            ('bank_name("ru_RU")', 'ЕАТП Банк'),

            ('inn_fl', '284151791372'),
            ('inn_ul', '2841647400'),
            ('ogrn_ip', '307415303422588'),
            ('ogrn_fl', '1116432582848'),
            ('kpp', '284145199'),
            ('snils_formatted', '888-167-630 78'),
        ]
    )
    def test_functions(self, function, expected):
        substitutor = Substitutor(Randomizer(seed=111))
        substitutor._local_context["root_element"] = 'someRootElement'
        substitutor._local_context["source_filename"] = 'filename-123'
        substitutor._local_context["source_extracted"] = 'extracted-123'
        substitutor._local_context['output_filename'] = 'output-123'

        is_found, value = substitutor.substitute_value("test", {"test": "{{" + function + "}}"}.items())
        assert is_found
        assert value == expected

    def test_any_from(self):
        substitutor = Substitutor(Randomizer(seed=111))
        results = set()
        for i in range(0, 50):
            _, value = substitutor.substitute_value("test", {"test": "{{ any_from('data/lines.txt') }}"}.items())
            results.add(value)

        assert len(results) == 3


class TestFunctionModifiers:

    def test_no_modifier(self):
        substitutor = Substitutor(Randomizer(seed=111))
        _, value_1 = substitutor.substitute_value("test", {"test": "{{ uuid }}"}.items())
        _, value_2 = substitutor.substitute_value("test", {"test": "{{ uuid }}"}.items())
        assert value_1 != value_2

    def test_local_modifier(self):
        substitutor = Substitutor(Randomizer(seed=111))
        _, value_1 = substitutor.substitute_value("test", {"test": "{{ uuid | local }}"}.items())
        _, value_2 = substitutor.substitute_value("test", {"test": "{{ uuid | local }}"}.items())
        _, value_3 = substitutor.substitute_value("test", {"test": "{{ uuid }}"}.items())
        assert value_1 == value_2
        assert value_1 != value_3

        config = GeneratorConfig(source_filename='(?P<extracted>.*).(xsd|XSD)', output_filename='_', )
        substitutor.reset_context("first_file.xsd", "someRootElement", config)

        _, value_4 = substitutor.substitute_value("test", {"test": "{{ uuid | local }}"}.items())
        assert value_4 != value_1

    def test_global_modifier(self):
        substitutor = Substitutor(Randomizer(seed=111))
        _, value_1 = substitutor.substitute_value("test", {"test": "{{ uuid | global }}"}.items())
        _, value_2 = substitutor.substitute_value("test", {"test": "{{ uuid | global }}"}.items())
        _, value_3 = substitutor.substitute_value("test", {"test": "{{ uuid | local }}"}.items())
        _, value_4 = substitutor.substitute_value("test", {"test": "{{ uuid }}"}.items())

        assert value_1 == value_2
        assert value_1 != value_3
        assert value_1 != value_4

        config = GeneratorConfig(source_filename='(?P<extracted>.*).(xsd|XSD)', output_filename='_', )
        substitutor.reset_context("first_file.xsd", "someRootElement", config)

        _, value_5 = substitutor.substitute_value("test", {"test": "{{ uuid | global }}"}.items())
        assert value_1 == value_5


def test_reset_context():
    substitutor = Substitutor(Randomizer(seed=111))

    config_1 = GeneratorConfig(
        source_filename='(?P<extracted>.*).(xsd|XSD)',
        output_filename='{{ source_extracted }}_c82f1749-36a8-4237-ad11-0c2078197df4',
    )
    substitutor.reset_context("first_file.xsd", "someRootElement", config_1)
    assert substitutor._local_context["root_element"] == "someRootElement"
    assert substitutor._local_context["source_filename"] == "first_file.xsd"
    assert substitutor._local_context["source_extracted"] == "first_file"
    assert substitutor._local_context["output_filename"] == "first_file_c82f1749-36a8-4237-ad11-0c2078197df4"

    config_2 = GeneratorConfig(
        source_filename='(?P<extracted>.*)_file.(xsd|XSD)',
        output_filename='{{ source_extracted }}_16dab037-65aa-4fcb-905f-7785ebff91d4',
    )
    substitutor.reset_context("second_file.xsd", "anotherRootElement", config_2)
    assert substitutor._local_context["root_element"] == "anotherRootElement"
    assert substitutor._local_context["source_filename"] == "second_file.xsd"
    assert substitutor._local_context["source_extracted"] == "second"
    assert substitutor._local_context["output_filename"] == "second_16dab037-65aa-4fcb-905f-7785ebff91d4"
