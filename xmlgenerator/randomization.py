import logging
import random
import string
import sys
from datetime import datetime, date, time, timedelta

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

        self.rnd = random.Random(seed)
        self.fake = Faker(locale='ru_RU')
        self.fake.seed_instance(seed)
        self.re_gen = rstr.Rstr(self.rnd)

    def ascii_string(self, min_length=-1, max_length=-1):
        min_length = min_length if min_length and min_length > -1 else 1
        max_length = max_length if max_length and max_length >= min_length else 20
        if max_length > 50:
            max_length = 50
        length = self.rnd.randint(min_length, max_length)
        # Генерация случайной строки из букв латиницы
        letters = string.ascii_letters  # Все буквы латиницы (a-z, A-Z)
        return ''.join(self.rnd.choice(letters) for _ in range(length))

    def random_date(self, start_date: str = '1990-01-01', end_date: str = '2025-12-31') -> date:
        # Преобразуем строки в объекты datetime
        start = date.fromisoformat(start_date)
        end = date.fromisoformat(end_date)

        # Вычисляем разницу в днях между начальной и конечной датой
        delta = (end - start).days

        # Генерируем случайное количество дней в пределах delta
        random_days = self.rnd.randint(0, delta)

        # Добавляем случайное количество дней к начальной дате
        return start + timedelta(days=random_days)

    def random_time(self, start_time: str = '00:00:00', end_time: str = '23:59:59') -> time:
        start = time.fromisoformat(start_time)
        end = time.fromisoformat(end_time)

        random_h = self.rnd.randint(start.hour, end.hour)
        random_m = self.rnd.randint(start.minute, end.minute)
        random_s = self.rnd.randint(start.second, end.second)

        return time(hour=random_h, minute=random_m, second=random_s)

    def random_datetime(self, start_date: str = '1990-01-01', end_date: str = '2025-12-31') -> datetime:
        # Преобразуем строки в объекты datetime
        start = datetime.strptime(start_date, "%Y-%m-%d")
        end = datetime.strptime(end_date, "%Y-%m-%d")

        # Вычисляем разницу в днях между начальной и конечной датой
        delta = (end - start).days

        # Генерируем случайное количество дней в пределах delta
        random_days = self.rnd.randint(0, delta)

        # Добавляем случайное количество дней к начальной дате
        return start + timedelta(days=random_days)

    def snils_formatted(self):
        snils = self.fake.snils()
        return f"{snils[:3]}-{snils[3:6]}-{snils[6:9]} {snils[9:]}"
