import pytest

from xmlgenerator.randomization import Randomizer
from xmlgenerator.substitution import _pattern, Substitutor


@pytest.mark.parametrize("expression, expected_groups_count", [
    ('', 0),
    ('{{}}', 1),
    (' {{}} ', 1),
    ('{{ }}', 1),
    ('{{ }} {{ }} ', 2),
    ('{{ }}abc{{ }} ', 2),
])
def test_parse_empty_expression(expression, expected_groups_count):
    findall = _pattern.findall(expression)
    assert len(findall) == expected_groups_count
    for i in range(expected_groups_count):
        assert len(findall[i]) == 3
        assert findall[i][0] == ""
        assert findall[i][1] == ""
        assert findall[i][2] == ""


@pytest.mark.parametrize("expression, expected_function", [
    ('{{uuid}}', 'uuid'),
    ('{{    uuid }}', 'uuid'),
    ('{{    uuid       }}', 'uuid'),
    ('{{ \t\r   uuid  \r     }}', 'uuid'),
    ('{{ func }}', 'func'),
    ('{{ func | }}', 'func'),
    ('{{ func |}}', 'func'),
    ('{{ func| }}', 'func'),
])
def test_parse_expression_with_function(expression, expected_function):
    findall = _pattern.findall(expression)
    assert len(findall) == 1
    assert len(findall[0]) == 3
    assert findall[0][0] == expected_function
    assert findall[0][1] == ""
    assert findall[0][2] == ""


@pytest.mark.parametrize("expression, expected_function, expected_argument, expected_modifier", [
    ('{{ func|kek}}', 'func', '', 'kek'),
    ('{{ func |   kek }}', 'func', '', 'kek'),
    ('{{ func|kek lol}}', 'func', '', 'kek lol'),
    ('{{ func|kek lol    }}     ', 'func', '', 'kek lol'),
    ("{{ func( 'farg') |  kek lol    }}     ", "func", "'farg'", 'kek lol'),
    ("{{ func( 'farg') |  kek lol    }}     ", "func", "'farg'", 'kek lol'),
])
def test_parse_expression_with_function_2(expression, expected_function, expected_argument, expected_modifier):
    findall = _pattern.findall(expression)
    assert len(findall) == 1
    assert len(findall[0]) == 3
    assert findall[0][0] == expected_function
    assert findall[0][1] == expected_argument
    assert findall[0][2] == expected_modifier


def test_parse_expression_extract_groups():
    match = _pattern.match("{{ func( 'farg') |  kek lol    }}     ")
    assert match.group("function") == "func"
    assert match.group("argument") == "'farg'"
    assert match.group("modifier") == "kek lol"


def test_parse_expression_extract_groups_01():
    match = _pattern.match("{{ regex(\"pattern\") }}     ")
    assert match.group("function") == "regex"
    assert match.group("argument") == "\"pattern\""
    assert match.group("modifier") is None


def test_parse_expression_few_expressions_in_one():
    findall = _pattern.findall("{{ func( \'farg\') |  kek lol    }} dsdsdsd {{ func2( \'f2arg\') |  kek#lol    }}     ")
    assert len(findall) == 2
    assert findall[0][0] == "func"
    assert findall[0][1] == "'farg'"
    assert findall[0][2] == "kek lol"

    assert findall[1][0] == "func2"
    assert findall[1][1] == "\'f2arg\'"
    assert findall[1][2] == "kek#lol"

class TestFunctions:

    @pytest.mark.parametrize(
        "function, expected", [
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
        substitutor._local_context["source_filename"] = 'filename-123'
        substitutor._local_context["source_extracted"] = 'extracted-123'
        substitutor._local_context['output_filename'] = 'output-123'

        is_found, value = substitutor.substitute_value("test", {"test": "{{" + function + "}}"}.items())
        assert is_found
        assert value == expected
