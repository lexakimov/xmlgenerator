import random
import string
import uuid
from datetime import datetime, timedelta


def ascii_string(min_length=-1, max_length=-1):
    min_length = min_length if min_length > -1 else 1
    max_length = max_length if max_length >= min_length else 20
    if max_length > 50:
        max_length = 50
    length = random.randint(min_length, max_length)
    # Генерация случайной строки из букв латиницы
    letters = string.ascii_letters  # Все буквы латиницы (a-z, A-Z)
    return ''.join(random.choice(letters) for _ in range(length))


def random_date(start_date: str, end_date: str) -> datetime:
    # Преобразуем строки в объекты datetime
    start = datetime.strptime(start_date, "%Y-%m-%d")
    end = datetime.strptime(end_date, "%Y-%m-%d")

    # Вычисляем разницу в днях между начальной и конечной датой
    delta = (end - start).days

    # Генерируем случайное количество дней в пределах delta
    random_days = random.randint(0, delta)

    # Добавляем случайное количество дней к начальной дате
    return start + timedelta(days=random_days)


def counterparty_id():
    part_1 = int(random.uniform(1000000000, 9999999999))
    part_2 = int(random.uniform(100000000, 999999999))
    part_3 = int(random.uniform(100000000000000000000, 999999999999999999999))

    return f"2BM-{part_1}-{part_2}-{part_3}"


def id_file(prefix):
    # R_Т_A_О_GGGGMMDD_N, где:
    # R_Т – префикс
    # А – идентификатор получателя
    receiver_id = counterparty_id()
    # О – идентификатор отправителя
    sender_id = counterparty_id()
    # GGGG – год формирования передаваемого файла обмена, MM - месяц, DD - день
    date_str = random_date("2010-01-01", "2025-01-01").strftime("%Y%m%d")
    # N – 36 символьный глобально уникальный идентификатор GUID
    n = uuid.uuid4()
    return f"{prefix}_{receiver_id}_{sender_id}_{date_str}_{n}"
