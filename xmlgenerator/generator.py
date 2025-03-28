import re
import sys

import rstr
import xmlschema
from lxml import etree
from xmlschema.validators import XsdComplexType, XsdAtomicRestriction, XsdTotalDigitsFacet, XsdElement, \
    XsdGroup, XsdFractionDigitsFacet, XsdLengthFacet, XsdMaxLengthFacet, XsdMinExclusiveFacet, XsdMinInclusiveFacet, \
    XsdMinLengthFacet, XsdAnyElement, XsdAtomicBuiltin, XsdEnumerationFacets

from xmlgenerator.configuration import GeneratorConfig
from xmlgenerator.randomization import Randomizer
from xmlgenerator.substitution import Substitutor


class XmlGenerator:
    def __init__(self, randomizer: Randomizer, substitutor: Substitutor):
        self.randomizer = randomizer
        self.substitutor = substitutor

    def generate_xml(self, xsd_schema: xmlschema.XMLSchema, local_config: GeneratorConfig) -> etree.Element:
        xsd_root_element = xsd_schema.root_elements[0]
        xml_root_element = etree.Element(xsd_root_element.name)
        self._add_elements(xml_root_element, xsd_root_element, local_config)
        return xml_root_element

    def _add_elements(self, xml_element: etree.Element, xsd_element, local_config: GeneratorConfig) -> None:
        rnd = self.randomizer.rnd

        xsd_element_type = getattr(xsd_element, 'type', None)

        # Add attributes if they are
        attributes = getattr(xsd_element, 'attributes', dict())
        if len(attributes) > 0 and xsd_element_type.local_name != 'anyType':
            for attr_name, attr in attributes.items():
                use = attr.use  # optional | required
                if use == 'optional':
                    if rnd.random() > local_config.randomization.probability:
                        # skip optional attribute
                        continue

                attr_value = self._generate_value(attr.type, attr_name, local_config)
                if attr_value is not None:
                    xml_element.set(attr_name, str(attr_value))

        # Find out the restrictions -----------------------------------------------------------------------------------
        min_occurs = getattr(xsd_element, 'min_occurs', None)  # None | int
        max_occurs = getattr(xsd_element, 'max_occurs', None)  # None | int
        effective_min_occurs = getattr(xsd_element, 'effective_min_occurs', None)  # None | int
        effective_max_occurs = getattr(xsd_element, 'effective_max_occurs', None)  # None | int

        # Process child elements --------------------------------------------------------------------------------------
        if isinstance(xsd_element, XsdElement):
            if isinstance(xsd_element_type, XsdAtomicRestriction):
                text = self._generate_value(xsd_element_type, xsd_element.name, local_config)
                xml_element.text = text
                return
            elif isinstance(xsd_element_type, XsdComplexType):
                xsd_element_type_content = xsd_element_type.content
                if isinstance(xsd_element_type_content, XsdGroup):
                    self._add_elements(xml_element, xsd_element_type_content, local_config)
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
                    self._add_elements(xml_child_element, xsd_child_element_type, local_config)
                return
            elif model == 'choice':
                xsd_child_element_type = rnd.choice(xsd_element)
                xml_child_element = etree.SubElement(xml_element, xsd_child_element_type.name)
                self._add_elements(xml_child_element, xsd_child_element_type, local_config)
                return
            else:
                raise RuntimeError()

        elif isinstance(xsd_element, XsdAnyElement):
            # для any не добавляем никаких дочерних тегов и атрибутов
            pass

        else:
            raise RuntimeError()

    def _generate_value(self, xsd_type, target_name, local_config: GeneratorConfig) -> str | None:
        if xsd_type is None:
            raise RuntimeError(f"xsd_type is None. Target name: {target_name}")

        if isinstance(xsd_type, XsdComplexType):
            return None

        rnd = self.randomizer.rnd

        # -------------------------------------------------------------------------------------------------------------
        # Выясняем ограничения

        # TODO
        #  decimal  allow_empty: True
        #  integer  allow_empty: True
        #  string   allow_empty: False
        #  string   allow_empty: True
        allow_empty = getattr(xsd_type, 'allow_empty', None)  # True | False

        min_length = getattr(xsd_type, 'min_length', None)  # None | int
        max_length = getattr(xsd_type, 'max_length', None)  # None | int

        min_value = getattr(xsd_type, 'min_value', None)  # None | int
        max_value = getattr(xsd_type, 'max_value', None)  # None

        total_digits = None
        fraction_digits = None
        enumeration = None

        patterns = getattr(xsd_type, 'patterns', None)  # None | XsdPatternFacets

        validators = getattr(xsd_type, 'validators', None)  # () | [XsdEnumerationFacets(...)]
        for validator in validators:
            if isinstance(validator, XsdMinExclusiveFacet):
                min_value = validator.value
            elif isinstance(validator, XsdMinInclusiveFacet):
                min_value = validator.value
            elif isinstance(validator, XsdLengthFacet):
                min_length = validator.value  # то же самое
                max_length = validator.value  # то же самое
            elif isinstance(validator, XsdMinLengthFacet):
                min_length = validator.value  # то же самое
            elif isinstance(validator, XsdMaxLengthFacet):
                max_length = validator.value  # то же самое
            elif isinstance(validator, XsdTotalDigitsFacet):
                total_digits = validator.value
            elif isinstance(validator, XsdFractionDigitsFacet):
                fraction_digits = validator.value
            elif isinstance(validator, XsdEnumerationFacets):
                enumeration = validator.enumeration
            else:
                raise RuntimeError(f"Unhandled validator: {validator}")

        min_length = min_length or -1
        max_length = max_length or -1

        # -------------------------------------------------------------------------------------------------------------
        # Ищем переопределение значения в конфигурации

        overwordings = local_config.value_override
        is_found, value_override = self.substitutor.substitute_value(target_name, overwordings.items())
        if is_found:
            return value_override

        # -------------------------------------------------------------------------------------------------------------
        # If there is an enumeration, select a random value from it

        if enumeration is not None:
            return rnd.choice(enumeration)

        # -------------------------------------------------------------------------------------------------------------\
        # Генерируем значения для стандартных типов

        if isinstance(xsd_type, XsdAtomicBuiltin):
            local_name = xsd_type.local_name
            match local_name:
                case 'string':
                    return self._generate_string(xsd_type, target_name, None, None, None)
                case 'boolean':
                    return self._generate_boolean()
                case 'float':
                    return self._generate_float()
                case 'double':
                    return self._generate_double()
                case 'decimal':
                    return self._generate_decimal()
                case 'duration':
                    return self._generate_duration()
                case 'dateTime':
                    return self._generate_datetime()
                case 'time':
                    return self._generate_time()
                case 'date':
                    return self._generate_date()
                case 'gYearMonth':
                    return self._generate_gyearmonth()
                case 'gYear':
                    return self._generate_gyear()
                case 'gMonthDay':
                    return self._generate_gmonthday()
                case 'gDay':
                    return self._generate_gday()
                case 'gMonth':
                    return self._generate_gmonth()
                case 'hexBinary':
                    return self._generate_hex_binary()
                case 'base64Binary':
                    return self._generate_base64_binary()
                case 'anyURI':
                    return self._generate_any_uri()
                case 'QName':
                    return self._generate_qname()
                case 'NOTATION':
                    return self._generate_notation()
                case _:
                    raise RuntimeError()

        # -------------------------------------------------------------------------------------------------------------
        # Проверяем базовый тип
        base_type = getattr(xsd_type, 'base_type', None)

        # невозможный кейс (только если попался комплексный тип)
        if base_type is None:
            raise RuntimeError(f"base_type is None. Target name: {target_name}")

        # -------------------------------------------------------------------------------------------------------------
        target_type = base_type.local_name  # string | integer | decimal | CCРФТип | СПДУЛТип

        # Генерация строки
        if target_type == 'string':
            return self._generate_string(xsd_type, target_name, patterns, min_length, max_length)

        if target_type == 'integer':
            # Генерация целого числа
            if total_digits:
                min_value = 10 ** (total_digits - 1)
                max_value = (10 ** total_digits) - 1
            rnd_int = rnd.randint(min_value, max_value)
            return str(rnd_int)

        if target_type == 'decimal':
            # Генерация десятичного числа
            if total_digits:
                if fraction_digits:
                    integer_digits = total_digits - fraction_digits
                    integer_part = rnd.randint(10 ** (integer_digits - 1), (10 ** integer_digits) - 1)
                    fractional_part = rnd.randint(0, (10 ** fraction_digits) - 1)
                    return f"{integer_part}.{fractional_part:0{fraction_digits}}"
                else:
                    min_value = 10 ** (total_digits - 1)
                    max_value = (10 ** total_digits) - 1

            rnd_int = rnd.randint(min_value, max_value)
            return f"{int(rnd_int / 100)}.{rnd_int % 100:02}"

        if isinstance(base_type, XsdAtomicRestriction) and patterns is not None:
            # Генерация строки по regex
            random_pattern = rnd.choice(base_type.patterns)
            return rstr.xeger(random_pattern.attrib['value'])

        else:
            raise RuntimeError(f"Can't generate value - unhandled type. Target name: {target_name}")


    def _generate_string(self, xsd_type, target_name, patterns, min_length, max_length):
        rnd = self.randomizer.rnd
        if patterns is not None:
            # Генерация строки по regex
            random_pattern = rnd.choice(xsd_type.patterns)
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
        return self.randomizer.ascii_string(min_length, max_length)

    def _generate_boolean(self):
        rnd = self.randomizer.rnd
        return rnd.choice(['true', 'false'])

    def _generate_gyear(self):
        rnd = self.randomizer.rnd
        return rnd.randint(2000, 2050)
