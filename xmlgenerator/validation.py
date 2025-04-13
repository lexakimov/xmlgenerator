import logging
import sys

from xmlschema import XMLSchemaValidationError

logger = logging.getLogger(__name__)


class XmlValidator:
    def __init__(self, post_validate: str, fail_fast: bool):
        self.fail_fast = fail_fast
        match post_validate:
            case 'schema':
                self.validation_func = self._validate_with_schema
            case 'schematron':
                self.validation_func = self._validate_with_schematron
        logger.debug("post validation: %s, fail fast: %s", post_validate, fail_fast)

    def validate(self, xsd_schema, document):
        self.validation_func(xsd_schema, document)

    def _validate_with_schema(self, xsd_schema, document):
        logger.debug("validate generated xml with xsd schema")
        try:
            xsd_schema.validate(document)
        except XMLSchemaValidationError as err:
            print(err, file=sys.stderr)
            if self.fail_fast:
                sys.exit(1)

    def _validate_with_schematron(self, xsd_schema, document):
        logger.debug("validate generated xml with xsd schematron")
        raise RuntimeError("not yet implemented")

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
