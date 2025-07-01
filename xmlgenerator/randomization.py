import logging
import mimetypes
import random
import re
import string
import sys
from datetime import datetime, date, time, timedelta
from pathlib import Path

import rstr
from faker import Faker

logger = logging.getLogger(__name__)


class Randomizer:
    def __init__(self, seed=None):
        if not seed:
            seed = random.randrange(sys.maxsize)
            logger.debug('initialize with random seed: %s', seed)
        else:
            logger.debug('initialize with provided seed: %s', seed)

        self._fakers = {}
        self._seed = seed
        self._rnd = random.Random(seed)
        self._rstr = rstr.Rstr(self._rnd)
        self._loaded_files = {}

    def _faker(self, locale='en_US'):
        if locale is None:
            locale = 'en_US'
        faker = self._fakers.get(locale)
        logger.debug('get Faker with locale: %s', locale)
        if faker is None:
            logger.debug('initialize new Faker with locale: %s', locale)
            faker = Faker(locale=locale)
            faker.seed_instance(self._seed)
            self._fakers[locale] = faker
        return faker

    def _lines(self, file_path: str):
        if file_path is None or len(file_path) == 0:
            raise RuntimeError('no file specified')

        file_lines = self._loaded_files.get(file_path)
        if file_lines is None:
            resolved_path = Path(file_path).resolve()
            if not resolved_path.exists():
                raise FileNotFoundError(f'file {resolved_path} does not exists')
            if not resolved_path.is_file():
                raise RuntimeError(f'{resolved_path} is not text file')
            mime = mimetypes.guess_type(resolved_path)
            if mime[0] is None or not mime[0].startswith('text/'):
                raise RuntimeError(f'file {resolved_path} is not text file')
            try:
                with open(resolved_path, 'r', encoding='utf-8') as f:
                    file_content = f.read().rstrip()
                    if not file_content:
                        file_lines = []
                    else:
                        file_lines = file_content.split('\n')
                    self._loaded_files[file_path] = file_lines
            except FileNotFoundError:
                raise FileNotFoundError(f'file {resolved_path} does not exists')

        return file_lines

    def random(self):
        return self._rnd.random()

    def any(self, options):
        return self._rnd.choice(options)

    def any_from(self, file_path):
        return self._rnd.choice(self._lines(file_path))

    def regex(self, pattern):
        xeger = self._rstr.xeger(pattern)
        return re.sub(r'\s', ' ', xeger)

    def uuid(self):
        return self._faker().uuid4()

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
        return self._faker().hexify(text=circumflexes, upper=True)

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

    # personal

    def first_name(self, args=None):
        locale = args.strip(' ').strip("'").strip('"') if args is not None else None
        return self._faker(locale).first_name_male()

    def last_name(self, args=None):
        locale = args.strip(' ').strip("'").strip('"') if args is not None else None
        return self._faker(locale).last_name_male()

    def middle_name(self, args=None):
        locale = args.strip(' ').strip("'").strip('"') if args is not None else None
        faker = self._faker(locale)
        return faker.middle_name_male() if hasattr(faker, 'middle_name_male') else faker.first_name_male()

    def phone_number(self, args=None):
        locale = args.strip(' ').strip("'").strip('"') if args is not None else None
        return self._faker(locale).phone_number()

    def email(self, args=None):
        locale = args.strip(' ').strip("'").strip('"') if args is not None else None
        return self._faker(locale).email()

    # address

    def country(self, args=None):
        locale = args.strip(' ').strip("'").strip('"') if args is not None else None
        return self._faker(locale).country()

    def city(self, args=None):
        locale = args.strip(' ').strip("'").strip('"') if args is not None else None
        faker = self._faker(locale)
        return faker.city_name() if hasattr(faker, 'city_name') else faker.city()

    def street(self, args=None):
        locale = args.strip(' ').strip("'").strip('"') if args is not None else None
        return self._faker(locale).street_name()

    def house_number(self, args=None):
        locale = args.strip(' ').strip("'").strip('"') if args is not None else None
        return self._faker(locale).building_number()

    def postcode(self, args=None):
        locale = args.strip(' ').strip("'").strip('"') if args is not None else None
        return self._faker(locale).postcode()

    def administrative_unit(self, args=None):
        locale = args.strip(' ').strip("'").strip('"') if args is not None else None
        return self._faker(locale).administrative_unit()

    # other

    def company_name(self, args=None):
        locale = args.strip(' ').strip("'").strip('"') if args is not None else None
        return self._faker(locale).company()

    def bank_name(self, args=None):
        locale = args.strip(' ').strip("'").strip('"') if args is not None else None
        faker = self._faker(locale)
        return faker.bank() if hasattr(faker, 'bank') else faker.company()

    # ru_RU only

    def inn_fl(self):
        return self._faker('ru_RU').individuals_inn()

    def inn_ul(self):
        return self._faker('ru_RU').businesses_inn()

    def ogrn_ip(self):
        return self._faker('ru_RU').individuals_ogrn()

    def ogrn_fl(self):
        return self._faker('ru_RU').businesses_ogrn()

    def kpp(self):
        return self._faker('ru_RU').kpp()

    def snils_formatted(self):
        snils = self._faker('ru_RU').snils()
        return f"{snils[:3]}-{snils[3:6]}-{snils[6:9]} {snils[9:]}"
