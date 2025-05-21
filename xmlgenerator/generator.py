import logging
from dataclasses import dataclass, replace
from decimal import Decimal
from typing import Optional, Any, Callable, Dict

from lxml import etree
from xmlschema.validators import XsdComplexType, XsdAtomicRestriction, XsdTotalDigitsFacet, XsdElement, \
    XsdGroup, XsdFractionDigitsFacet, XsdLengthFacet, XsdMaxLengthFacet, XsdMinExclusiveFacet, XsdMinInclusiveFacet, \
    XsdMinLengthFacet, XsdAnyElement, XsdAtomicBuiltin, XsdEnumerationFacets, XsdMaxExclusiveFacet, XsdMaxInclusiveFacet

from xmlgenerator.configuration import GeneratorConfig
from xmlgenerator.randomization import Randomizer
from xmlgenerator.substitution import Substitutor

logger = logging.getLogger(__name__)


@dataclass
class TypeConstraints:
    min_length: Optional[int] = None
    max_length: Optional[int] = None
    min_value: Optional[Any] = None
    max_value: Optional[Any] = None
    total_digits: Optional[int] = None
    fraction_digits: Optional[int] = None
    patterns: Optional[list] = None
    rand_config: Optional[Any] = None


class XmlGenerator:
    def __init__(self, randomizer: Randomizer, substitutor: Substitutor):
        self.randomizer = randomizer
        self.substitutor = substitutor
        self.generators: Dict[str, Callable[[TypeConstraints], str]] = {
            # primitive
            'boolean': self._generate_boolean,
            'string': self._generate_string,
            'decimal': self._generate_decimal,
            'float': self._generate_float,
            'double': self._generate_double,
            'duration': self._generate_duration,
            'dateTime': self._generate_datetime,
            'date': self._generate_date,
            'time': self._generate_time,
            'gYearMonth': self._generate_gyearmonth,
            'gYear': self._generate_gyear,
            'gMonthDay': self._generate_gmonthday,
            'gDay': self._generate_gday,
            'gMonth': self._generate_gmonth,
            'hexBinary': self._generate_hex_binary,
            'base64Binary': self._generate_base64_binary,
            'anyURI': self._generate_any_uri,
            'QName': self._generate_qname,
            'NOTATION': self._generate_notation,

            # derived - from decimal
            'byte': self._generate_byte,
            'short': self._generate_short,
            'int': self._generate_int,
            'integer': self._generate_integer,
            'long': self._generate_long,

            'unsignedByte': self._generate_unsigned_byte,
            'unsignedShort': self._generate_unsigned_short,
            'unsignedInt': self._generate_unsigned_int,
            'unsignedLong': self._generate_unsigned_long,

            'positiveInteger': self._generate_positive_integer,
            'negativeInteger': self._generate_negative_integer,
            'nonPositiveInteger': self._generate_non_positive_integer,
            'nonNegativeInteger': self._generate_non_negative_integer,

            # derived - from string
            'language': self._generate_language,
            'Name': self._generate_name,
            'NCName': self._generate_nc_name,
            'normalizedString': self._generate_normalized_string,
            'token': self._generate_token,
            'ID': self._generate_id,
            'IDREF': self._generate_idref,
            'IDREFS': self._generate_idrefs,
            'ENTITY': self._generate_entity,
            'ENTITIES': self._generate_entities,
            'NMTOKEN': self._generate_nmtoken,
            'NMTOKENS': self._generate_nmtokens,
        }

    def generate_xml(self, xsd_schema, local_config: GeneratorConfig) -> etree.Element:
        logger.debug('generate xml document...')
        ns_map = {None if k == '' else k: v for k, v in xsd_schema.namespaces.items() if v != ''}
        xsd_root_element = xsd_schema.root_elements[0]
        xml_root_element = etree.Element(xsd_root_element.name, nsmap=ns_map)
        xml_tree = etree.ElementTree(xml_root_element)
        self._add_elements(xml_tree, xml_root_element, xsd_root_element, local_config)
        return xml_root_element

    def _add_elements(self, xml_tree, xml_element, xsd_element, local_config: GeneratorConfig) -> None:
        rand_config = local_config.randomization
        min_occurs_conf = rand_config.min_occurs
        max_occurs_conf = rand_config.max_occurs

        # Process child elements --------------------------------------------------------------------------------------
        if isinstance(xsd_element, XsdElement):
            element_xpath = xml_tree.getpath(xml_element)
            logger.debug('element: %s [created]', element_xpath)

            xsd_element_type = getattr(xsd_element, 'type', None)

            # Add attributes if they are
            attributes = getattr(xsd_element, 'attributes', dict())
            if len(attributes) > 0 and xsd_element_type.local_name != 'anyType':
                for attr_name, attr in attributes.items():
                    logger.debug('element: %s; attribute: "%s" - [processing]', element_xpath, attr_name)
                    use = attr.use  # optional | required | prohibited
                    if use == 'prohibited':
                        logger.debug('element: %s; attribute: "%s" - [skipped]', element_xpath, attr_name)
                        continue
                    elif use == 'optional':
                        if self.randomizer.random() > rand_config.probability:
                            logger.debug('element: %s; attribute: "%s" - [skipped]', element_xpath, attr_name)
                            continue

                    attr_value = self._generate_value(attr.type, attr_name, local_config)
                    if attr_value is not None:
                        xml_element.set(attr_name, str(attr_value))
                        logger.debug('element: %s; attribute: "%s" = "%s"', element_xpath, attr_name, attr_value)

            if isinstance(xsd_element_type, XsdAtomicBuiltin):
                text = self._generate_value(xsd_element_type, xsd_element.name, local_config)
                xml_element.text = text
                logger.debug('element: %s = "%s"', element_xpath, text)

            elif isinstance(xsd_element_type, XsdAtomicRestriction):
                text = self._generate_value(xsd_element_type, xsd_element.name, local_config)
                xml_element.text = text
                logger.debug('element: %s = "%s"', element_xpath, text)

            elif isinstance(xsd_element_type, XsdComplexType):
                xsd_element_type_content = xsd_element_type.content
                if isinstance(xsd_element_type_content, XsdGroup):
                    self._add_elements(xml_tree, xml_element, xsd_element_type_content, local_config)
                else:
                    raise RuntimeError()

            else:
                raise RuntimeError()

        elif isinstance(xsd_element, XsdGroup):
            model = xsd_element.model

            min_occurs = getattr(xsd_element, 'min_occurs', None)
            max_occurs = getattr(xsd_element, 'max_occurs', None)
            min_occurs, max_occurs = merge_constraints(
                schema_min=min_occurs,
                schema_max=max_occurs,
                config_min=min_occurs_conf,
                config_max=max_occurs_conf
            )
            if max_occurs is None:
                max_occurs = 10
            group_occurs = self.randomizer.integer(min_occurs, max_occurs)
            logger.debug('add %s (random between %s and %s) groups of type "%s"',
                         group_occurs, min_occurs, max_occurs, model)

            if model == 'all':
                for _ in range(group_occurs):
                    xsd_group_content = xsd_element.content
                    for xsd_child_element_type in xsd_group_content:

                        min_occurs = getattr(xsd_child_element_type, 'min_occurs', None)
                        max_occurs = getattr(xsd_child_element_type, 'max_occurs', None)
                        min_occurs, max_occurs = merge_constraints(
                            schema_min=min_occurs,
                            schema_max=max_occurs,
                            config_min=min_occurs_conf,
                            config_max=max_occurs_conf
                        )
                        if max_occurs is None:
                            max_occurs = 10
                        element_occurs = self.randomizer.integer(min_occurs, max_occurs)
                        logger.debug('element_occurs: %s (random between %s and %s)', element_occurs, min_occurs,
                                     max_occurs)

                        for _ in range(element_occurs):
                            xml_child_element = etree.SubElement(xml_element, xsd_child_element_type.name)
                            self._add_elements(xml_tree, xml_child_element, xsd_child_element_type, local_config)

            elif model == 'sequence':
                for _ in range(group_occurs):
                    xsd_group_content = xsd_element.content
                    for xsd_child_element_type in xsd_group_content:
                        if isinstance(xsd_child_element_type, XsdElement):

                            min_occurs = getattr(xsd_child_element_type, 'min_occurs', None)
                            max_occurs = getattr(xsd_child_element_type, 'max_occurs', None)
                            min_occurs, max_occurs = merge_constraints(
                                schema_min=min_occurs,
                                schema_max=max_occurs,
                                config_min=min_occurs_conf,
                                config_max=max_occurs_conf
                            )
                            if max_occurs is None:
                                max_occurs = 10
                            element_occurs = self.randomizer.integer(min_occurs, max_occurs)
                            logger.debug('element_occurs: %s (random between %s and %s)', element_occurs, min_occurs,
                                         max_occurs)

                            for _ in range(element_occurs):
                                xml_child_element = etree.SubElement(xml_element, xsd_child_element_type.name)
                                self._add_elements(xml_tree, xml_child_element, xsd_child_element_type, local_config)

                        elif isinstance(xsd_child_element_type, XsdGroup):
                            xml_child_element = xml_element
                            self._add_elements(xml_tree, xml_child_element, xsd_child_element_type, local_config)

                        elif isinstance(xsd_child_element_type, XsdAnyElement):
                            xml_child_element = etree.SubElement(xml_element, "Any")
                            self._add_elements(xml_tree, xml_child_element, xsd_child_element_type, local_config)

                        else:
                            raise RuntimeError(xsd_child_element_type)

            elif model == 'choice':
                for _ in range(group_occurs):
                    xsd_child_element_type = self.randomizer.any(xsd_element)

                    min_occurs = getattr(xsd_child_element_type, 'min_occurs', None)
                    max_occurs = getattr(xsd_child_element_type, 'max_occurs', None)
                    min_occurs, max_occurs = merge_constraints(
                        schema_min=min_occurs,
                        schema_max=max_occurs,
                        config_min=min_occurs_conf,
                        config_max=max_occurs_conf
                    )
                    if max_occurs is None:
                        max_occurs = 10
                    element_occurs = self.randomizer.integer(min_occurs, max_occurs)
                    logger.debug('element_occurs: %s (random between %s and %s)', element_occurs, min_occurs,
                                 max_occurs)

                    for _ in range(element_occurs):
                        xml_child_element = etree.SubElement(xml_element, xsd_child_element_type.name)
                        self._add_elements(xml_tree, xml_child_element, xsd_child_element_type, local_config)

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

        # -------------------------------------------------------------------------------------------------------------
        # Ищем переопределение значения в конфигурации
        value_override = local_config.value_override
        is_found, overridden_value = self.substitutor.substitute_value(target_name, value_override.items())
        if is_found:
            logger.debug('value resolved: "%s"', overridden_value)
            return overridden_value

        # -------------------------------------------------------------------------------------------------------------
        # If there is an enumeration, select a random value from it
        enumeration = getattr(xsd_type, 'enumeration', None)
        if enumeration is not None:
            random_enum = self.randomizer.any(enumeration)
            logger.debug('use random value from enumeration: "%s" %s', random_enum, enumeration)
            return str(random_enum)

        # -------------------------------------------------------------------------------------------------------------
        # Генерируем значения для стандартных типов и типов с ограничениями
        if isinstance(xsd_type, XsdAtomicBuiltin) or isinstance(xsd_type, XsdAtomicRestriction):
            constraints = extract_type_constraints(xsd_type, local_config)
            type_id = xsd_type.id or xsd_type.base_type.id or xsd_type.root_type.id
            logger.debug('generate value for type: "%s"', type_id)
            generator = self.generators.get(type_id)
            if generator is None:
                raise RuntimeError(f"Generator not found for type: {type_id}")
            generated_value = generator(constraints)

            logger.debug('value generated: "%s"', generated_value)
            return generated_value

        # -------------------------------------------------------------------------------------------------------------
        # Проверяем базовый тип
        base_type = getattr(xsd_type, 'base_type', None)

        # невозможный кейс (только если попался комплексный тип)
        if base_type is None:
            raise RuntimeError(f"base_type is None. Target name: {target_name}")

        raise RuntimeError(f"Can't generate value - unhandled type. Target name: {target_name}")

    # noinspection PyUnusedLocal
    def _generate_boolean(self, constraints: TypeConstraints):
        return self.randomizer.any(['true', 'false'])

    def _generate_string(self, constraints: TypeConstraints):
        if constraints.patterns is not None:
            # Генерация строки по regex
            random_enum = self.randomizer.any(constraints.patterns)
            random_pattern = random_enum.attrib['value']
            return self.randomizer.regex(random_pattern)

        # Иначе генерируем случайную строку
        return self.randomizer.ascii_string(constraints.min_length, constraints.max_length)

    def _generate_decimal(self, constraints: TypeConstraints):
        rand_config = constraints.rand_config
        min_value = constraints.min_value
        max_value = constraints.max_value
        total_digits = constraints.total_digits
        fraction_digits = constraints.fraction_digits

        if fraction_digits is None:
            fraction_digits = self.randomizer.integer(1, 3)

        if fraction_digits > 4:
            fraction_digits = self.randomizer.integer(1, 4)

        if total_digits is None:
            total_digits = 10 + fraction_digits

        if total_digits > 10:
            total_digits = self.randomizer.integer(6, total_digits - 2)

        integer_digits = total_digits - fraction_digits

        # negative bound
        digit_min = -(10 ** integer_digits - 1)
        # positive bound
        digit_max = 10 ** integer_digits - 1
        logger.debug("integer digits: %s; digit_min: %s; digit_max: %s", integer_digits, digit_min, digit_max)

        logger.debug('bounds before adjust: min_value: %4s; max_value: %4s', min_value, max_value)
        config_min = rand_config.min_inclusive
        config_max = rand_config.max_inclusive
        effective_min, effective_max \
            = merge_constraints(digit_min, digit_max, min_value, max_value, config_min, config_max)
        logger.debug('bounds after  adjust: min_value: %4s; max_value: %4s', effective_min, effective_max)

        if fraction_digits == 0:
            random_int = self.randomizer.integer(effective_min, effective_max)
            return str(random_int)
        else:
            random_float = self.randomizer.float(effective_min, effective_max)
            return f"{random_float:.{fraction_digits}f}"

    def _generate_float(self, constraints: TypeConstraints):
        decimal_constraints = replace(constraints, fraction_digits=2)
        return self._generate_decimal(decimal_constraints)

    def _generate_double(self, constraints: TypeConstraints):
        decimal_constraints = replace(constraints, fraction_digits=2)
        return self._generate_decimal(decimal_constraints)

    def _generate_duration(self, constraints: TypeConstraints):
        raise RuntimeError("not yet implemented")

    # noinspection PyUnusedLocal
    def _generate_datetime(self, constraints: TypeConstraints):
        random_datetime = self.randomizer.random_datetime()
        formatted = random_datetime.isoformat()
        return formatted

    # noinspection PyUnusedLocal
    def _generate_date(self, constraints: TypeConstraints):
        random_date = self.randomizer.random_date()
        formatted = random_date.isoformat()
        return formatted

    # noinspection PyUnusedLocal
    def _generate_time(self, constraints: TypeConstraints):
        random_time = self.randomizer.random_time()
        formatted = random_time.isoformat()
        return formatted

    # noinspection PyUnusedLocal
    def _generate_gyearmonth(self, constraints: TypeConstraints):
        random_date = self.randomizer.random_date()
        formatted = random_date.strftime('%Y-%m')
        return formatted

    # noinspection PyUnusedLocal
    def _generate_gyear(self, constraints: TypeConstraints):
        return str(self.randomizer.integer(2000, 2050))

    # noinspection PyUnusedLocal
    def _generate_gmonthday(self, constraints: TypeConstraints):
        random_date = self.randomizer.random_date()
        formatted = random_date.strftime('--%m-%d')
        return formatted

    # noinspection PyUnusedLocal
    def _generate_gday(self, constraints: TypeConstraints):
        random_date = self.randomizer.random_date()
        formatted = random_date.strftime('---%d')
        return formatted

    # noinspection PyUnusedLocal
    def _generate_gmonth(self, constraints: TypeConstraints):
        random_date = self.randomizer.random_date()
        formatted = random_date.strftime('--%m--')
        return formatted

    def _generate_hex_binary(self, constraints: TypeConstraints):
        return self.randomizer.hex_string(constraints.min_length, constraints.max_length)

    # noinspection PyUnusedLocal
    def _generate_base64_binary(self, constraints: TypeConstraints):
        raise RuntimeError("not yet implemented")

    # noinspection PyUnusedLocal
    def _generate_any_uri(self, constraints: TypeConstraints):
        raise RuntimeError("not yet implemented")

    # noinspection PyUnusedLocal
    def _generate_qname(self, constraints: TypeConstraints):
        raise RuntimeError("not yet implemented")

    # noinspection PyUnusedLocal
    def _generate_notation(self, constraints: TypeConstraints):
        raise RuntimeError("not yet implemented")

    def _generate_byte(self, constraints: TypeConstraints):
        constraints = replace(constraints, fraction_digits=0)
        return self._generate_decimal(constraints)

    def _generate_short(self, constraints: TypeConstraints):
        constraints = replace(constraints, fraction_digits=0)
        return self._generate_decimal(constraints)

    def _generate_int(self, constraints: TypeConstraints):
        constraints = replace(constraints, fraction_digits=0)
        return self._generate_decimal(constraints)

    def _generate_integer(self, constraints: TypeConstraints):
        min_value = constraints.min_value if constraints.min_value is not None else -2147483648
        max_value = constraints.max_value if constraints.max_value is not None else 2147483647
        constraints = replace(constraints, min_value=min_value, max_value=max_value, fraction_digits=0)
        return self._generate_decimal(constraints)

    def _generate_long(self, constraints: TypeConstraints):
        constraints = replace(constraints, fraction_digits=0)
        return self._generate_decimal(constraints)

    def _generate_unsigned_byte(self, constraints: TypeConstraints):
        constraints = replace(constraints, fraction_digits=0)
        return self._generate_decimal(constraints)

    def _generate_unsigned_short(self, constraints: TypeConstraints):
        constraints = replace(constraints, fraction_digits=0)
        return self._generate_decimal(constraints)

    def _generate_unsigned_int(self, constraints: TypeConstraints):
        constraints = replace(constraints, fraction_digits=0)
        return self._generate_decimal(constraints)

    def _generate_unsigned_long(self, constraints: TypeConstraints):
        constraints = replace(constraints, fraction_digits=0)
        return self._generate_decimal(constraints)

    def _generate_positive_integer(self, constraints: TypeConstraints):
        min_value = constraints.min_value if constraints.min_value is not None else 1
        max_value = constraints.max_value if constraints.max_value is not None else 2 ** 31 - 1
        constraints = replace(constraints, min_value=min_value, max_value=max_value, fraction_digits=0)
        return self._generate_decimal(constraints)

    def _generate_negative_integer(self, constraints: TypeConstraints):
        min_value = constraints.min_value if constraints.min_value is not None else -2 ** 31
        max_value = constraints.max_value if constraints.max_value is not None else -1
        constraints = replace(constraints, min_value=min_value, max_value=max_value, fraction_digits=0)
        return self._generate_decimal(constraints)

    def _generate_non_positive_integer(self, constraints: TypeConstraints):
        min_value = constraints.min_value if constraints.min_value is not None else -2 ** 31
        max_value = constraints.max_value if constraints.max_value is not None else 0
        constraints = replace(constraints, min_value=min_value, max_value=max_value, fraction_digits=0)
        return self._generate_decimal(constraints)

    def _generate_non_negative_integer(self, constraints: TypeConstraints):
        min_value = constraints.min_value if constraints.min_value is not None else 0
        max_value = constraints.max_value if constraints.max_value is not None else 2 ** 31 - 1
        constraints = replace(constraints, min_value=min_value, max_value=max_value, fraction_digits=0)
        return self._generate_decimal(constraints)

    def _generate_language(self, constraints: TypeConstraints):
        raise RuntimeError('not yet implemented')

    def _generate_name(self, constraints: TypeConstraints):
        raise RuntimeError('not yet implemented')

    def _generate_nc_name(self, constraints: TypeConstraints):
        raise RuntimeError('not yet implemented')

    def _generate_normalized_string(self, constraints: TypeConstraints):
        raise RuntimeError('not yet implemented')

    def _generate_token(self, constraints: TypeConstraints):
        raise RuntimeError('not yet implemented')

    def _generate_id(self, constraints: TypeConstraints):
        raise RuntimeError('not yet implemented')

    def _generate_idref(self, constraints: TypeConstraints):
        raise RuntimeError('not yet implemented')

    def _generate_idrefs(self, constraints: TypeConstraints):
        raise RuntimeError('not yet implemented')

    def _generate_entity(self, constraints: TypeConstraints):
        raise RuntimeError('not yet implemented')

    def _generate_entities(self, constraints: TypeConstraints):
        raise RuntimeError('not yet implemented')

    def _generate_nmtoken(self, constraints: TypeConstraints):
        raise RuntimeError('not yet implemented')

    def _generate_nmtokens(self, constraints: TypeConstraints):
        raise RuntimeError('not yet implemented')


def extract_type_constraints(xsd_type, local_config: GeneratorConfig) -> TypeConstraints:
    min_length = getattr(xsd_type, 'min_length', None)
    max_length = getattr(xsd_type, 'max_length', None)
    min_value = getattr(xsd_type, 'min_value', None)
    max_value = getattr(xsd_type, 'max_value', None)
    total_digits = None
    fraction_digits = None
    patterns = getattr(xsd_type, 'patterns', None)
    validators = getattr(xsd_type, 'validators', None)
    for validator in validators:
        if isinstance(validator, XsdMinExclusiveFacet):
            min_value = validator.value
        elif isinstance(validator, XsdMinInclusiveFacet):
            min_value = validator.value
        elif isinstance(validator, XsdMaxExclusiveFacet):
            max_value = validator.value
        elif isinstance(validator, XsdMaxInclusiveFacet):
            max_value = validator.value
        elif isinstance(validator, XsdLengthFacet):
            min_length = validator.value
            max_length = validator.value
        elif isinstance(validator, XsdMinLengthFacet):
            min_length = validator.value
        elif isinstance(validator, XsdMaxLengthFacet):
            max_length = validator.value
        elif isinstance(validator, XsdTotalDigitsFacet):
            total_digits = validator.value
        elif isinstance(validator, XsdFractionDigitsFacet):
            fraction_digits = validator.value
        elif isinstance(validator, XsdEnumerationFacets):
            pass
        elif callable(validator):
            pass
        else:
            raise RuntimeError(f"Unhandled validator: {validator}")

    if isinstance(min_value, Decimal):
        min_value = float(min_value)
    if isinstance(max_value, Decimal):
        max_value = float(max_value)

    rand_config = local_config.randomization

    logger.debug('bounds before adjust: min_length: %4s; max_length: %4s', min_length, max_length)
    min_length, max_length = merge_constraints(
        schema_min=min_length,
        schema_max=max_length,
        config_min=rand_config.min_length,
        config_max=rand_config.max_length
    )
    logger.debug('bounds after  adjust: min_length: %4s; max_length: %4s', min_length, max_length)

    return TypeConstraints(
        min_length=min_length,
        max_length=max_length,
        min_value=min_value,
        max_value=max_value,
        total_digits=total_digits,
        fraction_digits=fraction_digits,
        patterns=patterns,
        rand_config=rand_config
    )


def merge_constraints(digit_min=None, digit_max=None, schema_min=None, schema_max=None, config_min=None, config_max=None):
    logger.debug(
        "merge numeric constraints: "
        "digit_min: %s, digit_max: %s, schema_min: %s, schema_max: %s, config_min: %s, config_max: %s",
        digit_min, digit_max, schema_min, schema_max, config_min, config_max)

    # За основу берем цифровые ограничения (они самые нестрогие)
    effective_min, effective_max = digit_min, digit_max

    # Применяем схемные ограничения
    if schema_min is not None:
        effective_min = max(effective_min, schema_min) if effective_min is not None else schema_min
    if schema_max is not None:
        effective_max = min(effective_max, schema_max) if effective_max is not None else schema_max

    # Применяем конфигурационные ограничения с проверкой на конфликт
    if config_min is not None:
        if effective_max is not None and config_min > effective_max:
            logger.warning("can't apply bound from configuration: config_min (%s) > effective_max (%s)",
                           config_min, effective_max)
        else:
            effective_min = max(effective_min, config_min) if effective_min is not None else config_min

    if config_max is not None:
        if effective_min is not None and config_max < effective_min:
            logger.warning("can't apply bound from configuration: config_max (%s) < effective_min (%s)",
                           config_max, effective_min)
        else:
            effective_max = min(effective_max, config_max) if effective_max is not None else config_max

    # Проверяем на конфликт
    if effective_min is not None and effective_max is not None and effective_min > effective_max:
        logger.warning("constrains conflict: effective_min (%s) > effective_max (%s). Swap values.",
                       effective_min, effective_max)
        effective_min, effective_max = effective_max, effective_min

    return effective_min, effective_max
