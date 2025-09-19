import pytest

import xmlgenerator.validation as validation
from xmlgenerator.validation import XmlValidator


class DummySchema:
    def __init__(self, exc):
        self._exc = exc

    def validate(self, document):
        if self._exc:
            raise self._exc


def test_validator_exits_on_validation_error(monkeypatch):
    class DummyError(Exception):
        pass

    monkeypatch.setattr(validation, "XMLSchemaValidationError", DummyError)

    validator = XmlValidator('schema', ignore_errors=False)
    schema = DummySchema(DummyError("boom"))

    with pytest.raises(SystemExit):
        validator.validate(schema, "<xml/>")


def test_validator_ignores_validation_error(monkeypatch):
    class DummyError(Exception):
        pass

    monkeypatch.setattr(validation, "XMLSchemaValidationError", DummyError)

    validator = XmlValidator('schema', ignore_errors=True)
    schema = DummySchema(DummyError("boom"))

    validator.validate(schema, "<xml/>")


def test_validator_skips_validation_when_disabled():
    validator = XmlValidator('none', ignore_errors=False)
    schema = DummySchema(Exception("should not raise"))

    validator.validate(schema, "<xml/>")
