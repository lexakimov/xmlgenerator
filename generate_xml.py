#!/usr/bin/python3

import random
import re
import sys
from argparse import ArgumentParser, HelpFormatter
from pathlib import Path

import rstr
import xmlschema
from lxml import etree
from xmlschema.validators import XsdComplexType, XsdAtomicRestriction, XsdTotalDigitsFacet, XsdElement, \
    XsdGroup, XsdFractionDigitsFacet, XsdLengthFacet, XsdMaxLengthFacet, XsdMinExclusiveFacet, XsdMinInclusiveFacet, \
    XsdMinLengthFacet, XsdAnyElement, XsdAtomicBuiltin

from cofiguration import load_config
from randomization import ascii_string
from substitution import get_value_override, init_id_file

global config
global config_for_file

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

    # TODO
    #  decimal  allow_empty: True
    #  integer  allow_empty: True
    #  string   allow_empty: False
    #  string   allow_empty: True
    allow_empty = getattr(xsd_type, 'allow_empty', None) # True | False

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
            min_length = validator.value # то же самое
            max_length = validator.value # то же самое
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

        overwordings = config.global_.value_override
        if config_for_file and config_for_file.value_override:
            overwordings = overwordings.copy()
            overwordings.update(config_for_file.value_override)

        is_found, value_override = get_value_override(target_name, overwordings.items())
        if is_found:
            return value_override

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
            use = attr.use  # optional | required
            if use == 'optional':
                # TODO generate random
                #  if generated > config.global_.randomization.probability:
                #      return
                pass
            attr_value = generate_value(attr.type, attr_name)
            if attr_value is not None:
                xml_element.set(attr_name, str(attr_value))

    # -----------------------------------------------------------------------------------------------------------------
    # Выясняем ограничения
    min_occurs = getattr(xsd_element, 'min_occurs', None)  # None | int
    max_occurs = getattr(xsd_element, 'max_occurs', None)  # None | int
    effective_min_occurs = getattr(xsd_element, 'effective_min_occurs', None)  # None | int
    effective_max_occurs = getattr(xsd_element, 'effective_max_occurs', None)  # None | int

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
        # для any не добавляем никаких дочерних тегов и атрибутов
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


def parse_args():
    class MyParser(ArgumentParser):
        def error(self, message):
            sys.stderr.write('error: %s\n' % message)
            self.print_help()
            sys.exit(2)

    class CustomHelpFormatter(HelpFormatter):
        def __init__(self, prog):
            super().__init__(prog, max_help_position=36, width=120)

    # xsdxmlgen
    # xmlgen
    # genxml
    # genxmlfromxsd
    # xmlgenerator
    # xsdgenxml
    # xsdtoxml
    # xml_
    parser = MyParser(
        prog='xsd2xml-gen',
        description='Generates XML documents from XSD schemas',
        formatter_class=CustomHelpFormatter
        #epilog='Text at the bottom of help'
    )

    parser.add_argument("-s", "--schema", metavar="<source.xsd>", dest="source_xsd", required=True, help="select the source xsd schema")
    parser.add_argument("-o", "--output", metavar="<output.xml>", dest="output_xml", required=False, help="save result to file")
    parser.add_argument("-c", "--config", metavar="<config.yml>", dest="config_yaml", help="pass yaml configuration file")
    parser.add_argument("-d", "--debug", action="store_true", help="enable debug mode")
    parser.add_argument("-v", "--version", action='version', version='%(prog)s 0.1.0', help="shows current version")

    return parser.parse_args()

def main():
    # args = parse_args()

    global config
    global config_for_file
    config = load_config('config.yml')
    config_source = config.source
    config_output = config.output
    config_specific = config.specific

    print(f"Найдено схем: {len(config_source.file_names)}")
    Path(config_output.directory).mkdir(parents=True, exist_ok=True)

    for xsd_name in config_source.file_names:
        config_for_file = None
        for pattern, conf in config_specific.items():
            if re.match(pattern, xsd_name):
                config_for_file = conf
                break

        xsd_schema_filename = config_source.directory + xsd_name

        print(f"Схема: {xsd_name}")

        # извлекаем префикс
        id_file = init_id_file(xsd_name)

        # Загрузка XSD-схемы
        xsd_schema = xmlschema.XMLSchema(xsd_schema_filename, ) # loglevel='DEBUG'
        # Генерация XML-документа
        xml_root = generate_xml_from_xsd(xsd_schema)

        # Преобразование в строку
        xml_str = etree.tostring(xml_root, encoding=config_output.encoding, pretty_print=config_output.pretty)
        decoded = xml_str.decode('cp1251' if config_output.encoding == 'windows-1251' else config_output.encoding)

        # Вывод
        if config_output.log_result:
            print(decoded)

        # Валидация
        post_validate = config_output.post_validate
        fail_fast = config_output.fail_fast

        if post_validate == 'schema':
            try:
                xsd_schema.validate(decoded)
            except BaseException as err:
                print(err, file=sys.stderr)
                if fail_fast:
                    sys.exit(1)
        elif post_validate == 'schematron':
            raise RuntimeError("not yet implemented")

        # Сохранение в файл
        with open(f'{config_output.directory}/{id_file}.xml', 'wb') as f:
            f.write(xml_str)


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
