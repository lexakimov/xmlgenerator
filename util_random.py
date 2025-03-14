import random
import string
import uuid
from datetime import datetime, timedelta


def inn_fl():
    # Генерация случайных частей ИНН
    region = f"{random.randint(1, 92):02d}"
    inspection = f"{random.randint(1, 99):02d}"
    numba = f"{random.randint(1, 999999):06d}"
    rezult = region + inspection + numba

    # Функция для вычисления контрольной цифры
    def calculate_control_digit(s, weights):
        total = sum(int(s[i]) * weights[i] for i in range(len(weights)))
        return str((total % 11) % 10)

    # Веса для первой и второй контрольных цифр
    weights1 = [7, 2, 4, 10, 3, 5, 9, 4, 6, 8]
    weights2 = [3, 7, 2, 4, 10, 3, 5, 9, 4, 6, 8]

    # Вычисление контрольных цифр
    kontr1 = calculate_control_digit(rezult, weights1)
    kontr1 = '0' if kontr1 == '10' else kontr1
    rezult += kontr1

    kontr2 = calculate_control_digit(rezult, weights2)
    kontr2 = '0' if kontr2 == '10' else kontr2
    rezult += kontr2

    return rezult


def inn_ul():
    # Генерация случайных частей ИНН
    rezult = (
        f"{random.randint(1, 92):02d}"  # регион
        f"{random.randint(1, 99):02d}"  # инспекция
        f"{random.randint(1, 99999):05d}"  # номер
    )

    # Веса для контрольной цифры
    weights = [2, 4, 10, 3, 5, 9, 4, 6, 8]

    # Вычисление контрольной цифры
    kontr = str(sum(int(rezult[i]) * weights[i] for i in range(9)) % 11 % 10)
    kontr = '0' if kontr == '10' else kontr

    return rezult + kontr


def ogrn():
    # Генерация случайных частей ОГРН
    rezult = (
        f"{random.randint(1, 9)}"  # признак
        f"{random.randint(1, 16):02d}"  # год регистрации
        f"{random.randint(1, 92):02d}"  # регион
        f"{random.randint(1, 99):02d}"  # инспекция
        f"{random.randint(1, 99999):05d}"  # номер записи
    )

    # Вычисление контрольной цифры
    kontr = str(int(rezult) % 11 % 10)
    kontr = '0' if kontr == '10' else kontr

    return rezult + kontr


def ogrn_ip():
    # Генерация случайных частей ОГРН
    rezult = (
        f"{random.randint(3, 4)}"  # признак
        f"{random.randint(1, 16):02d}"  # год регистрации
        f"{random.randint(1, 92):02d}"  # регион
        f"{random.randint(1, 999999999):09d}"  # номер записи
    )

    # Вычисление контрольной цифры
    kontr = str(int(rezult) % 11 % 10)
    kontr = '0' if kontr == '10' else kontr

    return rezult + kontr


def kpp():
    return (
        f"{random.randint(1, 92):02d}"  # регион
        f"{random.randint(1, 99):02d}"  # инспекция
        f"{random.choice(['01', '43', '44', '45'])}"  # причина
        f"{random.randint(1, 999):03d}"  # номер
    )


def snils():
    # Генерация случайных чисел и объединение их в строку
    rand1 = random.randint(2, 998)
    rand2 = random.randint(1, 999)
    rand3 = random.randint(1, 999)
    snils_base = f"{rand1:03}{rand2:03}{rand3:03}"

    # Вычисление контрольной суммы
    weights = [9, 8, 7, 6, 5, 4, 3, 2, 1]
    kontr = sum(int(snils_base[i]) * weights[i] for i in range(9))

    # Определение контрольного числа
    if kontr < 100:
        kontr = kontr
    elif kontr > 101:
        kontr = kontr % 101
        if kontr > 99:
            kontr = 0
    else:
        kontr = 0

    # Добавление контрольного числа к базовому номеру
    snils_full = f"{snils_base}{kontr:02}"
    return snils_full


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
