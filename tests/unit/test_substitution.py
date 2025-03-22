import pytest

from substitution import _pattern


@pytest.mark.parametrize("expression, expected_groups_count", [
    ('', 0),
    ('{{}}', 1),
    (' {{}}   ', 1),
    ('{{ }}', 1),
    ('{{       }}', 1),
])
def test_parse_empty_expression(expression, expected_groups_count):
    findall = _pattern.findall(expression)
    assert len(findall) == expected_groups_count


@pytest.mark.parametrize("expression, expected_function", [
    ('{{uuid}}', 'uuid'),
    ('{{    uuid }}', 'uuid'),
    ('{{    uuid       }}', 'uuid'),
    ('{{ \t\r   uuid  \r     }}', 'uuid'),
    ('{{ \t\r   (   )  \r     }}', '(   )'),
    ('{{ func }}', 'func'),
    ('{{ func | }}', 'func'),
    ('{{ func |}}', 'func'),
    ('{{ func| }}', 'func'),
])
def test_parse_expression_with_function(expression, expected_function):
    findall = _pattern.findall(expression)
    assert len(findall) == 1
    assert findall[0][0] == expected_function


@pytest.mark.parametrize("expression, expected_function, expected_modifier", [
    ('{{ func|kek}}', 'func', 'kek'),
    ('{{ func |   kek }}', 'func', 'kek'),
    ('{{ func|kek lol}}', 'func', 'kek lol'),
    ('{{ func|kek lol    }}     ', 'func', 'kek lol'),
    ("{{ func( \'farg\') |  kek lol    }}     ", "func( \'farg\')", 'kek lol'),
    ("{{ func( \'farg\') |  kek lol    }}     ", "func( \'farg\')", 'kek lol'),
])
def test_parse_expression_with_function(expression, expected_function, expected_modifier):
    findall = _pattern.findall(expression)
    assert len(findall) == 1
    assert findall[0][0] == expected_function
    assert findall[0][1] == expected_modifier


def test_parse_expression_extract_groups():
    match = _pattern.match("{{ func( \'farg\') |  kek lol    }}     ")
    assert match.group("function") == "func( \'farg\')"
    assert match.group("modifier") == "kek lol"


def test_parse_expression_few_expressions_in_one():
    findall = _pattern.findall("{{ func( \'farg\') |  kek lol    }} dsdsdsd {{ func2( \'f2arg\') |  kek#lol    }}     ")
    assert len(findall) == 2
    assert findall[0][0] == "func( \'farg\')"
    assert findall[0][1] == "kek lol"

    assert findall[1][0] == "func2( \'f2arg\')"
    assert findall[1][1] == "kek#lol"
