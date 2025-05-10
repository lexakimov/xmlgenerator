import logging
import random
import re
import string
import sys
from datetime import datetime, date, time, timedelta

import rstr
from faker import Faker

logger = logging.getLogger(__name__)


class Randomizer:
    def __init__(self, seed=None, locale='ru_RU'):
        if not seed:
            seed = random.randrange(sys.maxsize)
            logger.debug('initialize with random seed: %s', seed)
        else:
            logger.debug('initialize with provided seed: %s', seed)

        self._rnd = random.Random(seed)
        self._fake = Faker(locale=locale)
        self._fake.seed_instance(seed)
        self._rstr = rstr.Rstr(self._rnd)

    def random(self):
        return self._rnd.random()

    def any(self, options):
        return self._rnd.choice(options)

    def regex(self, pattern):
        xeger = self._rstr.xeger(pattern)
        return re.sub(r'\s', ' ', xeger)

    def uuid(self):
        return self._fake.uuid4()

    def integer(self, min_value, max_value):
        return self._rnd.randint(min_value, max_value)

    def float(self, min_value, max_value):
        return self._rnd.uniform(min_value, max_value)

    def ascii_string(self, min_length, max_length):
        if min_length is None:
            min_length = 1
        if max_length is None:
            max_length = 20

        length = self._rnd.randint(min_length, max_length)
        letters = string.ascii_lowercase
        return ''.join(self._rnd.choice(letters) for _ in range(length)).capitalize()

    def hex_string(self, min_length, max_length):
        if min_length is None:
            min_length = 1
        if max_length is None:
            max_length = 20

        length = self._rnd.randint(min_length, max_length)
        circumflexes = ''.join('^' for _ in range(length))
        return self._fake.hexify(text=circumflexes, upper=True)

    def random_date(self, start_date: str = '1990-01-01', end_date: str = '2025-12-31') -> date:
        start = date.fromisoformat(start_date)
        end = date.fromisoformat(end_date)

        delta = (end - start).days
        random_days = self._rnd.randint(0, delta)
        return start + timedelta(days=random_days)

    def random_time(self, start_time: str = '00:00:00', end_time: str = '23:59:59') -> time:
        start = time.fromisoformat(start_time)
        end = time.fromisoformat(end_time)

        random_h = self._rnd.randint(start.hour, end.hour)
        random_m = self._rnd.randint(start.minute, end.minute)
        random_s = self._rnd.randint(start.second, end.second)

        return time(hour=random_h, minute=random_m, second=random_s)

    def random_datetime(self, start_date: str = '1990-01-01', end_date: str = '2025-12-31') -> datetime:
        start = datetime.strptime(start_date, "%Y-%m-%d")
        end = datetime.strptime(end_date, "%Y-%m-%d")

        delta = (end - start).days
        random_days = self._rnd.randint(0, delta)
        return start + timedelta(days=random_days)

    def last_name(self):
        return self._fake.last_name_male()
    
    def first_name(self):
        return self._fake.first_name_male()
    
    def middle_name(self):
        return self._fake.middle_name_male()
    
    def address_text(self):
        return self._fake.address()
    
    def administrative_unit(self):
        return self._fake.administrative_unit()
    
    def house_number(self):
        return self._fake.building_number()
    
    def city_name(self):
        return self._fake.city_name() if hasattr(self._fake, 'city_name') else self._fake.city()

    def country(self):
        return self._fake.country()
    
    def postcode(self):
        return self._fake.postcode()
    
    def company_name(self):
        return self._fake.company()
    
    def bank_name(self):
        return self._fake.bank()
    
    def phone_number(self):
        return self._fake.phone_number()
    
    def inn_fl(self):
        return self._fake.individuals_inn()
    
    def inn_ul(self):
        return self._fake.businesses_inn()
    
    def ogrn_ip(self):
        return self._fake.individuals_ogrn()
    
    def ogrn_fl(self):
        return self._fake.businesses_ogrn()
    
    def kpp(self):
        return self._fake.kpp()

    def snils_formatted(self):
        snils = self._fake.snils()
        return f"{snils[:3]}-{snils[3:6]}-{snils[6:9]} {snils[9:]}"

    def email(self):
        return self._fake.email()
