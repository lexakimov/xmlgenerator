# XML Generator

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

## CLI Usage

The main command to run the generator is `xmlgenerator`.

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

**Install shell completions:**

```shell
# also available: zsh, tcsh
xmlgenerator -C bash | sudo tee /etc/bash_completion.d/xmlgenerator
```

**Detailed CLI Usage:**

```
usage: xmlgenerator [-h] [-c <config.yml>] [-o <output.xml>] [-p] [-v <validation>] [-ff] [-e <encoding>]
                    [--seed <seed>] [-d] [-V]
                    xsd [xsd ...]

Generates XML documents from XSD schemas

positional arguments:
  xsd                            paths to xsd schema(s) or directory with xsd schemas

options:
  -h, --help                     show this help message and exit
  -c, --config <config.yml>      pass yaml configuration file
  -l, --locale <locale>          randomizer locale (default: en_US)
  -o, --output <output.xml>      save output to dir or file
  -p, --pretty                   prettify output XML
  -v, --validation <validation>  validate generated XML document (none, schema, schematron, default is schema)
  -ff, --fail-fast               terminate execution on validation error (default is true)
  -e, --encoding <encoding>      output XML encoding (utf-8, windows-1251, default is utf-8)
  -s, --seed <seed>              set randomization seed
  -d, --debug                    enable debug mode
  -V, --version                  shows current version
  -C, --completion <shell>       print shell completion script (bash, zsh, tcsh)
```

## Configuration

The generator can be configured using a YAML file passed via the `-c` or `--config` option.

**Configuration File Structure:**

```yaml
# Global settings (apply to all schemas)
global:

  # Regular expression to extract a substring from the source xsd schema filename.
  # The extracted substring can be used via the `source_extracted` function.
  # The regular expression must contain the group `extracted`.
  # Default value: `(?P<extracted>.*).(xsd|XSD)` (extracts the filename without extension).
  source_filename: ...

  # Filename template for saving the generated document.
  # Default value: `{{ source_extracted }}_{{ uuid }}` (xsd schema filename + random UUID)
  output_filename: ...

  # Random value generator settings
  randomization:
    # Probability of adding optional elements (0.0-1.0)
    # Default value: 0.5
    probability: 1
    # Limit for the minimal number of elements
    min_occurs: 0
    # Limit for the maximum number of elements
    max_occurs: 5
    # Minimum string length
    min_length: 5
    # Maximum string length
    max_length: 20
    # Minimum numeric value
    min_inclusive: 10
    # Maximum numeric value
    max_inclusive: 1000000

  # Override generated values for tags and attributes.
  # Key - string or regular expression to match the tag/attribute name.
  # Value - string with optional use of placeholders:
  # `{{ function }}` - substitutes the value provided by the predefined function.
  # `{{ function | modifier }}` - same, but with a modifier [ global | local ].
  # - `global` - a single value will be used along all generation.
  # - `local` - a single value will be used in context of current document.
  #
  # The list of available functions is below.
  # The order of entries matters; the first matching override will be selected.
  # Key matching is case-insensitive.
  value_override:
    name_regexp_1: "static value"
    name_regexp_2: "{{ function_call }}"
    "name_regexp_\d": "static-text-and-{{ function_call }}"
    name: "static-text-and-{{ function_call }}-{{ another_function_call }}"

# Extend/override global settings for specific files.
# Key - string or regular expression to match the xsd filename(s).
# The order of entries matters; the first matching override will be selected.
# Key matching is case-insensitive.
specific:
  # Each value can have the same set of parameters as the global section
  "SCHEM.*":
    # for schemas named "SCHEM.*", xml document names will only contain UUIDv4 + '.xml'
    output_filename: "{{ uuid }}"
    # Random value generator settings for schemas named "SCHEM.*"
    randomization:
      # for schemas named "SCHEM.*", the probability of adding optional elements will be 30%
      probability: 0.3
    value_override:
      # override the value set by the global configuration
      name_regexp_1: "static value"
      # reset overrides for tags/attributes containing 'name' set by the global configuration
      name:
```

Configuration Priority:

- specific settings
- global settings
- default settings

### Placeholder Functions

In the `value_override` sections, you can specify either a string value or special placeholders:

- `{{ function }}` - Substitutes the value provided by the predefined function.
- `{{ function | modifier }}` - Same, but with a modifier `[ global | local ]`, where:
    - `global`: The function will generate and use *the same single value* throughout the *entire generation process*
      for all documents.
    - `local`: The function will generate and use *the same single value* within the scope of *a single generated
      document*.
    - No modifier: A new value is generated each time the function is called.

**List of Placeholder Functions:**

| Function                           | Description                                                                                                |
|------------------------------------|------------------------------------------------------------------------------------------------------------|
| `source_filename`                  | Filename of the source xsd schema with extension (e.g., `schema.xsd`)                                      |
| `source_extracted`                 | String extracted from the source xsd filename using the regex specified in `source_filename_extract_regex` |
| `output_filename`                  | String described by the `output_filename_template` configuration parameter                                 |
| `uuid`                             | Random UUIDv4                                                                                              |
| `regex("pattern")`                 | Random string value matching the specified regular expression                                              |
| `any('A', "B", C)`                 | Random value from enumeration                                                                              |
| `number(A, B)`                     | Random number between A and B                                                                              |
| `date("2010-01-01", "2025-01-01")` | Random date within the specified range                                                                     |
| `last_name`                        | Last Name                                                                                                  |
| `first_name`                       | First Name                                                                                                 |
| `middle_name`                      | Middle Name                                                                                                |
| `address_text`                     | Address                                                                                                    |
| `administrative_unit`              | Administrative Unit (e.g., District)                                                                       |
| `house_number`                     | House Number                                                                                               |
| `city_name`                        | City Name                                                                                                  |
| `postcode`                         | Postal Code                                                                                                |
| `company_name`                     | Company Name                                                                                               |
| `bank_name`                        | Bank Name                                                                                                  |
| `phone_number`                     | Phone Number                                                                                               |
| `inn_fl`                           | Individual Taxpayer Number (Physical Person)                                                               |
| `inn_ul`                           | Taxpayer Identification Number (Legal Entity)                                                              |
| `ogrn_ip`                          | Primary State Registration Number (Individual Entrepreneur)                                                |
| `ogrn_fl`                          | Primary State Registration Number (Physical Person)                                                        |
| `kpp`                              | Reason Code for Registration                                                                               |
| `snils_formatted`                  | SNILS (Personal Insurance Account Number) in the format `123-456-789 90`                                   |
| `email`                            | Random email address                                                                                       |

**Configuration Examples:**

```yaml
# TODO Add configuration examples.
```

---

## Validation

Generated XML documents are checked for conformance against the schema used for generation.
By default, validation against the source XSD schema is used.

If a document does not conform to the schema, execution stops immediately.
This behavior can be disabled using the flag `-ff false` or `--fail-fast false`.

To disable validation, use the flag `-v none` or `--validation none`.

## Contribution

Contributions are welcome! Please open an issue or submit a pull request on GitHub.

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
