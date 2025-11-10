import logging
import sys

from xmlschema import XMLSchemaValidationError

logger = logging.getLogger(__name__)


class XmlValidator:
    def __init__(self, post_validate: str, ignore_errors: bool):
        self.ignore_errors = ignore_errors
        match post_validate:
            case 'none':
                self.validation_func = self._skip_validation
            case 'schema':
                self.validation_func = self._validate_with_schema
            case 'schematron':
                self.validation_func = self._validate_with_schematron
            case _:
                raise ValueError(f"Unknown validation mode: {post_validate}")
        logger.debug("post validation: %s, ignore errors: %s", post_validate, ignore_errors)

    def validate(self, xsd_schema, document):
        self.validation_func(xsd_schema, document)

    def _skip_validation(self, *_):
        logger.debug("validation skipped (mode 'none')")

    def _validate_with_schema(self, xsd_schema, document):
        logger.debug("validate generated xml with xsd schema")
        try:
            xsd_schema.validate(document)
        except XMLSchemaValidationError as err:
            print(err, file=sys.stderr)
            if not self.ignore_errors:
                sys.exit(1)

    def _validate_with_schematron(self, xsd_schema, document):
        logger.debug("validate generated xml with xsd schematron")
        raise RuntimeError("not yet implemented")

# TODO валидация по Schematron
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
