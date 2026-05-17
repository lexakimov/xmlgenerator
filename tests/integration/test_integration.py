import os
import sys
from unittest.mock import patch

import tests
from xmlschema import XMLSchema

from xmlgenerator.bootstrap import main

os.chdir(os.path.dirname(os.path.abspath(tests.__file__)))


class TestIntegration:

    def test_cli_generates_valid_reproducible_xml(self, tmp_path, capsys):
        schema_path = os.path.abspath("data/simple_schemas/schema_1.xsd")
        schema = XMLSchema(schema_path)

        first_name, first_xml = self._run_cli(schema_path, tmp_path / "first")
        second_name, second_xml = self._run_cli(schema_path, tmp_path / "second")

        assert first_name == second_name
        assert first_xml == second_xml
        schema.validate(first_xml)

        captured = capsys.readouterr()
        assert not captured.out
        assert not captured.err

    @staticmethod
    def _run_cli(schema_path, output_dir):
        test_args = [
            "xmlgenerator",
            "--seed",
            "integration-seed",
            "--output",
            str(output_dir),
            schema_path,
        ]
        with patch.object(sys, "argv", test_args):
            main()

        generated_files = sorted(output_dir.glob("*.xml"))
        assert len(generated_files) == 1
        generated_file = generated_files[0]
        return generated_file.name, generated_file.read_text(encoding="utf-8")
