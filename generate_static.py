import random
import re
import sys

import rstr
import xmlschema
from lxml import etree
from russian_names import RussianNames
from xmlschema.validators import XsdComplexType, XsdAtomicRestriction, XsdTotalDigitsFacet, XsdAnyElement, XsdElement, \
    XsdGroup

from util_random import inn_fl, inn_ul, ogrn, ogrn_ip, kpp, snils, ascii_string, id_file

id_file_str = ""


# Генерация значений на основе ограничений XSD
def generate_value(xsd_type, target_name):
    # Тип не определен
    if xsd_type is None: raise RuntimeError(f"xsd_type is None. Target name: {target_name}")

    if isinstance(xsd_type, XsdComplexType):
        return None

    # Если есть перечисление, выбираем случайное значение из него
    if hasattr(xsd_type, 'enumeration') and xsd_type.enumeration is not None:
        return random.choice(xsd_type.enumeration)

    # Проверяем базовый тип
    base_type = getattr(xsd_type, 'base_type', None)
    if base_type is None: raise RuntimeError(f"base_type is None. Target name: {target_name}")

    total_digits = None
    for validator in xsd_type.validators:
        if isinstance(validator, XsdTotalDigitsFacet):
            total_digits = validator.value

    if base_type.local_name == 'string':
        # Генерация строки
        if hasattr(xsd_type, 'enumeration') and xsd_type.enumeration is not None:
            # Если есть перечисление, выбираем случайное значение из него
            return random.choice(xsd_type.enumeration)
        else:

            if target_name == 'ИдФайл' or target_name == 'FileID':
                return id_file_str
            if target_name == 'ВерсПрог':
                return "Python XML generator 1.0"

            if re.search('Фамилия', target_name, re.IGNORECASE):
                return RussianNames(name=False, surname=True, patronymic=False, gender=1).get_person()
            if (re.search('Имя', target_name, re.IGNORECASE)
                    and not re.search('ИмяДопПакета', target_name, re.IGNORECASE)):
                return RussianNames(name=True, surname=False, patronymic=False, gender=1).get_person()
            if re.search('Отчество', target_name, re.IGNORECASE):
                return RussianNames(name=False, surname=False, patronymic=True, gender=1).get_person()

            if xsd_type.local_name != 'ДатаТип':
                if re.search('ИННФЛ', target_name, re.IGNORECASE): return inn_fl()
                if re.search('ИННЮЛ', target_name, re.IGNORECASE): return inn_ul()
                if re.search('ОГРНИП', target_name, re.IGNORECASE): return ogrn_ip()
                if re.search('ОГРН', target_name, re.IGNORECASE): return ogrn()
                if re.search('КПП', target_name, re.IGNORECASE): return kpp()
                if re.search('СНИЛС', target_name, re.IGNORECASE): return snils()

            if isinstance(xsd_type, XsdAtomicRestriction):
                if hasattr(xsd_type, 'patterns') and xsd_type.patterns is not None:
                    # Генерация строки по regex
                    random_pattern = random.choice(xsd_type.patterns)
                    xeger = rstr.xeger(random_pattern.attrib['value'])
                    xeger = re.sub(r'\s', ' ', xeger)
                    return xeger

            # Иначе генерируем случайную строку
            min_length = xsd_type.min_length or -1
            max_length = xsd_type.max_length or -1
            return ascii_string(min_length, max_length)
    elif base_type.local_name == 'integer':
        # Генерация целого числа

        if total_digits:
            min_value = 10 ** (total_digits - 1)
            max_value = (10 ** total_digits) - 1
        else:
            min_value = getattr(xsd_type, 'min_inclusive', 0)
            max_value = getattr(xsd_type, 'max_inclusive', 10000)

        return str(random.randint(min_value, max_value))
    elif base_type.local_name == 'decimal':
        # Генерация десятичного числа

        if total_digits:
            min_value = 10 ** (total_digits - 1 - 1)
            max_value = (10 ** (total_digits - 1)) - 1
        else:
            min_value = getattr(xsd_type, 'min_inclusive', 0)
            max_value = getattr(xsd_type, 'max_inclusive', 10000)

        rnd_int = int(random.uniform(min_value, max_value))
        return f"{int(rnd_int / 100)}.{rnd_int % 100}"

    elif base_type.local_name == 'boolean':
        # Генерация булевого значения
        return random.choice([True, False])

    elif isinstance(base_type, XsdAtomicRestriction):
        if hasattr(base_type, 'patterns') and base_type.patterns is not None:
            # Генерация строки по regex
            random_pattern = random.choice(base_type.patterns)
            return rstr.xeger(random_pattern.attrib['value'])
    else:
        raise RuntimeError(f"Can't generate value - unhandled type. Target name: {target_name}")


# Рекурсивно добавляем элементы и атрибуты в соответствии с XSD-схемой
def add_elements(xml_element: etree.Element, xsd_element: XsdElement):
    # Добавляем атрибуты, если они есть
    if hasattr(xsd_element, 'attributes'):
        for attr_name, attr in xsd_element.attributes.items():
            # Генерация значения атрибута на основе его типа
            attr_value = generate_value(attr.type, attr_name)
            if attr_value is not None:
                xml_element.set(attr_name, str(attr_value))

    # Обрабатываем дочерние элементы
    if hasattr(xsd_element, 'type') or (hasattr(xsd_element, 'model') and xsd_element.model == 'choice'):

        if isinstance(xsd_element, XsdAnyElement):
            return

        if hasattr(xsd_element, 'type'):
            if hasattr(xsd_element.type, 'content'):
                xsd_type_content_child = xsd_element.type.content
            elif hasattr(xsd_element, 'name') and xsd_element.name is not None:
                # Генерация значения элемента на основе его типа
                element_value = generate_value(xsd_element.type, xsd_element.name)
                xml_element.text = element_value
                return
        else:
            xsd_type_content_child = xsd_element

        if isinstance(xsd_type_content_child, XsdElement):
            for xsd_child in xsd_type_content_child:
                if isinstance(xsd_child, XsdElement):
                    # Если это элемент, создаем его и рекурсивно добавляем дочерние элементы
                    xml_child = etree.SubElement(xml_element, xsd_child.name)
                    if hasattr(xsd_child, 'type'):
                        # Генерация значения элемента на основе его типа
                        element_value = generate_value(xsd_child.type, xsd_child.name)
                        xml_child.text = element_value
                    add_elements(xml_child, xsd_child)

        elif isinstance(xsd_type_content_child, XsdGroup):

            if xsd_type_content_child.model == 'sequence':
                for xsd_child_element in xsd_type_content_child:
                    if (not hasattr(xsd_child_element, 'model') or xsd_child_element.model != 'choice') and (
                            hasattr(xsd_child_element, 'name') and xsd_child_element.name is not None):
                        group_child_element = etree.SubElement(xml_element, xsd_child_element.name)
                    else:
                        group_child_element = xml_element

                    add_elements(group_child_element, xsd_child_element)

            elif xsd_type_content_child.model == 'choice':
                xsd_child_element = random.choice(xsd_type_content_child)
                if isinstance(xsd_child_element, XsdElement):
                    group_child_element = etree.SubElement(xml_element, xsd_child_element.name)
                    if hasattr(xsd_child_element, 'type'):
                        # Генерация значения элемента на основе его типа
                        element_value = generate_value(xsd_child_element.type, xsd_child_element.name)
                        group_child_element.text = element_value
                    add_elements(group_child_element, xsd_child_element)

            else: raise RuntimeError(xsd_type_content_child)

        else: raise RuntimeError(xsd_type_content_child)
    else:
        # Генерация значения элемента на основе его типа
        element_value = generate_value(xsd_element.type, xsd_element.name)
        xml_element.text = element_value

# Создание XML-документа на основе XSD-схемы
def generate_xml_from_xsd(xsd_schema):
    # Получаем корневой элемент схемы
    xsd_root_element = xsd_schema.root_elements[0]
    # Создаем корневой элемент XML документа
    xml_root_element = etree.Element(xsd_root_element.name)
    # Начинаем с корневого элемента схемы
    add_elements(xml_root_element, xsd_root_element)
    return xml_root_element


file = '/home/akimov/desktop/wb/wb-edi/edi-doc-api/src/main/resources/schemas/fns/ON_AKTREZRABP_1_971_01_01_00_02.xsd'

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
    # "ON_AKTREZRABP_1_971_01_01_00_02.xsd", ----
    # "ON_AKTREZRABZ_1_971_02_01_00_01.xsd", ----
    "ON_AKTSVEROTP_1_972_01_05_01_01.xsd",
    "ON_AKTSVERPOL_1_972_02_05_01_01.xsd",
    "ON_CONSGRPO_1_965_05_05_01_01.xsd",
    "ON_CONSIZM_1_965_03_05_01_01.xsd",
    "ON_CONSIZMPDTV_1_965_04_05_01_01.xsd",
    "ON_CONSOTPR_1_965_01_05_01_01.xsd",
    "ON_CONSPRV_1_965_02_05_01_01.xsd",
    "ON_CONSPRVYD_1_965_06_05_01_01.xsd",
    "ON_DOGDOC_1_999_01_01_01_02.xsd",
    # "ON_DOGFRAKHTEL_1_976_01_05_01_01.xsd", ----
    "ON_DOGFRASHCH_1_976_02_05_01_01.xsd",
    "ON_DOGMPOTPR_1_966_01_05_01_01.xsd",
    "ON_DOGMPPRV_1_966_02_05_01_01.xsd",
    "ON_DOGMPSOGLS_1_964_04_05_01_01.xsd",
    "ON_DOGMPSOGLS_1_966_04_05_01_01.xsd",
    "ON_DOGMPSOGLSH_1_966_03_05_01_01.xsd",
    "ON_DOGVTRGO_1_964_01_05_01_01.xsd",
    "ON_DOGVTRPRV_1_964_02_05_01_02.xsd",
    "ON_DOGVTRSOGLSH_1_964_03_05_01_02.xsd",
    # "ON_DOPLKNPOK_1_908_01_05_01_04.xsd", ----
    # "ON_DOPLKNPOK_1_908_01_05_02_01.xsd", ----
    # "ON_DOPLKNPROD_1_909_01_05_01_05.xsd", ----
    # "ON_DOPLKNPROD_1_909_01_05_02_01.xsd", ----
    # "ON_DOPLKNPROD_1_909_01_05_04_01.xsd", ----
    "ON_DORVEDGP_1_963_03_05_01_01.xsd",
    "ON_DORVEDIZM_1_963_02_05_01_01.xsd",
    "ON_DORVEDPRV_1_963_01_05_01_01.xsd",
    # "ON_GARANTLET_1_967_01_05_01_01.xsd", ----
    # "ON_GUCHSFAKT_1_910_01_05_01_03.xsd", ----
    # "ON_GUCHSFAKT_1_910_01_05_02_01.xsd", ----
    # "ON_KNPOK_1_898_01_05_01_04.xsd", ----
    # "ON_KNPOK_1_898_01_05_02_01.xsd", ----
    # "ON_KNPROD_1_899_01_05_01_05.xsd", ----
    # "ON_KNPROD_1_899_01_05_02_01.xsd", ----
    # "ON_KNPROD_1_899_01_05_04_01.xsd", ----
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
    # "ON_REESUSLDMS_1_881_00_05_01_01.xsd", ----
    "ON_SCHFDOPPOK_1_995_02_05_01_05.xsd",
    "ON_SCHFDOPPR_1_995_01_05_01_05.xsd",
    "ON_SFAKT_1_897_01_05_01_03.xsd",
    "ON_SFAKT_1_897_01_05_02_01.xsd",
    "ON_SODSD_1_999_02_01_01_01.xsd",
    "ON_SOGLK_1_999_03_01_01_01.xsd",
    "ON_SOPVEDGO_1_974_02_05_01_01.xsd",
    "ON_SOPVEDGP_1_974_03_05_01_01.xsd",
    "ON_SOPVEDPER_1_974_01_05_01_01.xsd",
    # "ON_SPISDMS_1_882_00_05_01_02.xsd", ----
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
    # "ON_ZAKZVGO_1_969_01_05_01_01.xsd", ----
    "ON_ZAKZVPER_1_969_02_05_01_02.xsd",
]

xsd_names_debug = [
    "DP_IAKTPRM_1_987_00_05_01_02.xsd",]

def main():
    for xsd_name in xsd_names:
    # for xsd_name in xsd_names_debug:
        xsd_schema_filename = xsd_directory + xsd_name

        print("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
        print(f"Схема: {xsd_name}\n")

        # извлекаем префикс
        matches = re.findall("^((ON|DP)_[A-Z0-9]*)_.*", xsd_name)
        file_id_prefix = matches[0][0]
        global id_file_str
        id_file_str = id_file(file_id_prefix)

        # Загрузка XSD-схемы
        xsd_schema = xmlschema.XMLSchema(xsd_schema_filename)

        # Генерация XML-документа
        xml_root = generate_xml_from_xsd(xsd_schema)

        # Преобразование в строку
        xml_str = etree.tostring(xml_root, encoding='windows-1251', pretty_print=True)

        # Вывод
        decoded = xml_str.decode('cp1251')
        print(decoded)

        # Валидация
        try:
            xsd_schema.validate(decoded)
        except BaseException as err:
            print(err, file=sys.stderr)
            sys.exit(1)

        # Сохранение в файл
        # with open(f'output_xml/{id_file_str}.xml', 'wb', ) as f:
        #     f.write(xml_str)


if __name__ == "__main__":
    main()
