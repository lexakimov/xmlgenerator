```

тесты для simpleType а не complexType 

# проверка типов mypy

# mypyc
# taichi

# добавить аннотации типов

# cyton - преобразует в c/c++ (pyx)
# nuitka - преобразует в оптимизированный c++ # nuitka --standalone script.py

# numba (jit)
# pypy - interpreter _ jit # pypy script.py



xmlgenerator test.xsd               # генерация из одного файла, вывод в stdout (только xml)

xmlgenerator *.xsd                  # генерация из n файлов, вывод в stdout (только xml)
xmlgenerator path/
xmlgenerator path/*.xsd

xmlgenerator -o test.xml test.xsd   # генерация из одного файла, вывод в файл

xmlgenerator -o out_dir/ test.xsd   # генерация из одного файла, вывод в директорию

xmlgenerator -o out_dir/ *.xsd      # генерация из n файлов, вывод в директорию
xmlgenerator -o out_dir/ path/
xmlgenerator -o out_dir/ path/*.xsd


# xsdxmlgen
# xmlgen
# genxml
# genxmlfromxsd
# xmlgenerator
# xsdgenxml
# xsdtoxml
# xml_
```


### Установка

```shell
pip install .
```

### Удаление

```shell
pip uninstall xmlgenerator
```


# XML Generator

## Обзор

Этот проект генерирует XML-документы из XSD-схем. Он поддерживает различные конфигурации и опции валидации.

## Возможности

- Генерация XML-документов на основе XSD-схем
- Настраиваемые конфигурации через YAML-файлы
- Поддержка пост-генерационной валидации с использованием XSD-схем
- Интерфейс командной строки для удобного использования

## Требования

- Python 3.x
- `pip` для управления пакетами

## Установка

1. Клонируйте репозиторий:
    ```sh
    git clone <repository_url>
    cd <repository_directory>
    ```

2. Установите необходимые пакеты:
    ```sh
    pip install -r requirements.txt
    ```

## Использование

### Интерфейс командной строки

Для генерации XML-документа из XSD-схемы используйте следующую команду:

```sh
python generate_xml.py -s <source.xsd> -o <output.xml> [-c <config.yml>] [-d]
```

- `-s`, `--schema`: Путь к исходной XSD-схеме (обязательно)
- `-o`, `--output`: Путь для сохранения сгенерированного XML-документа (опционально)
- `-c`, `--config`: Путь к YAML-файлу конфигурации (опционально)
- `-d`, `--debug`: Включить режим отладки (опционально)

### Пример

```sh
python generate_xml.py -s schema.xsd -o output.xml -c config.yml -d
```

## Конфигурация

Файл конфигурации (`config.yml`) позволяет настраивать различные аспекты процесса генерации XML. Вот пример конфигурации:

```yaml
source:
  directory: "schemas/"
  file_names:
    - "schema1.xsd"
    - "schema2.xsd"

output:
  directory: "output/"
  encoding: "utf-8"
  pretty: true
  log_result: true
  post_validate: "schema"
  fail_fast: true

specific:
  ".*schema1.*":
    some_specific_setting: "value"
```

## Валидация

Сгенерированные XML-документы могут быть проверены на соответствие XSD-схеме, использованной для генерации. Если в конфигурации указано `post_validate: schema`, скрипт выполнит эту проверку автоматически.

## Лицензия

Этот проект лицензирован под лицензией MIT. Подробности см. в файле `LICENSE`.

## Вклад

Приветствуются любые вклады! Пожалуйста, откройте issue или отправьте pull request на GitHub.

## Контакты

По любым вопросам или проблемам обращайтесь по адресу [your_email@example.com].
