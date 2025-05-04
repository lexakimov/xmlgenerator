import logging
from decimal import Decimal

from lxml import etree
from xmlschema.validators import XsdComplexType, XsdAtomicRestriction, XsdTotalDigitsFacet, XsdElement, \
    XsdGroup, XsdFractionDigitsFacet, XsdLengthFacet, XsdMaxLengthFacet, XsdMinExclusiveFacet, XsdMinInclusiveFacet, \
    XsdMinLengthFacet, XsdAnyElement, XsdAtomicBuiltin, XsdEnumerationFacets, XsdMaxExclusiveFacet, XsdMaxInclusiveFacet

from xmlgenerator.configuration import GeneratorConfig
from xmlgenerator.randomization import Randomizer
from xmlgenerator.substitution import Substitutor

logger = logging.getLogger(__name__)


class XmlGenerator:
    def __init__(self, randomizer: Randomizer, substitutor: Substitutor):
        self.randomizer = randomizer
        self.substitutor = substitutor

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
            # Выясняем ограничения
            min_length = getattr(xsd_type, 'min_length', None)  # None | int
            max_length = getattr(xsd_type, 'max_length', None)  # None | int

            min_value = getattr(xsd_type, 'min_value', None)  # None | int
            max_value = getattr(xsd_type, 'max_value', None)  # None

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

            type_id = xsd_type.id or xsd_type.base_type.id or xsd_type.root_type.id
            logger.debug('generate value for type: "%s"', type_id)

            match type_id:
                case 'boolean':
                    result = self._generate_boolean()
                case 'string':
                    result = self._generate_string(min_length, max_length, patterns)
                case 'integer':
                    result = self._generate_integer(min_value, max_value, total_digits)
                case 'decimal':
                    result = self._generate_decimal(rand_config, min_value, max_value, total_digits, fraction_digits)
                case 'float':
                    result = self._generate_float(rand_config, min_value, max_value)
                case 'double':
                    result = self._generate_double(rand_config, min_value, max_value)
                case 'duration':
                    result = self._generate_duration()
                case 'dateTime':
                    result = self._generate_datetime()
                case 'date':
                    result = self._generate_date()
                case 'time':
                    result = self._generate_time()
                case 'gYearMonth':
                    result = self._generate_gyearmonth()
                case 'gYear':
                    result = self._generate_gyear()
                case 'gMonthDay':
                    result = self._generate_gmonthday()
                case 'gDay':
                    result = self._generate_gday()
                case 'gMonth':
                    result = self._generate_gmonth()
                case 'hexBinary':
                    result = self._generate_hex_binary()
                case 'base64Binary':
                    result = self._generate_base64_binary()
                case 'anyURI':
                    result = self._generate_any_uri()
                case 'QName':
                    result = self._generate_qname()
                case 'NOTATION':
                    result = self._generate_notation()
                case _:
                    raise RuntimeError(type_id)
            generated_value = result
            logger.debug('value generated: "%s"', generated_value)
            return generated_value

        # -------------------------------------------------------------------------------------------------------------
        # Проверяем базовый тип
        base_type = getattr(xsd_type, 'base_type', None)

        # невозможный кейс (только если попался комплексный тип)
        if base_type is None:
            raise RuntimeError(f"base_type is None. Target name: {target_name}")

        raise RuntimeError(f"Can't generate value - unhandled type. Target name: {target_name}")

    def _generate_boolean(self):
        return self.randomizer.any(['true', 'false'])

    def _generate_string(self, min_length, max_length, patterns):
        if patterns is not None:
            # Генерация строки по regex
            random_enum = self.randomizer.any(patterns)
            random_pattern = random_enum.attrib['value']
            return self.randomizer.regex(random_pattern)

        # Иначе генерируем случайную строку
        return self.randomizer.ascii_string(min_length, max_length)

    def _generate_integer(self, min_value, max_value, total_digits):
        if total_digits:
            min_value = 10 ** (total_digits - 1)
            max_value = (10 ** total_digits) - 1
        rnd_int = self.randomizer.integer(min_value, max_value)
        return str(rnd_int)

    def _generate_decimal(self, rand_config, schema_min, schema_max, total_digits, fraction_digits):
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

        logger.debug('bounds before adjust: min_value: %4s; max_value: %4s', schema_min, schema_max)
        config_min = rand_config.min_inclusive
        config_max = rand_config.max_inclusive
        effective_min, effective_max \
            = merge_constraints(digit_min, digit_max, schema_min, schema_max, config_min, config_max)
        logger.debug('bounds after  adjust: min_value: %4s; max_value: %4s', effective_min, effective_max)

        random_float = self.randomizer.float(effective_min, effective_max)
        return f"{random_float:.{fraction_digits}f}"

    def _generate_float(self, rand_config, min_value, max_value):
        return self._generate_decimal(rand_config, min_value, max_value, None, 2)

    def _generate_double(self, rand_config, min_value, max_value):
        return self._generate_decimal(rand_config, min_value, max_value, None, 2)

    def _generate_duration(self):
        raise RuntimeError("not yet implemented")

    def _generate_datetime(self):
        random_datetime = self.randomizer.random_datetime()
        formatted = random_datetime.isoformat()
        return formatted

    def _generate_date(self):
        random_date = self.randomizer.random_date()
        formatted = random_date.isoformat()
        return formatted

    def _generate_time(self):
        random_time = self.randomizer.random_time()
        formatted = random_time.isoformat()
        return formatted

    def _generate_gyearmonth(self):
        random_date = self.randomizer.random_date()
        formatted = random_date.strftime('%Y-%m')
        return formatted

    def _generate_gyear(self):
        return str(self.randomizer.integer(2000, 2050))

    def _generate_gmonthday(self):
        random_date = self.randomizer.random_date()
        formatted = random_date.strftime('--%m-%d')
        return formatted

    def _generate_gday(self):
        random_date = self.randomizer.random_date()
        formatted = random_date.strftime('---%d')
        return formatted

    def _generate_gmonth(self):
        random_date = self.randomizer.random_date()
        formatted = random_date.strftime('--%m--')
        return formatted

    def _generate_hex_binary(self):
        raise RuntimeError("not yet implemented")

    def _generate_base64_binary(self):
        raise RuntimeError("not yet implemented")

    def _generate_any_uri(self):
        raise RuntimeError("not yet implemented")

    def _generate_qname(self):
        raise RuntimeError("not yet implemented")

    def _generate_notation(self):
        raise RuntimeError("not yet implemented")


def merge_constraints(digit_min=None, digit_max=None, schema_min=None, schema_max=None, config_min=None,
                      config_max=None):
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
