import random
import re
import string
import sys
from xml.dom import minidom
from xml.etree import ElementTree

import rstr
import xmlschema
from lxml import etree
from russian_names import RussianNames
from xmlschema.validators import XsdComplexType, XsdAtomicRestriction


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


def random_string(min_length=-1, max_length=-1):
    min_length = min_length if min_length > -1 else 1
    max_length = max_length if max_length >= min_length else 20
    if max_length > 50:
        max_length = 50
    length = random.randint(min_length, max_length)
    # Генерация случайной строки из букв латиницы
    letters = string.ascii_letters  # Все буквы латиницы (a-z, A-Z)
    return ''.join(random.choice(letters) for _ in range(length))


# Генерация значений на основе ограничений XSD
def generate_value(xsd_type, target_name):
    # Тип не определен
    if xsd_type is None:
        return None

    if isinstance(xsd_type, XsdComplexType):
        return None

    if isinstance(xsd_type, XsdAtomicRestriction):
        if hasattr(xsd_type, 'enumeration') and xsd_type.enumeration is not None:
            # Если есть перечисление, выбираем случайное значение из него
            return random.choice(xsd_type.enumeration)

    # Проверяем базовый тип
    base_type = getattr(xsd_type, 'base_type', None)
    if base_type is None:
        return "default_value"

    if base_type.local_name == 'string':
        # Генерация строки
        if hasattr(xsd_type, 'enumeration') and xsd_type.enumeration is not None:
            # Если есть перечисление, выбираем случайное значение из него
            return random.choice(xsd_type.enumeration)
        else:

            if target_name == 'ИдФайл' or target_name == 'FileID':
                return "ID_FILE"
            if target_name == 'ВерсПрог':
                return "Python XML generator 1.0"

            if re.search('Фамилия', target_name, re.IGNORECASE):
                return RussianNames(name=False, surname=True, patronymic=False, gender=1).get_person()
            if re.search('Имя', target_name, re.IGNORECASE):
                return RussianNames(name=True, surname=False, patronymic=False, gender=1).get_person()
            if re.search('Отчество', target_name, re.IGNORECASE):
                return RussianNames(name=False, surname=False, patronymic=True, gender=1).get_person()

            if re.search('ИННФЛ', target_name, re.IGNORECASE):
                return innfl()
            if re.search('ИННЮЛ', target_name, re.IGNORECASE):
                return innul()
            if re.search('ОГРН', target_name, re.IGNORECASE):
                return ogrn()
            if re.search('КПП', target_name, re.IGNORECASE):
                return kpp()
            if re.search('СНИЛС', target_name, re.IGNORECASE):
                return snils()

            if isinstance(xsd_type, XsdAtomicRestriction):
                if hasattr(xsd_type, 'patterns') and xsd_type.patterns is not None:
                    # Генерация строки по regex
                    random_pattern = random.choice(xsd_type.patterns)
                    return rstr.xeger(random_pattern.attrib['value'])

            # Иначе генерируем случайную строку
            min_length = xsd_type.min_length or -1
            max_length = xsd_type.max_length or -1
            return random_string(min_length, max_length)
    elif base_type.local_name == 'integer':
        # Генерация целого числа
        min_value = getattr(xsd_type, 'min_inclusive', 0)
        max_value = getattr(xsd_type, 'max_inclusive', 10000)
        return str(random.randint(min_value, max_value))
    elif base_type.local_name == 'decimal':
        # Генерация десятичного числа
        min_value = float(getattr(xsd_type, 'min_inclusive', 0.0))
        max_value = float(getattr(xsd_type, 'max_inclusive', 10000.0))
        return str(round(random.uniform(min_value, max_value), 2))
    elif base_type.local_name == 'boolean':
        # Генерация булевого значения
        return random.choice([True, False])
    elif isinstance(base_type, XsdAtomicRestriction):
        if hasattr(base_type, 'patterns') and base_type.patterns is not None:
            # Генерация строки по regex
            random_pattern = random.choice(base_type.patterns)
            return rstr.xeger(random_pattern.attrib['value'])
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
            if attr_value is not None:
                xml_element.set(attr_name, str(attr_value))

    # Обрабатываем дочерние элементы
    if hasattr(xsd_element, 'type') and hasattr(xsd_element.type, 'content'):
        content = xsd_element.type.content

        if isinstance(content, xmlschema.validators.groups.XsdGroup):
            if content.model == 'choice':
                group_child = random.choice(content)
                if isinstance(group_child, xmlschema.validators.elements.XsdElement):
                    group_child_element = etree.SubElement(xml_element, group_child.name)
                    if hasattr(group_child, 'type'):
                        # Генерация значения элемента на основе его типа
                        element_value = generate_value(group_child.type, group_child.name)
                        group_child_element.text = element_value
                    add_elements(group_child_element, group_child)
            if content.model == 'sequence':
                for group_child in content:
                    if isinstance(group_child, xmlschema.validators.elements.XsdElement):
                        group_child_element = etree.SubElement(xml_element, group_child.name)
                        if hasattr(group_child, 'type'):
                            # Генерация значения элемента на основе его типа
                            element_value = generate_value(group_child.type, group_child.name)
                            group_child_element.text = element_value
                        add_elements(group_child_element, group_child)
        else:
            for xsd_child in content:
                if isinstance(xsd_child, xmlschema.validators.elements.XsdElement):
                    # Если это элемент, создаем его и рекурсивно добавляем дочерние элементы
                    xml_child = etree.SubElement(xml_element, xsd_child.name)
                    if hasattr(xsd_child, 'type'):
                        # Генерация значения элемента на основе его типа
                        element_value = generate_value(xsd_child.type, xsd_child.name)
                        xml_child.text = element_value
                    add_elements(xml_child, xsd_child)


# Создание XML-документа на основе XSD-схемы
def generate_xml_from_xsd(xsd_schema):
    # Получаем корневой элемент схемы
    xsd_root_element = xsd_schema.root_elements[0]  # Получаем имя корневого элемента
    xml_root_element = etree.Element(xsd_root_element.name)

    # Начинаем с корневого элемента схемы
    add_elements(xml_root_element, xsd_root_element)
    return xml_root_element


xsd_directory = '/home/akimov/desktop/wb/wb-edi/edi-doc-api/src/main/resources/schemas/fns/'
xsd_names = [
    "DP_IAKTPRM_1_987_00_05_01_02.xsd",
    "DP_INFSOOB_1_981_00_05_01_01.xsd",
    "DP_IZVPOL_1_982_00_01_01_01.xsd",
    "DP_IZVPOL_1_982_00_01_02_02.xsd",
    "DP_IZVPOL_1_982_00_01_03_01.xsd",
    "DP_OTORG12_1_986_00_05_01_02.xsd",
    "DP_PDOTPR_1_983_00_01_01_01.xsd",
    "DP_PDOTPR_1_983_00_01_02_02.xsd",
    "DP_PDOTPR_1_983_00_01_03_01.xsd",
    "DP_PDPOL_1_984_00_01_01_01.xsd",
    "DP_PDPOL_1_984_00_01_02_02.xsd",
    "DP_PDPOL_1_984_00_01_03_01.xsd",
    "DP_PRANNUL_1_985_00_01_01_01.xsd",
    "DP_PRANNUL_1_985_00_01_01_02.xsd",
    "DP_PRIRASXDOP_1_994_02_05_01_01.xsd",
    "DP_PRIRASXPRIN_1_994_01_05_01_02.xsd",
    "DP_PTORG12_1_989_00_05_01_02.xsd",
    "DP_REZRUISP_1_990_01_05_02_01.xsd",
    "DP_REZRUZAK_1_990_02_05_02_01.xsd",
    "DP_TOVTORGPOK_1_992_02_05_02_01.xsd",
    "DP_TOVTORGPR_1_992_01_05_02_01.xsd",
    "DP_UVUTOCH_1_985_00_01_01_01.xsd",
    "DP_UVUTOCH_1_985_00_01_02_02.xsd",
    "DP_UVUTOCH_1_985_00_01_03_01.xsd",
    "DP_ZAKTPRM_1_990_00_05_01_02.xsd",
    "ON_AKTREKLOTP_1_961_01_05_01_01.xsd",
    "ON_AKTREKLPOL_1_961_02_05_01_01.xsd",
    "ON_AKTREZRABP_1_971_01_01_00_02.xsd",
    "ON_AKTREZRABZ_1_971_02_01_00_01.xsd",
    "ON_AKTSVEROTP_1_972_01_05_01_01.xsd",
    "ON_AKTSVERPOL_1_972_02_05_01_01.xsd",
    "ON_CONSGRPO_1_965_05_05_01_01.xsd",
    "ON_CONSIZM_1_965_03_05_01_01.xsd",
    "ON_CONSIZMPDTV_1_965_04_05_01_01.xsd",
    "ON_CONSOTPR_1_965_01_05_01_01.xsd",
    "ON_CONSPRV_1_965_02_05_01_01.xsd",
    "ON_CONSPRVYD_1_965_06_05_01_01.xsd",
    "ON_DOGDOC_1_999_01_01_01_02.xsd",
    "ON_DOGFRAKHTEL_1_976_01_05_01_01.xsd",
    "ON_DOGFRASHCH_1_976_02_05_01_01.xsd",
    "ON_DOGMPOTPR_1_966_01_05_01_01.xsd",
    "ON_DOGMPPRV_1_966_02_05_01_01.xsd",
    "ON_DOGMPSOGLS_1_964_04_05_01_01.xsd",
    "ON_DOGMPSOGLS_1_966_04_05_01_01.xsd",
    "ON_DOGMPSOGLSH_1_966_03_05_01_01.xsd",
    "ON_DOGVTRGO_1_964_01_05_01_01.xsd",
    "ON_DOGVTRPRV_1_964_02_05_01_02.xsd",
    "ON_DOGVTRSOGLSH_1_964_03_05_01_02.xsd",
    "ON_DOPLKNPOK_1_908_01_05_01_04.xsd",
    "ON_DOPLKNPOK_1_908_01_05_02_01.xsd",
    "ON_DOPLKNPROD_1_909_01_05_01_05.xsd",
    "ON_DOPLKNPROD_1_909_01_05_02_01.xsd",
    "ON_DOPLKNPROD_1_909_01_05_04_01.xsd",
    "ON_DORVEDGP_1_963_03_05_01_01.xsd",
    "ON_DORVEDIZM_1_963_02_05_01_01.xsd",
    "ON_DORVEDPRV_1_963_01_05_01_01.xsd",
    "ON_GARANTLET_1_967_01_05_01_01.xsd",
    "ON_GUCHSFAKT_1_910_01_05_01_03.xsd",
    "ON_GUCHSFAKT_1_910_01_05_02_01.xsd",
    "ON_KNPOK_1_898_01_05_01_04.xsd",
    "ON_KNPOK_1_898_01_05_02_01.xsd",
    "ON_KNPROD_1_899_01_05_01_05.xsd",
    "ON_KNPROD_1_899_01_05_02_01.xsd",
    "ON_KNPROD_1_899_01_05_04_01.xsd",
    "ON_KORSCHFDOPPOK_1_996_02_05_02_01.xsd",
    "ON_KORSCHFDOPPR_1_996_01_05_02_01.xsd",
    "ON_KORSFAKT_1_911_01_05_01_03.xsd",
    "ON_KORSFAKT_1_911_01_05_02_01.xsd",
    "ON_KVPRIMGR_1_962_01_05_01_01.xsd",
    "ON_NKORSCHFDOPPOK_1_996_04_05_01_03.xsd",
    "ON_NKORSCHFDOPPR_1_996_03_05_01_04.xsd",
    "ON_NSCHFDOPPOK_1_997_02_05_01_02.xsd",
    "ON_NSCHFDOPPOK_1_997_02_05_02_01.xsd",
    "ON_NSCHFDOPPOK_1_997_02_05_03_01.xsd",
    "ON_NSCHFDOPPR_1_997_01_05_01_03.xsd",
    "ON_NSCHFDOPPR_1_997_01_05_02_01.xsd",
    "ON_NSCHFDOPPR_1_997_01_05_03_01.xsd",
    "ON_OTZGARANT_1_967_02_05_01_01.xsd",
    "ON_PRICELISTISP_1_883_01_05_01_01.xsd",
    "ON_PRICELISTZAK_1_883_02_05_01_01.xsd",
    "ON_PTLSODPARK_1_968_05_05_01_01.xsd",
    "ON_PTLSODVZD_1_968_04_05_01_01.xsd",
    "ON_PTLSPOSMO_1_968_06_05_01_01.xsd",
    "ON_PTLSPRMO_1_968_02_05_01_01.xsd",
    "ON_PTLSSOBTS_1_968_01_05_01_01.xsd",
    "ON_PTLSVIPTS_1_968_03_05_01_01.xsd",
    "ON_REESUSLDMS_1_881_00_05_01_01.xsd",
    "ON_SCHFDOPPOK_1_995_02_05_01_05.xsd",
    "ON_SCHFDOPPR_1_995_01_05_01_05.xsd",
    "ON_SFAKT_1_897_01_05_01_03.xsd",
    "ON_SFAKT_1_897_01_05_02_01.xsd",
    "ON_SODSD_1_999_02_01_01_01.xsd",
    "ON_SOGLK_1_999_03_01_01_01.xsd",
    "ON_SOPVEDGO_1_974_02_05_01_01.xsd",
    "ON_SOPVEDGP_1_974_03_05_01_01.xsd",
    "ON_SOPVEDPER_1_974_01_05_01_01.xsd",
    "ON_SPISDMS_1_882_00_05_01_02.xsd",
    "ON_TRNACLGROT_1_973_01_05_01_01.xsd",
    "ON_TRNACLGRPO_1_973_05_05_01_01.xsd",
    "ON_TRNACLPPRIN_1_973_02_05_01_01.xsd",
    "ON_TRNACLPVYN_1_973_06_05_01_01.xsd",
    "ON_TRNPEREADR_1_973_03_05_01_01.xsd",
    "ON_TRNPUDGO_1_973_08_05_01_01.xsd",
    "ON_TRNPUDPER_1_973_07_05_01_02.xsd",
    "ON_TRNVPRFINSOST_1_973_28_05_01_02.xsd",
    "ON_TRNVPRFINSOSTPODTV_1_973_29_05_01_01.xsd",
    "ON_TRNVPRGO_1_973_21_05_01_01.xsd",
    "ON_TRNVPRGRPO_1_973_26_05_01_01.xsd",
    "ON_TRNVPRPDTV_1_973_24_05_01_01.xsd",
    "ON_TRNVPRPEREADR_1_973_23_05_01_01.xsd",
    "ON_TRNVPRPRV_1_973_22_05_01_01.xsd",
    "ON_TRNVPRVGP_1_973_27_05_01_01.xsd",
    "ON_TRNVPRZAMEN_1_973_25_05_01_01.xsd",
    "ON_TRNZAMEN_1_973_04_05_01_01.xsd",
    "ON_ZAKAZNAR_1_975_01_05_01_01.xsd",
    "ON_ZAKAZNARPOD_1_975_03_05_01_01.xsd",
    "ON_ZAKAZNARSOG_1_975_02_05_01_01.xsd",
    "ON_ZAKAZNARVOZ_1_975_04_05_01_01.xsd",
    "ON_ZAKZVGO_1_969_01_05_01_01.xsd",
    "ON_ZAKZVPER_1_969_02_05_01_02.xsd",
]

def main():
    for xsd_name in xsd_names:
        xsd_schema_filename = xsd_directory + xsd_name

        print("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
        print(f"Схема: {xsd_name}\n")

        matches = re.findall("^((ON|DP)_[A-Z0-9]*)_.*", xsd_name)
        file_id_prefix = matches[0][0]

        # Загрузка XSD-схемы
        xsd_schema = xmlschema.XMLSchema(xsd_schema_filename)

        # Генерация XML-документа
        xml_root = generate_xml_from_xsd(xsd_schema)

        # Преобразование в строку
        rough_string = ElementTree.tostring(xml_root, encoding='utf-8')
        reparsed = minidom.parseString(rough_string)
        xml_str = reparsed.toprettyxml(indent="    ", encoding='windows-1251')
        decoded = xml_str.decode('cp1251')

        # Вывод
        print(decoded)

        # Валидация
        try:
            xsd_schema.validate(decoded)
        except BaseException as err:
            print(err, file=sys.stderr)
            sys.exit(1)

        # Сохранение в файл
        with open('output_xml/output.xml', 'wb', ) as f:
            f.write(xml_str)


if __name__ == "__main__":
    main()
