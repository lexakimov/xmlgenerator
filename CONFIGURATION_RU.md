# Конфигурирование xmlgenerator

[ [🇺🇸 English](CONFIGURATION.md) ]

Это руководство поможет вам понять, как настраивать `xmlgenerator`.

* [Базовое использование](#базовое-использование)
* [Конфигурирование](#конфигурирование)
  * [Настройка генерации элементов и значений](#настройка-генерации-элементов-и-значений)
    * [Вероятность добавления опциональных атрибутов](#вероятность-добавления-опциональных-атрибутов)
    * [Ограничение количества элементов](#ограничение-количества-элементов)
    * [Ограничение длины строк](#ограничение-длины-строк)
    * [Ограничение диапазона для числовых значений](#ограничение-диапазона-для-числовых-значений)
  * [Переопределение значений](#переопределение-значений)
    * [По имени тега/атрибута](#по-имени-тегаатрибута)
    * [По регулярному выражению для имени тега/атрибута](#по-регулярному-выражению-для-имени-тегаатрибута)
    * [Использование встроенных функций для генерации значений](#использование-встроенных-функций-для-генерации-значений)
    * [Объявление и использование локальных и глобальных переменных](#объявление-и-использование-локальных-и-глобальных-переменных)
  * [Настройка имени выходных файлов](#настройка-имени-выходных-файлов)
  * [Применение настроек для групп документов](#применение-настроек-для-групп-документов)
    * [Пример конфигурации](#пример-конфигурации)
  * [Приложение 1: Структура конфигурационного файла](#приложение-1-структура-конфигурационного-файла)
  * [Приложение 2: Подстановочные функции](#приложение-2-подстановочные-функции)


## Базовое использование

Для начала рассмотрим самый простой сценарий: генерация XML-документа на основе одной XSD-схемы и вывод результата в консоль.

Для демонстрации мы будем использовать простую схему [employee.xsd](examples/employee.xsd), которая описывает сотрудника:

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

Чтобы сгенерировать XML и вывести его в консоль в отформатированном виде, выполните следующую команду:

```bash
xmlgenerator --pretty examples/employee.xsd
```

Пример полученного XML документа:

```xml
<employee xmlns:xs="http://www.w3.org/2001/XMLSchema">
  <firstName>Rpgubocpxtb</firstName>
  <lastName>Ebfzoc</lastName>
  <email>Yoyzbjplus</email>
  <age>1606855874</age>
</employee>
```
*Примечание: значения в полях генерируются случайным образом, поэтому ваш результат будет отличаться.*

Формально мы получили валидный XML-документ (проходит проверку по исходной XSD-схеме), но есть несколько семантических ошибок:
- `firstName` и `lastName` содержат случайный бессмысленный текст.
- Поле `patronymic` отсутствует (в схеме оно необязательно, но мы бы хотели, чтобы оно присутствовало).
- Значение `email` не соответствует формату.
- Значение `age` слишком велико.

## Конфигурирование

`xmlgenerator` позволяет гибко настраивать процесс генерации с помощью YAML-файла конфигурации, который передается через опцию `-c` или `--config`.

### Настройка генерации элементов и значений

Эти настройки задаются в секции `randomization` файла конфигурации и позволяют управлять генерацией элементов и атрибутов документа.

Для демонстрации мы будем использовать схему [order.xsd](examples/order.xsd), описывающую заказ с товарами:

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

#### Вероятность добавления опциональных атрибутов

Параметр `probability` определяет вероятность (от 0.0 до 1.0) добавления в документ опциональных атрибутов (у которых в схеме `use="optional"`).

В нашей схеме это атрибут `status` у элемента `<order>`.

**Конфигурация `config.yml`:**
```yaml
global:
  randomization:
    # Устанавливаем вероятность в 100%, чтобы атрибут `status` всегда присутствовал
    probability: 1.0
```

**Команда:**
```bash
xmlgenerator -c config.yml --pretty examples/order.xsd
```

**Пример результата:**
```xml
<!-- атрибут status теперь присутствует всегда -->
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
*Если установить `probability: 0.0`, атрибут `status` точно НЕ БУДЕТ добавлен.*

#### Ограничение количества элементов

Параметры `min_occurs` и `max_occurs` позволяют переопределить, сколько раз может генерироваться повторяющийся элемент (например, `item` в нашей схеме, у которого `maxOccurs="unbounded"`).

**Конфигурация `config.yml`:**
```yaml
global:
  randomization:
    # Генерировать от 3 до 5 элементов `item`
    min_occurs: 3
    max_occurs: 5
```

**Команда:**
```bash
xmlgenerator -c config.yml --pretty examples/order.xsd
```

**Пример результата:**
```xml
<order xmlns:xs="http://www.w3.org/2001/XMLSchema">
  <orderId>N</orderId>
  <description>Nujhx</description>
  <!-- Сгенерировано 4 элемента item, что находится в диапазоне от 3 до 5 -->
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

#### Ограничение длины строк

Параметры `min_length` и `max_length` позволяют для генерируемых строковых значений задать или сузить диапазон длины, если он определен в XSD.

В нашем примере это `orderId` и `description`.

**Конфигурация `config.yml`:**
```yaml
global:
  randomization:
    min_length: 30
    max_length: 50
```

**Команда:**
```bash
xmlgenerator -c config.yml --pretty examples/order.xsd
```

**Пример результата:**
```xml
<order xmlns:xs="http://www.w3.org/2001/XMLSchema">
    <!-- Длина orderId и description теперь от 30 до 50 символов -->
    <!-- Длина productCode осталась прежней, т.к. она задана в XSD-схеме (5-10) -->
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

#### Ограничение диапазона для числовых значений

Аналогично строкам, параметры `min_inclusive` и `max_inclusive` позволяют задать или сузить диапазон для числовых значений, если он определен в XSD.

Для демонстрации создадим XML по схеме [employee.xsd](examples/employee.xsd). В нашем примере это затронет поле `age`.

**Конфигурация `config.yml`:**
```yaml
global:
  randomization:
    min_inclusive: 10
    max_inclusive: 90
```

**Команда:**
```bash
xmlgenerator -c config.yml --pretty examples/employee.xsd
```

**Пример результата:**
```xml
<employee xmlns:xs="http://www.w3.org/2001/XMLSchema">
    <firstName>Rmppncvmgdotncbx</firstName>
    <lastName>Khwbhu</lastName>
    <email>R</email>
    <age>19</age>
</employee>
```

### Переопределение значений

Секция `value_override` позволяет задавать конкретные значения для элементов и атрибутов, вместо случайно сгенерированных. Ключом является имя тега/атрибута или регулярное выражение для него.

#### По имени тега/атрибута

Вы можете задать значение для поля, указав его точное имя.

**Конфигурация `config.yml`:**
```yaml
global:
  value_override:
    # Для всех элементов и атрибутов <age> будет установлено значение 31
    age: "31"
```

**Команда:**
```bash
xmlgenerator -c config.yml --pretty examples/employee.xsd
```

**Пример результата:**
```xml
<employee xmlns:xs="http://www.w3.org/2001/XMLSchema">
  <firstName>Snaswuddx</firstName>
  <lastName>Qv</lastName>
  <patronymic>Kribmsokjlmzodybizpk</patronymic>
  <email>Nnamfbwmhlnee</email>
  <!-- Значение было переопределено -->
  <age>31</age>
</employee>
```

#### По регулярному выражению для имени тега/атрибута

Если нужно применить одно правило для нескольких полей, можно использовать регулярное выражение.

**Конфигурация `config.yml`:**
```yaml
global:
  value_override:
    # Для всех элементов и атрибутов, имя которых заканчивается на "Name" (firstName, lastName)
    # будет установлено значение "Smith"
    ".*Name": "Smith"
```

**Команда:**
```bash
xmlgenerator -c config.yml --pretty examples/employee.xsd
```

**Пример результата:**
```xml
<employee xmlns:xs="http://www.w3.org/2001/XMLSchema">
  <!-- Значения были переопределены по регулярному выражению -->
  <firstName>Smith</firstName>
  <lastName>Smith</lastName>
  <patronymic>Xritviffwqtgjf</patronymic>
  <email>Zmrntlenbiiphb</email>
  <age>376513798</age>
</employee>
```

#### Использование встроенных функций для генерации значений

Самый мощный способ — использование плейсхолдеров вида `{{ function }}` для подстановки данных, генерируемых встроенными функциями.

**Конфигурация `config.yml`:**
```yaml
global:
  value_override:
    firstName: "{{ first_name }}"
    lastName: "{{ last_name }}"
    patronymic: "{{ middle_name }}"
    email: "{{ email }}"
    age: "{{ number(18, 65) }}"
```

**Команда:**
```bash
xmlgenerator -c config.yml --pretty examples/employee.xsd
```

**Пример результата:**
```xml
<employee xmlns:xs="http://www.w3.org/2001/XMLSchema">
  <!-- Значения сгенерированы с помощью плейсхолдеров -->
  <firstName>Derek</firstName>
  <lastName>Moore</lastName>
  <email>sandrawilkerson@example.com</email>
  <age>27</age>
</employee>
```

*Полный список доступных функций приведен в [Приложении 2](#приложение-2-подстановочные-функции)*.

#### Объявление и использование локальных и глобальных переменных

Если нужно переиспользовать какое-то сгенерированное значение, вы можете объявить переменные в блоке `variables` и ссылаться на них через функции `local` и `global`.

Значения переменных объявленных в `variables.global` вычисляются из указанных выражений один раз (при первом обращении) и затем при обращении к ним через `global('key')` переиспользуются на протяжении всей генерации.

Значения переменных объявленных в `variables.local` вычисляются из указанных выражений и затем при обращении к ним через `local('key')` переиспользуются в пределах генерации одного документа.

**Конфигурация `config.yml`:**
```yaml
variables:
  global:
    shared_id: "{{ uuid }}"
  local:
    document_code: "prefix_{{ source_extracted }}-{{ uuid }}"

global:
  value_override:
    someAttribute1: "{{ global('shared_id') }}"
    someAttribute2: "{{ local('document_code') }}"
```

### Настройка имени выходных файлов

Параметр `output_filename` позволяет задать шаблон для имен генерируемых файлов. Это особенно полезно при обработке множества схем, когда результаты нужно сохранять в одну директорию. В шаблоне также можно использовать плейсхолдеры.

**Конфигурация `config.yml`:**
```yaml
global:
  # Шаблон: <имя_схемы_без_расширения>_report_<случайный_uuid>.xml
  output_filename: "{{ source_extracted }}_report_{{ uuid }}"
```

**Команда:**
```bash
xmlgenerator -c config.yml -o output/ examples/employee.xsd
```

**Результат (команда выполнена 5 раз):**
```
output/
├── employee_report_36621bb4-208c-4e39-9f9d-aafd9361a49d.xml
├── employee_report_53d3c673-5da4-4f6a-8de6-c5247202f113.xml
├── employee_report_6df829e3-35b8-4a8d-b848-f9696f32331c.xml
├── employee_report_94b499e8-4279-4d74-aa8a-f0d6e3a8ffd5.xml
└── employee_report_d04e6eec-266f-4a24-bc84-3aac45a7708a.xml
```

### Применение настроек для групп документов

Секция `specific` позволяет применять наборы настроек только к определенным файлам схем, которые соответствуют заданному шаблону имени (строка или регулярное выражение).
Это позволяет переопределять `global` настройки для конкретных случаев, в том числе при пакетной обработке схем.

Порядок приоритета настроек: **specific -> global -> default**.

Для демонстрации используем две новые схемы: [invoice.xsd](./examples/invoice.xsd) и [contract.xsd](./examples/contract.xsd).

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

#### Пример конфигурации

Создадим конфигурацию, где:
1.  Глобально для всех документов компания (`company`) будет "GlobalCorp".
2.  Для инвойсов (`invoice.xsd`) компания будет "Invoice LLC", а поле `amount` будет генерироваться случайно (сброс глобальной настройки).
3.  Для контрактов (`cont.*.xsd`) компания будет "Contractors Ltd.".

**Конфигурация `config.yml`:**
```yaml
global:
  value_override:
    company: "GlobalCorp"
    amount: "100.00" # Глобальное значение для всех полей amount

specific:
  # Правила для файлов, точно совпадающих с "invoice.xsd"
  "invoice.xsd":
    value_override:
      company: "Invoice LLC" # Переопределяем global-значение
      amount: # Сбрасываем global-значение, будет сгенерировано случайное

  # Правила для файлов, подходящих под регулярное выражение "cont.*\\.xsd"
  "cont.*\.xsd":
    value_override:
      company: "Contractors Ltd." # Переопределяем global-значение
```

**Команда:**
```bash
# Генерируем XML для всех схем в папке examples/ и выводим в output/
xmlgenerator -c config.yml -o output/ --pretty examples/
```

**Результаты:**

Команда обработает все `.xsd` файлы в директории. Рассмотрим два из них.

**`output/invoice_0e964d8a-3aec-43c1-8b23-fad50a9a2f50.xml`:**
```xml
<invoice xmlns:xs="http://www.w3.org/2001/XMLSchema">
    <invoiceNumber>Pvmwwyttlaskwpxkcukr</invoiceNumber>
    <!-- Применилось значение из specific-блока для invoice.xsd -->
    <company>Invoice LLC</company>
    <!-- Глобальное значение 100.00 было сброшено, сгенерировалось случайное -->
    <amount>-55457963.98</amount>
</invoice>
```

**`output/contract_91383077-3a20-4c2a-90d0-e99d36a79606.xml`:**
```xml
<contract xmlns:xs="http://www.w3.org/2001/XMLSchema">
    <contractId>Scbzhbge</contractId>
    <!-- Применилось значение из specific-блока для cont.*.xsd -->
    <company>Contractors Ltd.</company>
    <signDate>2006-06-10</signDate>
</contract>
```
Таким образом, секция `specific` обеспечивает мощный механизм для тонкой настройки генерации под разные типы документов в одном процессе. 

---

### Приложение 1: Структура конфигурационного файла

В начало конфигурационного файла можно добавить директиву `yaml-language-server`.
Среды разработки с поддержкой JSON Schema для YAML, например VS Code, будут использовать ее для подсказок по структуре и валидации.

```yaml
# yaml-language-server: $schema=https://raw.githubusercontent.com/lexakimov/xmlgenerator/refs/heads/master/configuration-schema.json

# Необязательный блок переменных, доступных как `{{ global('key') }}` и `{{ local('key') }}`.
variables:
  global:
    shared_id: "{{ uuid }}"
    # Здесь так же можно ссылаться на другие переменные через local() и global(). Избегайте циклических зависимостей! 
    shared_suffix: "{{ global('shared_id') }}-{{ number(1, 10) }}"
  local:
    base_prefix: "prefix_{{ source_extracted }}"
    # Здесь так же можно ссылаться на другие переменные через local() и global(). Избегайте циклических зависимостей! 
    document_code: "{{ local('base_prefix') }}-{{ uuid }}"

# Глобальные настройки (применяются ко всем схемам)
global:
  # Регулярное выражение для извлечения подстроки из имени файла исходной xsd схемы.
  # Извлеченная подстрока может быть использована через функцию `source_extracted`.
  # Регулярное выражение обязательно должно содержать именованную группу `(?P<extracted>...)`.
  # Значение по умолчанию: `(?P<extracted>.*).(xsd|XSD)` (означает извлечение имени файла без расширения).
  source_filename: ...

  # Шаблон имени файла для сохранения сгенерированного документа.
  # Значение по умолчанию: `{{ source_extracted }}_{{ uuid }}` (означает имя файла xsd схемы + случайный UUID)
  output_filename: ...

  # Настройки генератора случайных значений
  randomization:
    # Вероятность добавления опциональных элементов (0.0-1.0)
    # Значение по умолчанию: 0.5
    probability: 1
    # Ограничение минимального количества элементов
    min_occurs: 0
    # Ограничение максимального количества элементов
    max_occurs: 5
    # Минимальная длина строк
    min_length: 5
    # Максимальная длина строк
    max_length: 20
    # Минимальное числовое значение
    min_inclusive: 10
    # Максимальное числовое значение
    max_inclusive: 1000000

  # Переопределение генерируемых значений тегов и атрибутов.
  # Ключ - строка или регулярное выражение для сопоставления с именем тега/атрибута.
  # Значение - строка с опциональным использованием плейсхолдеров вида `{{ function }}`.
  #
  # Список доступных функций указан ниже.
  # Порядок записей важен, будет выбрано первое подходящее переопределение.
  # Поиск по ключу происходит без учета регистра.
  value_override:
    name_regexp_1: "static value"
    name_regexp_2: "{{ function_call }}"
    "name_regexp_\d": "static-text-and-{{ function_call }}"
    name: "static-text-and-{{ function_call }}-{{ another_function_call }}"

# Расширение/переопределение глобальных настроек для определенных файлов.
# Ключ - строка или регулярное выражение для сопоставления с именем файла XSD-схемы.
# Порядок записей важен, будет выбрано первое подходящее переопределение.
# Поиск по ключу происходит без учета регистра.
specific:
  # Каждое значение может иметь тот же набор параметров, что и секция global
  "SCHEM.*":
    # для схем с именем "SCHEM.*" имена xml документов будут содержать только UUIDv4 + '.xml'
    output_filename: "{{ uuid }}"
    # Настройки генератора случайных значений для схем с именем "SCHEM.*"
    randomization:
      # для схем с именем "SCHEM.*" вероятность добавления опциональных элементов будет равна 30%
      probability: 0.3
    value_override:
      # переопределение значения, установленного глобальной конфигурацией
      name_regexp_1: "static value"
      # сброс переопределений для тегов/атрибутов, содержащих name, установленных глобальной конфигурацией
      # значение будет сгенерировано случайно
      name:
```

Приоритет используемых настроек:

- настройки из `specific`
- настройки из `global`
- настройки по умолчанию

### Приложение 2: Подстановочные функции

В значениях секций `value_override` можно указывать как строковые значения, так и специальные плейсхолдеры. Например `{{ function }}` — подставит значение, предоставленное предопределенной функцией `function`.

**Список подстановочных функций:**

| Функция                            | Описание                                                                                                   |
|------------------------------------|------------------------------------------------------------------------------------------------------------|
| `source_filename`                  | Имя файла исходной xsd схемы с расширением (например `schema.xsd`)                                         |
| `source_extracted`                 | Строка, извлеченная из имени файла исходной xsd схемы регулярным выражением, указанным в `source_filename` |
| `output_filename`                  | Строка, описываемая параметром конфигурации `output_filename`                                              |
| `root_element`                     | Название тега корневого элемента XML документа                                                             |
| `local('имя')`                     | Значение локальной переменной `имя` (из `variables.local`)                                                 |
| `global('имя')`                    | Значение глобальной переменной `имя` (из `variables.global`)                                               |
| `uuid`                             | Случайный UUIDv4                                                                                           |
| `regex("pattern")`                 | Случайное строковое значение по указанному регулярному выражению                                           |
| `any('A', "B", C)`                 | Случайное значение из перечисленных                                                                        |
| `any_from('./values.txt')`         | Случайное значение из многострочного файла                                                                 |
| `number(A, B)`                     | Случайное число от A до B                                                                                  |
| `date("2010-01-01", "2025-01-01")` | Случайная дата в указанном диапазоне <tr><td colspan="2" align="center">**Персональные данные**</td></tr>  |
| `first_name`__*__                  | Имя                                                                                                        |
| `last_name`__*__                   | Фамилия                                                                                                    |
| `middle_name`__*__                 | Отчество                                                                                                   |
| `phone_number`__*__                | Номер телефона                                                                                             |
| `email`__*__                       | Случайный адрес электронной почты <tr><td colspan="2" align="center">**Адреса**</td></tr>                  |
| `country`__*__                     | Страна                                                                                                     |
| `city`__*__                        | Город                                                                                                      |
| `street`__*__                      | Улица                                                                                                      |
| `house_number`__*__                | Номер дома                                                                                                 |
| `postcode`__*__                    | Почтовый индекс                                                                                            |
| `administrative_unit`__*__         | Район                                                                                                      |
| `company_name`__*__                | Наименование компании                                                                                      |
| `bank_name`__*__                   | Наименование банка <tr><td colspan="2" align="center">**Только русская локаль `ru_RU`**</td></tr>          |
| `inn_fl`                           | ИНН физического лица                                                                                       |
| `inn_ul`                           | ИНН юридического лица                                                                                      |
| `ogrn_ip`                          | ОГРН индивидуального предпринимателя                                                                       |
| `ogrn_fl`                          | ОГРН физического лица                                                                                      |
| `kpp`                              | КПП                                                                                                        |
| `snils_formatted`                  | СНИЛС в формате `123-456-789 90`                                                                           |

\* Для функций, отмеченных звездочкой, можно указать локаль, например: `first_name("ru_RU")`. По умолчанию используется `en_US`.
