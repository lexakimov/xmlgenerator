import random
import re
import sys

import rstr
import xmlschema
from faker import Faker
from lxml import etree
from xmlschema.validators import XsdComplexType, XsdAtomicRestriction, XsdTotalDigitsFacet, XsdElement, \
    XsdGroup, XsdFractionDigitsFacet, XsdLengthFacet, XsdMaxLengthFacet, XsdMinExclusiveFacet, XsdMinInclusiveFacet, \
    XsdMinLengthFacet, XsdAnyElement, XsdAtomicBuiltin

from util_random import ascii_string, id_file

id_file_str = ""

fake = Faker('ru_RU')

# Генерация значений на основе ограничений XSD
def generate_value(xsd_type, target_name):
    # Тип не определен
    if xsd_type is None:
        raise RuntimeError(f"xsd_type is None. Target name: {target_name}")

    # Если есть перечисление, выбираем случайное значение из него
    enumeration = getattr(xsd_type, 'enumeration', None)
    if enumeration is not None:
        return random.choice(enumeration)

    if isinstance(xsd_type, XsdComplexType):
        return None

    if isinstance(xsd_type, XsdAtomicBuiltin):
        local_name = xsd_type.local_name
        if local_name == 'gYear':
            return random.randint(2000, 2050)
        else:
            # python_type = xsd_type.python_type
            # pattern = python_type.pattern
            # return rstr.xeger(pattern)
            raise RuntimeError(local_name)

    # -----------------------------------------------------------------------------------------------------------------
    # Проверяем базовый тип
    base_type = getattr(xsd_type, 'base_type', None)

    # невозможный кейс (только если попался комплексный тип)
    if base_type is None:
        raise RuntimeError(f"base_type is None. Target name: {target_name}")

    # -----------------------------------------------------------------------------------------------------------------
    # Выясняем ограничения

    allow_empty = getattr(xsd_type, 'allow_empty', None) # True | False TODO

    min_length = getattr(xsd_type, 'min_length', None) # None | int
    max_length = getattr(xsd_type, 'max_length', None) # None | int

    min_value = getattr(xsd_type, 'min_value', None) # None | int
    max_value = getattr(xsd_type, 'max_value', None) # None

    total_digits = None
    fraction_digits = None

    patterns = getattr(xsd_type, 'patterns', None) # None | XsdPatternFacets

    validators = getattr(xsd_type, 'validators', None) # () | [XsdEnumerationFacets(...)]
    for validator in validators:
        if isinstance(validator, XsdMinExclusiveFacet):
            min_value = validator.value
        elif isinstance(validator, XsdMinInclusiveFacet):
            min_value = validator.value
        elif isinstance(validator, XsdLengthFacet):
            pass
        elif isinstance(validator, XsdMinLengthFacet):
            min_length = validator.value # то же самое
        elif isinstance(validator, XsdMaxLengthFacet):
            max_length = validator.value # то же самое
        elif isinstance(validator, XsdTotalDigitsFacet):
            total_digits = validator.value
        elif isinstance(validator, XsdFractionDigitsFacet):
            fraction_digits = validator.value
        else:
            raise RuntimeError(f"Unhandled validator: {validator}")

    min_length = min_length or -1
    max_length = max_length or -1

    # -----------------------------------------------------------------------------------------------------------------
    target_type = base_type.local_name # string | integer | decimal | CCРФТип | СПДУЛТип

    # Генерация строки
    if target_type == 'string':

        if target_name == 'ИдФайл' or target_name == 'FileID':
            return id_file_str
        if target_name == 'ВерсПрог':
            return "Xsd2Xml 0.1.0"

        if re.search('Фамилия', target_name, re.IGNORECASE):
            return fake.last_name_male()
        if re.search('Имя', target_name, re.IGNORECASE) and not re.search('ИмяДопПакета', target_name, re.IGNORECASE):
            return fake.first_name_male()
        if re.search('Отчество', target_name, re.IGNORECASE):
            return fake.middle_name_male()

        if xsd_type.local_name != 'ДатаТип':
            if re.search('АдрТекст', target_name, re.IGNORECASE): return fake.address()
            if re.search('Район', target_name, re.IGNORECASE): return fake.administrative_unit()
            if re.search('Дом', target_name, re.IGNORECASE): return fake.building_number()
            if re.search('Город', target_name, re.IGNORECASE): return fake.city_name()
            if re.search('Индекс', target_name, re.IGNORECASE): return fake.postcode()
            if re.search('НаимОрг', target_name, re.IGNORECASE): return fake.company()
            if re.search('НаимБанк', target_name, re.IGNORECASE): return fake.bank()
            if re.search('Тлф', target_name, re.IGNORECASE): return fake.phone_number()
            if re.search('ИННФЛ', target_name, re.IGNORECASE): return fake.individuals_inn()
            if re.search('ИННЮЛ', target_name, re.IGNORECASE): return fake.businesses_inn()
            if re.search('ОГРНИП', target_name, re.IGNORECASE): return fake.individuals_ogrn()
            if re.search('ОГРН', target_name, re.IGNORECASE): return fake.businesses_ogrn()
            if re.search('КПП', target_name, re.IGNORECASE): return fake.kpp()
            if re.search('СНИЛС', target_name, re.IGNORECASE):
                snils = fake.snils()
                return f"{snils[:3]}-{snils[3:6]}-{snils[6:9]} {snils[9:]}"

        if isinstance(xsd_type, XsdAtomicRestriction):
            if patterns is not None:
                # Генерация строки по regex
                random_pattern = random.choice(xsd_type.patterns)
                xeger = rstr.xeger(random_pattern.attrib['value'])
                xeger = re.sub(r'\s', ' ', xeger)
                if max_length is not None and len(xeger) > max_length:
                    print(
                        f"Possible mistake in schema: {target_name} generated value '{xeger}' can't be longer than {max_length}",
                        file=sys.stderr)
                if min_length is not None and len(xeger) < min_length:
                    print(
                        f"Possible mistake in schema: {target_name} generated value '{xeger}' can't be shorter than {min_length}",
                        file=sys.stderr)
                return xeger

        # Иначе генерируем случайную строку
        return ascii_string(min_length, max_length)

    if target_type == 'integer':
        # Генерация целого числа
        if total_digits:
            min_value = 10 ** (total_digits - 1)
            max_value = (10 ** total_digits) - 1
        rnd_int = random.randint(min_value, max_value)
        return str(rnd_int)

    if target_type == 'decimal':
        # Генерация десятичного числа
        if total_digits:
            if fraction_digits:
                integer_digits = total_digits - fraction_digits
                integer_part = random.randint(10 ** (integer_digits - 1), (10 ** integer_digits) - 1)
                fractional_part = random.randint(0, (10 ** fraction_digits) - 1)
                return f"{integer_part}.{fractional_part:0{fraction_digits}}"
            else:
                min_value = 10 ** (total_digits - 1)
                max_value = (10 ** total_digits) - 1

        rnd_int = random.randint(min_value, max_value)
        return f"{int(rnd_int / 100)}.{rnd_int % 100:02}"

    if isinstance(base_type, XsdAtomicRestriction):
        patterns = getattr(base_type, 'patterns', None)
        if patterns is not None:
            # Генерация строки по regex
            random_pattern = random.choice(base_type.patterns)
            return rstr.xeger(random_pattern.attrib['value'])

    else:
        raise RuntimeError(f"Can't generate value - unhandled type. Target name: {target_name}")


# Рекурсивно добавляем элементы и атрибуты в соответствии с XSD-схемой
def add_elements(xml_element: etree.Element, xsd_element):
    xsd_element_type = getattr(xsd_element, 'type', None)

    # Добавляем атрибуты, если они есть
    attributes = getattr(xsd_element, 'attributes', dict())
    if len(attributes) > 0 and xsd_element_type.local_name != 'anyType':
        for attr_name, attr in attributes.items():
            attr_value = generate_value(attr.type, attr_name)
            if attr_value is not None:
                xml_element.set(attr_name, str(attr_value))

    # Обрабатываем дочерние элементы
    if isinstance(xsd_element, XsdElement):
        if isinstance(xsd_element_type, XsdAtomicRestriction):
            text = generate_value(xsd_element_type, xsd_element.name)
            xml_element.text = text
            return
        elif isinstance(xsd_element_type, XsdComplexType):
            xsd_element_type_content = xsd_element_type.content
            if isinstance(xsd_element_type_content, XsdGroup):
                add_elements(xml_element, xsd_element_type_content)
            else:
                raise RuntimeError()
        else:
            raise RuntimeError()

    elif isinstance(xsd_element, XsdGroup):
        model = xsd_element.model
        if model == 'sequence':
            for xsd_child_element_type in xsd_element:
                if isinstance(xsd_child_element_type, XsdElement):
                    xml_child_element = etree.SubElement(xml_element, xsd_child_element_type.name)
                elif isinstance(xsd_child_element_type, XsdGroup):
                    xml_child_element = xml_element
                elif isinstance(xsd_child_element_type, XsdAnyElement):
                    xml_child_element = etree.SubElement(xml_element, "Any")
                    # return
                    # pass
                else:
                    raise RuntimeError(xsd_child_element_type)
                add_elements(xml_child_element, xsd_child_element_type)
            return
        elif model == 'choice':
            xsd_child_element_type = random.choice(xsd_element)
            xml_child_element = etree.SubElement(xml_element, xsd_child_element_type.name)
            add_elements(xml_child_element, xsd_child_element_type)
            return
        else:
            raise RuntimeError()

    elif isinstance(xsd_element, XsdAnyElement):
        pass

    else:
        raise RuntimeError()

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

# TODO
# def validate_xml_with_schematron(xml_file, schematron_file):
#     # Загрузка Schematron-схемы
#     with open(schematron_file, 'rb') as f:
#         schematron_doc = etree.parse(f)
#
#     # Преобразование Schematron в XSLT
#     schematron = etree.Schematron(schematron_doc)
#
#     # Загрузка XML-документа
#     with open(xml_file, 'rb') as f:
#         xml_doc = etree.parse(f)
#
#     # Валидация XML-документа
#     is_valid = schematron.validate(xml_doc)
#
#     if is_valid:
#         print("XML документ валиден по Schematron-схеме.")
#     else:
#         print("XML документ не валиден по Schematron-схеме.")
#         print(schematron.error_log)

# Пример использования
# validate_xml_with_schematron('example.xml', 'schema.sch')
