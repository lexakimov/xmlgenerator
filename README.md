# XML Generator

![PyPI - Version](https://img.shields.io/pypi/v/xmlgenerator)
[![PyPI - Downloads](https://img.shields.io/pypi/dm/xmlgenerator)](https://pypistats.org/packages/xmlgenerator)
[![DeepWiki](https://img.shields.io/badge/DeepWiki-lexakimov%2Fxmlgenerator-blue.svg?logo=data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAACwAAAAyCAYAAAAnWDnqAAAAAXNSR0IArs4c6QAAA05JREFUaEPtmUtyEzEQhtWTQyQLHNak2AB7ZnyXZMEjXMGeK/AIi+QuHrMnbChYY7MIh8g01fJoopFb0uhhEqqcbWTp06/uv1saEDv4O3n3dV60RfP947Mm9/SQc0ICFQgzfc4CYZoTPAswgSJCCUJUnAAoRHOAUOcATwbmVLWdGoH//PB8mnKqScAhsD0kYP3j/Yt5LPQe2KvcXmGvRHcDnpxfL2zOYJ1mFwrryWTz0advv1Ut4CJgf5uhDuDj5eUcAUoahrdY/56ebRWeraTjMt/00Sh3UDtjgHtQNHwcRGOC98BJEAEymycmYcWwOprTgcB6VZ5JK5TAJ+fXGLBm3FDAmn6oPPjR4rKCAoJCal2eAiQp2x0vxTPB3ALO2CRkwmDy5WohzBDwSEFKRwPbknEggCPB/imwrycgxX2NzoMCHhPkDwqYMr9tRcP5qNrMZHkVnOjRMWwLCcr8ohBVb1OMjxLwGCvjTikrsBOiA6fNyCrm8V1rP93iVPpwaE+gO0SsWmPiXB+jikdf6SizrT5qKasx5j8ABbHpFTx+vFXp9EnYQmLx02h1QTTrl6eDqxLnGjporxl3NL3agEvXdT0WmEost648sQOYAeJS9Q7bfUVoMGnjo4AZdUMQku50McDcMWcBPvr0SzbTAFDfvJqwLzgxwATnCgnp4wDl6Aa+Ax283gghmj+vj7feE2KBBRMW3FzOpLOADl0Isb5587h/U4gGvkt5v60Z1VLG8BhYjbzRwyQZemwAd6cCR5/XFWLYZRIMpX39AR0tjaGGiGzLVyhse5C9RKC6ai42ppWPKiBagOvaYk8lO7DajerabOZP46Lby5wKjw1HCRx7p9sVMOWGzb/vA1hwiWc6jm3MvQDTogQkiqIhJV0nBQBTU+3okKCFDy9WwferkHjtxib7t3xIUQtHxnIwtx4mpg26/HfwVNVDb4oI9RHmx5WGelRVlrtiw43zboCLaxv46AZeB3IlTkwouebTr1y2NjSpHz68WNFjHvupy3q8TFn3Hos2IAk4Ju5dCo8B3wP7VPr/FGaKiG+T+v+TQqIrOqMTL1VdWV1DdmcbO8KXBz6esmYWYKPwDL5b5FA1a0hwapHiom0r/cKaoqr+27/XcrS5UwSMbQAAAABJRU5ErkJggg==)](https://deepwiki.com/lexakimov/xmlgenerator)

- [Русский 🇷🇺](README_RU.md)
- [English 🇺🇸](README.md)

Generates XML documents based on XSD schemas with the ability to customize data through a YAML configuration file.

Simplifies the creation of test or demonstration XML data for complex schemas.

## Features

- Generation of XML documents based on XSD schemas
- Customization of generated values via a YAML configuration file
- Validation of generated documents
- Command-line interface for convenient use

## Installation

### Installation via pip

```bash
pip install xmlgenerator
```

### Install executable file manually (linux)

```bash
curl -LO https://github.com/lexakimov/xmlgenerator/releases/download/v0.5.3/xmlgenerator-linux-amd64
chmod +x xmlgenerator-linux-amd64
sudo install xmlgenerator-linux-amd64 /usr/local/bin/xmlgenerator
```

### Install shell completions (linux)

```shell
# also available: zsh, tcsh
xmlgenerator -C bash | sudo tee /etc/bash_completion.d/xmlgenerator
```

## Usage

The generator command is `xmlgenerator`

**Flags and parameters:**

```
usage: xmlgenerator [-h] [-c <config.yml>] [-o <output.xml>] [-p] [-v <validation>] [-ff] [-e <encoding>] [-s <seed>]
                    [-d] [-V] [-C <shell>]
                    xsd [xsd ...]

Generates XML documents from XSD schemas

positional arguments:
  xsd                            paths to xsd schema(s) or directory with xsd schemas

options:
  -h, --help                     show this help message and exit
  -c, --config <config.yml>      pass a YAML configuration file
  -o, --output <output.xml>      save the output to a directory or file
  -p, --pretty                   prettify the output XML
  -v, --validation <validation>  validate the generated XML document (none, schema, schematron; default: schema)
  -ff, --fail-fast               terminate execution on a validation error (default: true)
  -e, --encoding <encoding>      the output XML encoding (utf-8, windows-1251; default: utf-8)
  -s, --seed <seed>              set the randomization seed
  -d, --debug                    enable debug mode
  -V, --version                  show the current version
  -C, --completion <shell>       print a shell completion script (bash, zsh, tcsh)
```

**Examples:**

- Generate XML from a single schema and print to console:
   ```bash
   xmlgenerator path/to/your/schema.xsd
   ```

- Generate XML from all schemas in a directory and save to the `output` folder using a configuration file:
   ```bash
   xmlgenerator -c config.yml -o output/ path/to/schemas/
   ```

- Generate XML from a specific schema, save to a file with pretty formatting and windows-1251 encoding:
   ```bash
   xmlgenerator -o output.xml -p -e windows-1251 path/to/your/schema.xsd
   ```

- Generate XML with validation disabled:
   ```bash
   xmlgenerator -v none path/to/your/schema.xsd
   ```

## Configuration

The generator can be configured using a YAML file passed via the `-c` or `--config` option.

Description and examples of configuration are in [CONFIGURATION](./CONFIGURATION.md).

## Validation

Generated XML documents are checked for conformance against the schema used for generation.
By default, validation against the source XSD schema is used.

If a document does not conform to the schema, execution stops immediately.
This behavior can be disabled using the flag `-ff false` or `--fail-fast false`.

To disable validation, use the flag `-v none` or `--validation none`.

## Contribution

Contributions are welcome! Please open an issue or submit a pull request on GitHub.

### Build from source

1. **Clone the repository:**
   ```bash
   git clone https://github.com/lexakimov/xmlgenerator.git
   cd xmlgenerator
   ```

2. **Create and activate a virtual environment (recommended):**
   ```bash
   python -m venv .venv
   ```
    * **For Linux/macOS:**
      ```bash
      source .venv/bin/activate
      ```
    * **For Windows (Command Prompt/PowerShell):**
      ```bash
      .\.venv\Scripts\activate
      ```

3. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

4.1. **Install the package:**

   ```bash
   pip install .
   # or for development mode (code changes will be immediately reflected)
   # pip install -e .
   ```

4.2. **Otherwise, build single executable:**

   ```bash
   python build_native.py
   ```

### Project Structure

- `xmlgenerator/` - main project code
- `tests/` - tests

### Running Tests

```bash
pytest
```

---

## License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.

## Contacts

For any questions or issues, please contact [lex.akimov23@gmail.com].

You can also create an [Issue on GitHub](https://github.com/lexakimov/xmlgenerator/issues) to report bugs or suggest
improvements.
