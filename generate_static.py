import re
import string
from xml.dom import minidom
from xml.etree import ElementTree

import xmlschema
from lxml import etree
from russian_names import RussianNames

file = '/home/akimov/desktop/wb/wb-edi/edi-doc-api/src/main/resources/schemas/fns/DP_IAKTPRM_1_987_00_05_01_02.xsd'

xsd_directory = '/home/akimov/desktop/wb/wb-edi/edi-doc-api/src/main/resources/schemas/fns/'
xsd_names = [
    "DP_IAKTPRM_1_987_00_05_01_02.xsd",
]

xsd_schema_filename = xsd_directory + xsd_names[0]

# Загрузка XSD-схемы
xsd_schema = xmlschema.XMLSchema(xsd_schema_filename)

import random


def innfl():
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


def innul():
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


# Генерация значений на основе ограничений XSD
def generate_value(xsd_type, element_name=''):
    if xsd_type is None:
        return "default_value"  # Возвращаем значение по умолчанию, если тип не определен

    if xsd_type.simple_type is None:
        return None

    # Проверяем базовый тип
    base_type = getattr(xsd_type, 'base_type', None)
    if base_type is None:
        return "default_value"  # Возвращаем значение по умолчанию, если базовый тип не определен

    if base_type.local_name == 'string':
        # Генерация строки
        if hasattr(xsd_type, 'enumeration') and xsd_type.enumeration is not None:
            # Если есть перечисление, выбираем случайное значение из него
            return random.choice(xsd_type.enumeration)
        else:

            if element_name == 'ИдФайл':
                return RussianNames(name=False, surname=True, patronymic=False, gender=1).get_person()
            if element_name == 'ВерсПрог':
                return "Python XML generator 1.0"

            if re.search('Фамилия', element_name, re.IGNORECASE):
                return RussianNames(name=False, surname=True, patronymic=False, gender=1).get_person()
            if re.search('Имя', element_name, re.IGNORECASE):
                return RussianNames(name=True, surname=False, patronymic=False, gender=1).get_person()
            if re.search('Отчество', element_name, re.IGNORECASE):
                return RussianNames(name=False, surname=False, patronymic=True, gender=1).get_person()

            if re.search('ИННФЛ', element_name, re.IGNORECASE):
                return innfl()
            if re.search('ИННЮЛ', element_name, re.IGNORECASE):
                return innul()
            if re.search('ОГРН', element_name, re.IGNORECASE):
                return ogrn()
            if re.search('КПП', element_name, re.IGNORECASE):
                return kpp()
            if re.search('СНИЛС', element_name, re.IGNORECASE):
                return snils()

            # Иначе генерируем случайную строку
            return ''.join(random.choices(string.ascii_letters, k=10))
    elif base_type.local_name == 'integer':
        # Генерация целого числа
        min_value = getattr(xsd_type, 'min_inclusive', 0)
        max_value = getattr(xsd_type, 'max_inclusive', 100)
        return random.randint(min_value, max_value)
    elif base_type.local_name == 'decimal':
        # Генерация десятичного числа
        min_value = float(getattr(xsd_type, 'min_inclusive', 0.0))
        max_value = float(getattr(xsd_type, 'max_inclusive', 100.0))
        return round(random.uniform(min_value, max_value), 2)
    elif base_type.local_name == 'boolean':
        # Генерация булевого значения
        return random.choice([True, False])
    else:
        # Для других типов возвращаем значение по умолчанию
        return "default_value"


# Рекурсивно добавляем элементы и атрибуты в соответствии с XSD-схемой
def add_elements(xml_element, xsd_element):
    # Добавляем атрибуты, если они есть
    if hasattr(xsd_element, 'attributes'):
        for attr_name, attr in xsd_element.attributes.items():
            # Генерация значения атрибута на основе его типа
            attr_value = generate_value(attr.type, attr_name)
            xml_element.set(attr_name, str(attr_value))

    # Обрабатываем дочерние элементы
    if hasattr(xsd_element, 'type') and hasattr(xsd_element.type, 'content'):
        for xsd_child in xsd_element.type.content:
            if isinstance(xsd_child, xmlschema.validators.elements.XsdElement):
                # Если это элемент, создаем его и рекурсивно добавляем дочерние элементы
                xml_child = etree.SubElement(xml_element, xsd_child.name)
                if hasattr(xsd_child, 'type'):
                    # Генерация значения элемента на основе его типа
                    element_value = generate_value(xsd_child.type, xsd_child.name)
                    xml_child.text = element_value
                add_elements(xml_child, xsd_child)
            elif isinstance(xsd_child, xmlschema.validators.groups.XsdGroup):
                # Если это группа, обрабатываем её элементы
                for group_child in xsd_child:
                    if isinstance(group_child, xmlschema.validators.elements.XsdElement):
                        group_child_element = etree.SubElement(xml_element, group_child.name)
                        if hasattr(group_child, 'type'):
                            # Генерация значения элемента на основе его типа
                            group_child_element.text = str(generate_value(group_child.type, group_child.name))
                        add_elements(group_child_element, group_child)


# Создание XML-документа на основе XSD-схемы
def generate_xml_from_xsd(xsd_schema):
    # Получаем корневой элемент схемы
    xsd_root_element = xsd_schema.root_elements[0]  # Получаем имя корневого элемента
    xml_root_element = etree.Element(xsd_root_element.name)

    # Начинаем с корневого элемента схемы
    add_elements(xml_root_element, xsd_root_element)
    return xml_root_element


def prettify(elem):
    rough_string = ElementTree.tostring(elem, 'windows-1251')
    reparsed = minidom.parseString(rough_string)
    return reparsed.toprettyxml(indent="    ", )  # encoding='windows-1251'


# Генерация XML-документа
xml_root = generate_xml_from_xsd(xsd_schema)

# Преобразование в строку и вывод
xml_str = prettify(xml_root)
print(xml_str)

# # Сохранение в файл
# with open('output.xml', 'w') as f:
#     f.write(xml_str)
