import os

import pytest
import tests
from xmlgenerator.configuration import GeneratorConfig
from xmlgenerator.generator import XmlGenerator
from xmlgenerator.randomization import Randomizer
from xmlgenerator.substitution import Substitutor
from xmlschema import XMLSchema

os.chdir(os.path.dirname(os.path.abspath(tests.__file__)))

@pytest.fixture
def randomizer():
    """Фикстура для создания генератора случайных значений."""
    return Randomizer()

@pytest.fixture
def substitutor(randomizer):
    """Фикстура для создания подстановщика значений."""
    return Substitutor(randomizer)

@pytest.fixture
def generator(randomizer, substitutor):
    """Фикстура для создания генератора XML."""
    return XmlGenerator(randomizer, substitutor)

@pytest.fixture
def config():
    """Фикстура для создания конфигурации генератора."""
    return GeneratorConfig()

@pytest.mark.skip(reason="not yet implemented")
class TestIntegration:
    """Интеграционные тесты для проверки взаимодействия компонентов."""
    
    def test_complex_schema_generation(self, generator, config):
        """
        Проверяет генерацию XML для сложной схемы с множеством типов данных
        и вложенных элементов.
        """
        xsd_schema = XMLSchema("data/complex/integration/complex_schema.xsd")
        generated_xml = generator.generate_xml(xsd_schema, config)
        
        # Проверяем наличие всех обязательных элементов
        assert generated_xml.xpath("/root/person/name")
        assert generated_xml.xpath("/root/person/age")
        assert generated_xml.xpath("/root/person/address")
        
        # Проверяем валидность сгенерированных значений
        age = int(generated_xml.xpath("/root/person/age/text()")[0])
        assert 0 <= age <= 120
        
        # Проверяем корректность вложенных элементов
        address_elements = generated_xml.xpath("/root/person/address/*")
        assert len(address_elements) >= 1
        
    def test_configuration_override(self, generator, config):
        """
        Проверяет корректность переопределения конфигурации
        при генерации XML.
        """
        # Создаем конфигурацию с переопределенными значениями
        custom_config = GeneratorConfig()
        custom_config.set_value("person.name", "John Doe")
        custom_config.set_value("person.age", "30")
        
        xsd_schema = XMLSchema("data/complex/integration/person_schema.xsd")
        generated_xml = generator.generate_xml(xsd_schema, custom_config)
        
        # Проверяем, что значения были переопределены
        assert generated_xml.xpath("/root/person/name/text()")[0] == "John Doe"
        assert generated_xml.xpath("/root/person/age/text()")[0] == "30"
        
    def test_randomization_distribution(self, generator, config):
        """
        Проверяет равномерность распределения случайных значений
        при генерации XML.
        """
        xsd_schema = XMLSchema("data/complex/integration/random_schema.xsd")
        values = []
        
        # Генерируем множество значений
        for _ in range(1000):
            generated_xml = generator.generate_xml(xsd_schema, config)
            value = generated_xml.xpath("/root/value/text()")[0]
            values.append(value)
            
        # Проверяем распределение значений
        unique_values = set(values)
        assert len(unique_values) > 10  # Должно быть достаточно уникальных значений 
