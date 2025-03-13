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


def zeros(s, length):
    while len(s) < length:
        s = '0' + s
    return s

def innfl():
    region = zeros(str(random.randint(1, 92)), 2)
    inspection = zeros(str(random.randint(1, 99)), 2)
    numba = zeros(str(random.randint(1, 999999)), 6)
    rezult = region + inspection + numba
    kontr = str(((7 * int(rezult[0]) + 2 * int(rezult[1]) + 4 * int(rezult[2]) + 10 * int(rezult[3]) +
                  3 * int(rezult[4]) + 5 * int(rezult[5]) + 9 * int(rezult[6]) + 4 * int(rezult[7]) +
                  6 * int(rezult[8]) + 8 * int(rezult[9])) % 11) % 10)
    kontr = '0' if kontr == '10' else kontr
    rezult += kontr
    kontr = str(((3 * int(rezult[0]) + 7 * int(rezult[1]) + 2 * int(rezult[2]) +
                  4 * int(rezult[3]) + 10 * int(rezult[4]) + 3 * int(rezult[5]) +
                  5 * int(rezult[6]) + 9 * int(rezult[7]) + 4 * int(rezult[8]) +
                  6 * int(rezult[9]) + 8 * int(rezult[10])) % 11) % 10)
    kontr = '0' if kontr == '10' else kontr
    rezult += kontr
    return rezult


def innul():
    region = zeros(str(random.randint(1, 92)), 2)
    inspection = zeros(str(random.randint(1, 99)), 2)
    numba = zeros(str(random.randint(1, 99999)), 5)
    rezult = region + inspection + numba
    kontr = str(((2 * int(rezult[0]) + 4 * int(rezult[1]) + 10 * int(rezult[2]) +
                  3 * int(rezult[3]) + 5 * int(rezult[4]) + 9 * int(rezult[5]) +
                  4 * int(rezult[6]) + 6 * int(rezult[7]) + 8 * int(rezult[8])) % 11) % 10)
    kontr = '0' if kontr == '10' else kontr
    rezult += kontr
    return rezult


def ogrn():
    priznak = str(random.randint(1, 9))
    godreg = zeros(str(random.randint(1, 16)), 2)
    region = zeros(str(random.randint(1, 92)), 2)
    inspection = zeros(str(random.randint(1, 99)), 2)
    zapis = zeros(str(random.randint(1, 99999)), 5)
    rezult = priznak + godreg + region + inspection + zapis
    kontr = str((int(rezult) % 11) % 10)
    kontr = '0' if kontr == '10' else kontr
    rezult += kontr
    return rezult


def kpp():
    region = zeros(str(random.randint(1, 92)), 2)
    inspection = zeros(str(random.randint(1, 99)), 2)
    prichina = random.randint(1, 4)
    prichina = ['01', '43', '44', '45'][prichina - 1]
    numba = zeros(str(random.randint(1, 999)), 3)
    rezult = region + inspection + prichina + numba
    return rezult


def snils():
    rand1 = zeros(str(random.randint(2, 998)), 3)
    rand2 = zeros(str(random.randint(1, 999)), 3)
    rand3 = zeros(str(random.randint(1, 999)), 3)
    rezult = rand1 + rand2 + rand3
    kontr = str(9 * int(rezult[0]) + 8 * int(rezult[1]) + 7 * int(rezult[2]) +
                6 * int(rezult[3]) + 5 * int(rezult[4]) + 4 * int(rezult[5]) +
                3 * int(rezult[6]) + 2 * int(rezult[7]) + 1 * int(rezult[8]))
    if int(kontr) < 100:
        pass
    elif int(kontr) > 101:
        kontr = str(int(kontr) % 101)
        kontr = zeros(kontr, 2)
        if int(kontr) > 99:
            kontr = '00'
    else:
        kontr = '00'
    rezult += kontr
    return rezult


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
