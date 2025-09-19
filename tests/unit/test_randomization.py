import logging
from datetime import time

import pytest

from xmlgenerator import randomization
from xmlgenerator.randomization import Randomizer

randomization.logger.setLevel(logging.DEBUG)


@pytest.mark.repeat(10)
def test_random_no_seed():
    randomizer1 = Randomizer()
    randomizer2 = Randomizer()
    for _ in range(5):
        assert randomizer1.integer(0, 1000000) != randomizer2.integer(0, 1000000)


@pytest.mark.repeat(10)
def test_fake_no_seed():
    randomizer1 = Randomizer()
    randomizer2 = Randomizer()
    for _ in range(5):
        assert randomizer1.email() != randomizer2.email()


def test_random_has_seed():
    randomizer1 = Randomizer(seed=123)
    randomizer2 = Randomizer(seed=123)
    for _ in range(5):
        assert randomizer1.integer(0, 1000000) == randomizer2.integer(0, 1000000)


def test_fake_has_seed():
    randomizer1 = Randomizer(seed=123)
    randomizer2 = Randomizer(seed=123)
    for _ in range(5):
        assert randomizer1.email() == randomizer2.email()


def test_random_time_cross_hour():
    randomizer = Randomizer(seed=123)
    generated_time = randomizer.random_time('09:45:00', '17:15:00')

    assert time.fromisoformat('09:45:00') <= generated_time <= time.fromisoformat('17:15:00')
