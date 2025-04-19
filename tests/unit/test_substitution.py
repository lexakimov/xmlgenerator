import pytest

from xmlgenerator.substitution import _pattern


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
