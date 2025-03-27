import random
import string
from datetime import datetime, timedelta

from faker import Faker


class Randomizer:
    def __init__(self, seed=None):
        self.rnd = random.Random(seed)
        self.fake = Faker(locale='ru_RU')
        self.fake.seed_instance(seed)

    def ascii_string(self, min_length=-1, max_length=-1):
        min_length = min_length if min_length and min_length > -1 else 1
        max_length = max_length if max_length and max_length >= min_length else 20
        if max_length > 50:
            max_length = 50
        length = self.rnd.randint(min_length, max_length)
        # Генерация случайной строки из букв латиницы
        letters = string.ascii_letters  # Все буквы латиницы (a-z, A-Z)
        return ''.join(self.rnd.choice(letters) for _ in range(length))

    def random_date(self, start_date: str, end_date: str) -> datetime:
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
