# XML Generator

[![PyPI - Version](https://img.shields.io/pypi/v/xmlgenerator)](https://pypi.org/project/xmlgenerator)
[![PyPI - Downloads](https://img.shields.io/pypi/dm/xmlgenerator)](https://pypistats.org/packages/xmlgenerator)
[![Ask DeepWiki](https://deepwiki.com/badge.svg)](https://deepwiki.com/lexakimov/xmlgenerator)

- [Русский 🇷🇺](README_RU.md)
- [English 🇺🇸](README.md)

Генерирует XML-документы на основе XSD-схем с возможностью настройки через конфигурационный YAML-файл.

Упрощает создание тестовых или демонстрационных XML-данных по сложным схемам.

## Возможности

- Генерация XML-документов на основе XSD-схем
- Кастомизация генерируемых значений через YAML-файл конфигурации
- Валидация сгенерированных документов
- Интерфейс командной строки для удобного использования

## Установка

### Установка через pip

```bash
pip install xmlgenerator
```

### Ручная установка исполняемого файла (linux)

```bash
curl -LO https://github.com/lexakimov/xmlgenerator/releases/latest/download/xmlgenerator-linux-amd64
chmod +x xmlgenerator-linux-amd64
sudo install xmlgenerator-linux-amd64 /usr/local/bin/xmlgenerator

# также можно установить автодополнения для командной строки
# доступны: bash, zsh, tcsh
xmlgenerator -C bash | sudo tee /etc/bash_completion.d/xmlgenerator
```

## Использование

Команда генератора: `xmlgenerator`

**Описание флагов и параметров запуска:**

```
usage: xmlgenerator [-h] [-c <config.yml>] [-o <output.xml>] [-p] [-n alias=namespace] [-v <validation>] [-i]
                    [-e <encoding>] [-s <seed>] [-d] [-V] [-C <shell>]
                    xsd [xsd ...]

Generates XML documents from XSD schemas

positional arguments:
  xsd                              paths to xsd schema(s) or directory with xsd schemas

options:
  -h, --help                       show this help message and exit
  -c, --config <config.yml>        pass a YAML configuration file
  -o, --output <output.xml>        save the output to a directory or file
  -p, --pretty                     prettify the output XML
  -n, --namespace alias=namespace  define XML namespace alias (repeatable flag)
  -v, --validation <validation>    validate the generated XML document (none, schema, schematron; default: schema)
  -i                               continue execution when validation errors occur
  -e, --encoding <encoding>        the output XML encoding (utf-8, windows-1251; default: utf-8)
  -s, --seed <seed>                set the randomization seed
  -d, --debug                      enable debug mode
  -V, --version                    show the current version
  -C, --completion <shell>         print a shell completion script (bash, zsh, tcsh)
```

**Примеры:**

- Сгенерировать XML из одной схемы и вывести в консоль:
   ```bash
   xmlgenerator path/to/your/schema.xsd
   ```

- Сгенерировать XML из всех схем в директории и сохранить в папку `output`, используя конфигурационный файл:
   ```bash
   xmlgenerator -c config.yml -o output/ path/to/schemas/
   ```

- Сгенерировать XML из конкретной схемы, сохранить в файл с красивым форматированием и кодировкой windows-1251:
   ```bash
   xmlgenerator -o output.xml -p -e windows-1251 path/to/your/schema.xsd
   ```

- Сгенерировать XML с отключенной валидацией:
   ```bash
   xmlgenerator -v none path/to/your/schema.xsd
   ```

## Конфигурация

Генератор можно настроить с помощью YAML-файла, передав путь к нему через опцию `-c` или `--config`.

Описание и примеры конфигурации приведены в [CONFIGURATION_RU](./CONFIGURATION_RU.md).

## Валидация

Сгенерированные XML-документы проверяются на соответствие схеме, использованной для генерации.
По умолчанию используется валидация через исходную XSD-схему.

При несоответствии документа схеме выполнение прекращается незамедлительно.
Чтобы продолжить обработку несмотря на ошибки валидации, используйте флаг `-i`.

Чтобы отключить валидацию, укажите флаг `-v none` или `--validation none`.

## Вклад

Приветствуются любые вклады! Пожалуйста, откройте issue или отправьте pull request на GitHub.

### Получение исходного кода

1. **Клонируйте репозиторий:**
   ```bash
   git clone https://github.com/lexakimov/xmlgenerator.git
   cd xmlgenerator
   ```

2. **Создайте и активируйте виртуальное окружение (рекомендуется):**
   ```bash
   python -m venv .venv
   ```
    * **Для Linux/macOS:**
      ```bash
      source .venv/bin/activate
      ```
    * **Для Windows (Command Prompt/PowerShell):**
      ```bash
      .\.venv\Scripts\activate
      ```

3. **Установите зависимости:**
   ```bash
   pip install -r requirements.txt
   ```

4.1. **Установите пакет:**

Установка в режиме разработки (изменения в коде будут сразу видны):
   ```bash
   pip install -e .
   ```

4.2. **Или соберите единый исполняемый файл:**

   ```bash
   python build_native.py
   ```

### Запуск тестов

```bash
pytest
```

---

## Лицензия

Этот проект лицензирован под лицензией MIT. Подробности см. в файле [LICENSE](LICENSE).

## Контакты

По любым вопросам или проблемам обращайтесь по адресу [lex.akimov23@gmail.com].

Вы также можете создать [Issue на GitHub](https://github.com/lexakimov/xmlgenerator/issues) для сообщения об ошибках или
предложений по улучшению.
