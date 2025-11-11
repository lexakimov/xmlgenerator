# Configuring xmlgenerator

- [Русский 🇷🇺](./CONFIGURATION_RU.md)
- [English 🇺🇸](./CONFIGURATION.md)

This guide will help you understand how to configure `xmlgenerator`.

* [Basic usage](#basic-usage)
* [Configuration](#configuration)
  * [Customizing the generation of elements and values](#customizing-the-generation-of-elements-and-values)
    * [Probability of adding optional attributes](#probability-of-adding-optional-attributes)
    * [Limiting the number of elements](#limiting-the-number-of-elements)
    * [Limiting string length](#limiting-string-length)
    * [Limiting the range for numeric values](#limiting-the-range-for-numeric-values)
  * [Overriding values](#overriding-values)
    * [By tag/attribute name](#by-tagattribute-name)
    * [By regular expression for tag/attribute name](#by-regular-expression-for-tagattribute-name)
    * [Using built-in functions](#using-built-in-functions)
  * [Configuring output filenames](#configuring-output-filenames)
  * [Applying settings for groups of documents](#applying-settings-for-groups-of-documents)
    * [Configuration Example](#configuration-example)
  * [Appendix 1: Configuration File Structure](#appendix-1-configuration-file-structure)
  * [Appendix 2: Placeholder Functions](#appendix-2-placeholder-functions)


## Basic usage

Let's start with the simplest scenario: generating an XML document from a single XSD schema and printing the result to the console.

To demonstrate, we will use a simple [employee.xsd](examples/employee.xsd) schema, which describes an employee:

```xml
<?xml version="1.0" encoding="UTF-8"?>
<xs:schema xmlns:xs="http://www.w3.org/2001/XMLSchema">
    <xs:element name="employee">
        <xs:complexType>
            <xs:sequence>
                <xs:element name="firstName" type="xs:string"/>
                <xs:element name="lastName" type="xs:string"/>
                <xs:element name="patronymic" type="xs:string" minOccurs="0"/>
                <xs:element name="email" type="xs:string"/>
                <xs:element name="age" type="xs:positiveInteger"/>
            </xs:sequence>
        </xs:complexType>
    </xs:element>
</xs:schema>
```

To generate the XML and print it to the console in a formatted way, run the following command:

```bash
xmlgenerator --pretty examples/employee.xsd
```

An example of the resulting XML document:

```xml
<employee xmlns:xs="http://www.w3.org/2001/XMLSchema">
  <firstName>Rpgubocpxtb</firstName>
  <lastName>Ebfzoc</lastName>
  <email>Yoyzbjplus</email>
  <age>1606855874</age>
</employee>
```
*Note: The values in the fields are generated randomly, so your result will differ.*

Formally, we received a valid XML document (it passes validation against the source XSD schema), but there are several semantic issues:
- `firstName` and `lastName` contain random, meaningless text.
- The `patronymic` field is missing (it's optional in the schema, but we'd like it to be present).
- The `email` value is not in a valid format.
- The `age` value is an unreasonably large number.

## Configuration

`xmlgenerator` allows you to flexibly configure the generation process using a YAML file, passed with the `-c` or `--config` option.

### Customizing the generation of elements and values

These settings are specified in the `randomization` section of the configuration file and allow you to control the generation of document elements and attributes.

To demonstrate, we will use the [order.xsd](examples/order.xsd) schema, which describes an order with items:

```xml
<?xml version="1.0" encoding="UTF-8"?>
<xs:schema xmlns:xs="http://www.w3.org/2001/XMLSchema">

  <xs:element name="order">
    <xs:complexType>
      <xs:sequence>
        <xs:element name="orderId" type="xs:string"/>
        <xs:element name="description" type="xs:string" minOccurs="0"/>
        <xs:element name="items">
          <xs:complexType>
            <xs:sequence>
              <xs:element name="item" minOccurs="1" maxOccurs="unbounded">
                <xs:complexType>
                  <xs:sequence>
                    <xs:element name="productCode">
                      <xs:simpleType>
                        <xs:restriction base="xs:string">
                          <xs:minLength value="5"/>
                          <xs:maxLength value="10"/>
                        </xs:restriction>
                      </xs:simpleType>
                    </xs:element>
                    <xs:element name="quantity">
                      <xs:simpleType>
                        <xs:restriction base="xs:positiveInteger">
                          <xs:minInclusive value="1"/>
                          <xs:maxInclusive value="100"/>
                        </xs:restriction>
                      </xs:simpleType>
                    </xs:element>
                  </xs:sequence>
                </xs:complexType>
              </xs:element>
            </xs:sequence>
          </xs:complexType>
        </xs:element>
      </xs:sequence>
      <xs:attribute name="status" type="xs:string" use="optional"/>
    </xs:complexType>
  </xs:element>

</xs:schema> 
```

#### Probability of adding optional attributes

The `probability` parameter determines the probability (from 0.0 to 1.0) of adding optional attributes to the document (those with `use="optional"` in the schema).

In our schema, this is the `status` attribute of the `<order>` element.

**`config.yml` configuration:**
```yaml
global:
  randomization:
    # Set the probability to 100% so that the `status` attribute is always present
    probability: 1.0
```

**Command:**
```bash
xmlgenerator -c config.yml --pretty examples/order.xsd
```

**Example result:**
```xml
<!-- the status attribute is now always present -->
<order xmlns:xs="http://www.w3.org/2001/XMLSchema" status="Yv">
  <orderId>F</orderId>
  <items>
    <item>
      <productCode>Wbfmvrhw</productCode>
      <quantity>34</quantity>
    </item>
    <item>
      <productCode>Stoccquo</productCode>
      <quantity>40</quantity>
    </item>
  </items>
</order>
```
*If you set `probability: 0.0`, the `status` attribute will definitely NOT be added.*

#### Limiting the number of elements

The `min_occurs` and `max_occurs` parameters allow you to override how many times a repeating element can be generated (e.g., `item` in our schema, which has `maxOccurs="unbounded"`).

**`config.yml` configuration:**
```yaml
global:
  randomization:
    # Generate from 3 to 5 `item` elements
    min_occurs: 3
    max_occurs: 5
```

**Command:**
```bash
xmlgenerator -c config.yml --pretty examples/order.xsd
```

**Example result:**
```xml
<order xmlns:xs="http://www.w3.org/2001/XMLSchema">
  <orderId>N</orderId>
  <description>Nujhx</description>
  <!-- 4 item elements were generated, which is in the range of 3 to 5 -->
  <items>
    <item>
      <productCode>Qporrht</productCode>
      <quantity>53</quantity>
    </item>
    <item>
      <productCode>Qtauts</productCode>
      <quantity>24</quantity>
    </item>
    <item>
      <productCode>Euamsuseks</productCode>
      <quantity>87</quantity>
    </item>
    <item>
      <productCode>Nimdpctfx</productCode>
      <quantity>99</quantity>
    </item>
  </items>
</order>
```

#### Limiting string length

The `min_length` and `max_length` parameters allow you to set or narrow the length range for generated string values if it is defined in the XSD.

In our example, this affects `orderId` and `description`.

**`config.yml` configuration:**
```yaml
global:
  randomization:
    min_length: 30
    max_length: 50
```

**Command:**
```bash
xmlgenerator -c config.yml --pretty examples/order.xsd
```

**Example result:**
```xml
<order xmlns:xs="http://www.w3.org/2001/XMLSchema">
    <!-- The length of orderId and description is now from 30 to 50 characters -->
    <!-- The length of productCode remains the same, as it is defined in the XSD schema (5-10) -->
    <orderId>Aqbglrbzeswpfoesnammolxzgcppmxsdqfryrqqpepc</orderId>
    <description>Lnfpewbjffxkmiifftjgcdsucixxuqtjpukzkybxsqeoy</description>
    <items>
        <item>
            <productCode>Cqlfnrdhhf</productCode>
            <quantity>81</quantity>
        </item>
    </items>
</order>
```

#### Limiting the range for numeric values

Similar to strings, the `min_inclusive` and `max_inclusive` parameters allow you to set or narrow the range for numeric values if it is defined in the XSD.

To demonstrate, let's create an XML from the [employee.xsd](examples/employee.xsd) schema. In our example, this will affect the `age` field.

**`config.yml` configuration:**
```yaml
global:
  randomization:
    min_inclusive: 10
    max_inclusive: 90
```

**Command:**
```bash
xmlgenerator -c config.yml --pretty examples/employee.xsd
```

**Example result:**
```xml
<employee xmlns:xs="http://www.w3.org/2001/XMLSchema">
    <firstName>Rmppncvmgdotncbx</firstName>
    <lastName>Khwbhu</lastName>
    <email>R</email>
    <age>19</age>
</employee>
```

### Overriding values

The `value_override` section allows you to set specific values for elements and attributes, replacing randomly generated ones. The key is the tag/attribute name or a regular expression for it.

#### By tag/attribute name

You can set a value for a field by specifying its exact name.

**`config.yml` configuration:**
```yaml
global:
  value_override:
    # A value of "31" will be set for all <age> elements and attributes
    age: "31"
```

**Command:**
```bash
xmlgenerator -c config.yml --pretty examples/employee.xsd
```

**Example result:**
```xml
<employee xmlns:xs="http://www.w3.org/2001/XMLSchema">
  <firstName>Snaswuddx</firstName>
  <lastName>Qv</lastName>
  <patronymic>Kribmsokjlmzodybizpk</patronymic>
  <email>Nnamfbwmhlnee</email>
  <!-- The value was overridden -->
  <age>31</age>
</employee>
```

#### By regular expression for tag/attribute name

If you need to apply one rule to multiple fields, you can use a regular expression.

**`config.yml` configuration:**
```yaml
global:
  value_override:
    # For all elements and attributes whose names end with "Name" (firstName, lastName),
    # the value "Smith" will be set
    ".*Name": "Smith"
```

**Command:**
```bash
xmlgenerator -c config.yml --pretty examples/employee.xsd
```

**Example result:**
```xml
<employee xmlns:xs="http://www.w3.org/2001/XMLSchema">
  <!-- Values were overridden by regular expression -->
  <firstName>Smith</firstName>
  <lastName>Smith</lastName>
  <patronymic>Xritviffwqtgjf</patronymic>
  <email>Zmrntlenbiiphb</email>
  <age>376513798</age>
</employee>
```

#### Using built-in functions

The most powerful method is to use placeholders like `{{ function }}` to substitute data generated by built-in functions.

**`config.yml` configuration:**
```yaml
global:
  value_override:
    firstName: "{{ first_name }}"
    lastName: "{{ last_name }}"
    patronymic: "{{ middle_name }}"
    email: "{{ email }}"
    age: "{{ number(18, 65) }}"
```

**Command:**
```bash
xmlgenerator -c config.yml --pretty examples/employee.xsd
```

**Example result:**
```xml
<employee xmlns:xs="http://www.w3.org/2001/XMLSchema">
  <!-- Values generated using placeholders -->
  <firstName>Derek</firstName>
  <lastName>Moore</lastName>
  <email>sandrawilkerson@example.com</email>
  <age>27</age>
</employee>
```

*A full list of available functions is provided in [Appendix 2](#appendix-2-placeholder-functions)*.

### Configuring output filenames

The `output_filename` parameter allows you to set a template for the names of generated files. This is especially useful when processing multiple schemas where the results need to be saved to a single directory. Placeholders can also be used in the template.

**`config.yml` configuration:**
```yaml
global:
  # Template: <schema_name_without_extension>_report_<random_uuid>.xml
  output_filename: "{{ source_extracted }}_report_{{ uuid }}"
```

**Command:**
```bash
xmlgenerator -c config.yml -o output/ examples/employee.xsd
```

**Result (command executed 5 times):**
```
output/
├── employee_report_36621bb4-208c-4e39-9f9d-aafd9361a49d.xml
├── employee_report_53d3c673-5da4-4f6a-8de6-c5247202f113.xml
├── employee_report_6df829e3-35b8-4a8d-b848-f9696f32331c.xml
├── employee_report_94b499e8-4279-4d74-aa8a-f0d6e3a8ffd5.xml
└── employee_report_d04e6eec-266f-4a24-bc84-3aac45a7708a.xml
```

### Applying settings for groups of documents

The `specific` section allows you to apply sets of settings only to specific schema files that match a given name pattern (string or regular expression).
This allows you to override `global` settings for specific cases, including batch processing of schemas.

The order of settings priority is: **specific -> global -> default**.

To demonstrate, we will use two new schemas: [invoice.xsd](./examples/invoice.xsd) and [contract.xsd](./examples/contract.xsd).

**`invoice.xsd`**
```xml
<?xml version="1.0" encoding="UTF-8"?>
<xs:schema xmlns:xs="http://www.w3.org/2001/XMLSchema">
    <xs:element name="invoice">
        <xs:complexType>
            <xs:sequence>
                <xs:element name="invoiceNumber" type="xs:string"/>
                <xs:element name="company" type="xs:string"/>
                <xs:element name="amount" type="xs:decimal"/>
            </xs:sequence>
        </xs:complexType>
    </xs:element>
</xs:schema>
```

**`contract.xsd`**
```xml
<?xml version="1.0" encoding="UTF-8"?>
<xs:schema xmlns:xs="http://www.w3.org/2001/XMLSchema">
    <xs:element name="contract">
        <xs:complexType>
            <xs:sequence>
                <xs:element name="contractId" type="xs:string"/>
                <xs:element name="company" type="xs:string"/>
                <xs:element name="signDate" type="xs:date"/>
            </xs:sequence>
        </xs:complexType>
    </xs:element>
</xs:schema>
```

#### Configuration Example

Let's create a configuration where:
1.  Globally, for all documents, the company (`company`) will be "GlobalCorp".
2.  For invoices (`invoice.xsd`), the company will be "Invoice LLC", and the `amount` field will be generated randomly (resetting the global setting).
3.  For contracts (`cont.*.xsd`), the company will be "Contractors Ltd.".

**`config.yml` configuration:**
```yaml
global:
  value_override:
    company: "GlobalCorp"
    amount: "100.00" # Global value for all amount fields

specific:
  # Rules for files that exactly match "invoice.xsd"
  "invoice.xsd":
    value_override:
      company: "Invoice LLC" # Override the global value
      amount: # Reset the global value, a random one will be generated

  # Rules for files matching the regular expression "cont.*\\.xsd"
  "cont.*\\.xsd":
    value_override:
      company: "Contractors Ltd." # Override the global value
```

**Command:**
```bash
# Generate XML for all schemas in the examples/ folder and output to output/
xmlgenerator -c config.yml -o output/ --pretty examples/
```

**Results:**

The command will process all `.xsd` files in the directory. Let's look at two of them.

**`output/invoice_0e964d8a-3aec-43c1-8b23-fad50a9a2f50.xml`:**
```xml
<invoice xmlns:xs="http://www.w3.org/2001/XMLSchema">
    <invoiceNumber>Pvmwwyttlaskwpxkcukr</invoiceNumber>
    <!-- The value from the specific block for invoice.xsd was applied -->
    <company>Invoice LLC</company>
    <!-- The global value of 100.00 was reset, a random one was generated -->
    <amount>-55457963.98</amount>
</invoice>
```

**`output/contract_91383077-3a20-4c2a-90d0-e99d36a79606.xml`:**
```xml
<contract xmlns:xs="http://www.w3.org/2001/XMLSchema">
    <contractId>Scbzhbge</contractId>
    <!-- The value from the specific block for cont.*.xsd was applied -->
    <company>Contractors Ltd.</company>
    <signDate>2006-06-10</signDate>
</contract>
```
Thus, the `specific` section provides a powerful mechanism for fine-tuning generation for different document types in a single process.


---

### Appendix 1: Configuration File Structure

```yaml
# Optional variables that can be referenced from placeholders via
# `{{ global('name') }}` or `{{ local('name') }}`.
# - `global` variables are evaluated once (the first time they are needed) and reused for
#   every generated document.
# - `local` variables are re-evaluated for each generated document and stored in the
#   local context.
variables:
  global:
    invoice_id: "{{ uuid }}"
    batch_name: "{{ global('invoice_id') }}-{{ number(1, 10) }}"
  local:
    customer_prefix: "{{ source_extracted }}"
    customer_id: "{{ local('customer_prefix') }}-{{ uuid }}"

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
  #
  # The list of available functions is below.
  # The order of entries matters; the first matching override will be selected.
  # Key matching is case-insensitive.
  value_override:
    name_regexp_1: "static value"
    name_regexp_2: "{{ function_call }}"
    "name_regexp_\\d": "static-text-and-{{ function_call }}"
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

### Appendix 2: Placeholder Functions

In the `value_override` sections, you can specify either a string value or special placeholders:

- `{{ function }}` - substitutes the value provided by the predefined function.
- `{{ global('name') }}` - gets a value of the predefined global variable `name` (configured in the `variables` block);
  the value is generated once per process on first use.
- `{{ local('name') }}` - gets a value of the predefined local variable `name` (configured in the `variables` block);
  the value is recalculated for each generated document. Built-in context values such as `root_element`,
  `source_filename`, `source_extracted`, and `output_filename` are also available through `local()`.

Global and local variables are declared in the optional `variables` block located at the root of the YAML file. Global variables behave similarly to the
old `| global` modifier (the first computed value is reused everywhere) while local variables replace `| local`.

**List of Placeholder Functions:**

| Function                           | Description                                                                                              |
|------------------------------------|----------------------------------------------------------------------------------------------------------|
| `source_filename`                  | Filename of the source XSD schema with its extension (e.g., `schema.xsd`).                               |
| `source_extracted`                 | A string extracted from the source XSD filename using the regex specified in `source_filename`.          |
| `output_filename`                  | String defined by the `output_filename` configuration parameter.                                         |
| `root_element`                     | The name of the root element of the XML document.                                                        |
| `local('name')`                    | Value of the local variable `name` (configured under `variables.local` or built-in context values).      |
| `global('name')`                   | Value of the global variable `name` (configured under `variables.global`).                               |
| `uuid`                             | A random UUIDv4.                                                                                         |
| `regex("pattern")`                 | A random string value matching the specified regular expression.                                         |
| `any('A', "B", C)`                 | A random value from the provided enumeration.                                                            |
| `any_from('./values.txt')`         | A random value from a multi-line file                                                                    |
| `number(A, B)`                     | A random number between A and B.                                                                         |
| `date("2010-01-01", "2025-01-01")` | A random date within the specified range. <tr><td colspan="2" align="center">**Personal data**</td></tr> |
| `first_name`__*__                  | A random first name.                                                                                     |
| `last_name`__*__                   | A random last name.                                                                                      |
| `middle_name`__*__                 | A random middle name.                                                                                    |
| `phone_number`__*__                | A phone number.                                                                                          |
| `email`__*__                       | A random email address. <tr><td colspan="2" align="center">**Address**</td></tr>                         |
| `country`__*__                     | A random country.                                                                                        |
| `city`__*__                        | A random city name.                                                                                      |
| `street`__*__                      | A random street.                                                                                         |
| `house_number`__*__                | A house number.                                                                                          |
| `postcode`__*__                    | A postal code.                                                                                           |
| `administrative_unit`__*__         | An administrative unit (e.g., a district).                                                               |
| `company_name`__*__                | A company name.                                                                                          |
| `bank_name`__*__                   | A bank name. <tr><td colspan="2" align="center">**Russian locale only `ru_RU`**</td></tr>                |
| `inn_fl`                           | Taxpayer Identification Number (for an individual).                                                      |
| `inn_ul`                           | Taxpayer Identification Number (for a legal entity).                                                     |
| `ogrn_ip`                          | Primary State Registration Number (for an individual entrepreneur).                                      |
| `ogrn_fl`                          | Primary State Registration Number (for an individual).                                                   |
| `kpp`                              | Tax Registration Reason Code (KPP).                                                                      |
| `snils_formatted`                  | SNILS (Personal Insurance Account Number) formatted as `123-456-789 90`.                                 |

\* It's available to set custom locale via `func("ru_RU")`. Default locale is `en_US`</td></tr>
