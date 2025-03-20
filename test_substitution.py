from substitution import _pattern


def test_01():
    findall = _pattern.findall("")
    assert 0 == len(findall)


def test_02():
    findall = _pattern.findall("{{}}")
    assert 1 == len(findall)


def test_03():
    findall = _pattern.findall(" {{}}   ")
    assert 1 == len(findall)


def test_04():
    findall = _pattern.findall("{{ }}")
    assert 1 == len(findall)


def test_05():
    findall = _pattern.findall("{{       }}")
    assert 1 == len(findall)


def test_06():
    findall = _pattern.findall("{{uuid}}")
    assert 1 == len(findall)
    assert "uuid" == findall[0][0]


def test_07():
    findall = _pattern.findall("{{    uuid }}")
    assert 1 == len(findall)
    assert "uuid" == findall[0][0]


def test_08():
    findall = _pattern.findall("{{    uuid       }}")
    assert 1 == len(findall)
    assert "uuid" == findall[0][0]


def test_09():
    findall = _pattern.findall("{{ \t\r   uuid  \r     }}")

    assert 1 == len(findall)
    assert "uuid" == findall[0][0]


def test_10():
    findall = _pattern.findall("{{ \t\r   (   )  \r     }}")
    assert 1 == len(findall)
    assert "(   )" == findall[0][0]


def test_11():
    findall = _pattern.findall("{{ func }}")
    assert 1 == len(findall)
    assert "func" == findall[0][0]


def test_12():
    findall = _pattern.findall("{{ func | }}")
    assert 1 == len(findall)
    assert "func" == findall[0][0]


def test_13():
    findall = _pattern.findall("{{ func |}}")
    assert 1 == len(findall)
    assert "func" == findall[0][0]


def test_14():
    findall = _pattern.findall("{{ func| }}")
    assert 1 == len(findall)
    assert "func" == findall[0][0]


def test_15():
    findall = _pattern.findall("{{ func|kek}}")
    assert 1 == len(findall)
    assert "func" == findall[0][0]
    assert "kek" == findall[0][1]


def test_16():
    findall = _pattern.findall("{{ func |   kek }}")
    assert 1 == len(findall)
    assert "func" == findall[0][0]
    assert "kek" == findall[0][1]


def test_17():
    findall = _pattern.findall("{{ func|kek lol}}")
    assert 1 == len(findall)
    assert "func" == findall[0][0]
    assert "kek lol" == findall[0][1]


def test_18():
    findall = _pattern.findall("{{ func|kek lol    }}     ")
    assert 1 == len(findall)
    assert "func" == findall[0][0]
    assert "kek lol" == findall[0][1]


def test_19():
    findall = _pattern.findall("{{ func( \'farg\') |  kek lol    }}     ")
    assert 1 == len(findall)
    assert "func( \'farg\')" == findall[0][0]
    assert "kek lol" == findall[0][1]


def test_20():
    match = _pattern.match("{{ func( \'farg\') |  kek lol    }}     ")
    assert "func( \'farg\')" == match.group("function")
    assert "kek lol" == match.group("modifier")


def test_21():
    findall = _pattern.findall("{{ func( \'farg\') |  kek lol    }} dsdsdsd {{ func2( \'f2arg\') |  kek#lol    }}     ")
    assert 2 == len(findall)
    assert "func( \'farg\')" == findall[0][0]
    assert "kek lol" == findall[0][1]

    assert "func2( \'f2arg\')" == findall[1][0]
    assert "kek#lol" == findall[1][1]
