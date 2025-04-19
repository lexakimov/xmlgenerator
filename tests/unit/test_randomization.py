import logging

import pytest

from xmlgenerator import randomization
from xmlgenerator.randomization import Randomizer

randomization.logger.setLevel(logging.DEBUG)


@pytest.mark.repeat(10)
def test_random_no_seed():
    randomizer1 = Randomizer()
    randomizer2 = Randomizer()
    for _ in range(10):
        assert randomizer1.rnd.randint(0, 1000) != randomizer2.rnd.randint(0, 1000)


@pytest.mark.repeat(10)
def test_fake_no_seed():
    randomizer1 = Randomizer()
    randomizer2 = Randomizer()
    for _ in range(10):
        assert randomizer1.fake.name() != randomizer2.fake.name()


@pytest.mark.repeat(10)
def test_random_has_seed():
    randomizer1 = Randomizer(seed=123)
    randomizer2 = Randomizer(seed=123)
    for _ in range(10):
        assert randomizer1.rnd.randint(0, 1000) == randomizer2.rnd.randint(0, 1000)


@pytest.mark.repeat(10)
def test_fake_has_seed():
    randomizer1 = Randomizer(seed=123)
    randomizer2 = Randomizer(seed=123)
    for _ in range(10):
        assert randomizer1.fake.name() == randomizer2.fake.name()
