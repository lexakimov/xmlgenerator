# XML Generator

![PyPI - Version](https://img.shields.io/pypi/v/xmlgenerator)
[![PyPI - Downloads](https://img.shields.io/pypi/dm/xmlgenerator)](https://pypistats.org/packages/xmlgenerator)
[![DeepWiki](https://img.shields.io/badge/DeepWiki-lexakimov%2Fxmlgenerator-blue.svg?logo=data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAACwAAAAyCAYAAAAnWDnqAAAAAXNSR0IArs4c6QAAA05JREFUaEPtmUtyEzEQhtWTQyQLHNak2AB7ZnyXZMEjXMGeK/AIi+QuHrMnbChYY7MIh8g01fJoopFb0uhhEqqcbWTp06/uv1saEDv4O3n3dV60RfP947Mm9/SQc0ICFQgzfc4CYZoTPAswgSJCCUJUnAAoRHOAUOcATwbmVLWdGoH//PB8mnKqScAhsD0kYP3j/Yt5LPQe2KvcXmGvRHcDnpxfL2zOYJ1mFwrryWTz0advv1Ut4CJgf5uhDuDj5eUcAUoahrdY/56ebRWeraTjMt/00Sh3UDtjgHtQNHwcRGOC98BJEAEymycmYcWwOprTgcB6VZ5JK5TAJ+fXGLBm3FDAmn6oPPjR4rKCAoJCal2eAiQp2x0vxTPB3ALO2CRkwmDy5WohzBDwSEFKRwPbknEggCPB/imwrycgxX2NzoMCHhPkDwqYMr9tRcP5qNrMZHkVnOjRMWwLCcr8ohBVb1OMjxLwGCvjTikrsBOiA6fNyCrm8V1rP93iVPpwaE+gO0SsWmPiXB+jikdf6SizrT5qKasx5j8ABbHpFTx+vFXp9EnYQmLx02h1QTTrl6eDqxLnGjporxl3NL3agEvXdT0WmEost648sQOYAeJS9Q7bfUVoMGnjo4AZdUMQku50McDcMWcBPvr0SzbTAFDfvJqwLzgxwATnCgnp4wDl6Aa+Ax283gghmj+vj7feE2KBBRMW3FzOpLOADl0Isb5587h/U4gGvkt5v60Z1VLG8BhYjbzRwyQZemwAd6cCR5/XFWLYZRIMpX39AR0tjaGGiGzLVyhse5C9RKC6ai42ppWPKiBagOvaYk8lO7DajerabOZP46Lby5wKjw1HCRx7p9sVMOWGzb/vA1hwiWc6jm3MvQDTogQkiqIhJV0nBQBTU+3okKCFDy9WwferkHjtxib7t3xIUQtHxnIwtx4mpg26/HfwVNVDb4oI9RHmx5WGelRVlrtiw43zboCLaxv46AZeB3IlTkwouebTr1y2NjSpHz68WNFjHvupy3q8TFn3Hos2IAk4Ju5dCo8B3wP7VPr/FGaKiG+T+v+TQqIrOqMTL1VdWV1DdmcbO8KXBz6esmYWYKPwDL5b5FA1a0hwapHiom0r/cKaoqr+27/XcrS5UwSMbQAAAABJRU5ErkJggg==)](https://deepwiki.com/lexakimov/xmlgenerator)

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
curl -LO https://github.com/lexakimov/xmlgenerator/releases/download/v0.5.3/xmlgenerator-linux-amd64
chmod +x xmlgenerator-linux-amd64
sudo install xmlgenerator-linux-amd64 /usr/local/bin/xmlgenerator
```

### Установить автодополнения (linux)

```shell
# также доступны: zsh, tcsh
xmlgenerator -C bash | sudo tee /etc/bash_completion.d/xmlgenerator
```

## Использование

Команда генератора: `xmlgenerator`

**Описание флагов и параметров запуска:**

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

Описание и примеры конфигурации описаны в [CONFIGURATION](./CONFIGURATION_RU.md).

## Валидация

Сгенерированные XML-документы проверяются на соответствие схеме, использованной для генерации.
По умолчанию используется валидация через исходную XSD-схему.

При несоответствии документа схеме, выполнение прекращается незамедлительно.
Это поведение можно отключить через флаг `-ff false` или `--fail-fast false`.

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
