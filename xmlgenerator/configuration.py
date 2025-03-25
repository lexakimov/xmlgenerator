import dataclasses
import re
import sys
from dataclasses import dataclass, field, Field
from typing import Dict, get_args, get_origin, Any

import yaml


@dataclass
class RandomizationConfig:
    max_occurs: int = field(default=None)
    probability: float = field(default=None)

@dataclass
class GeneratorConfig:
    source_filename: str = None
    output_filename: str = None
    randomization: RandomizationConfig = field(default_factory=lambda: RandomizationConfig())
    value_override: Dict[str, str] = field(default_factory=lambda: {})

@dataclass
class Config:
    global_: GeneratorConfig = field(default_factory=lambda: GeneratorConfig())
    specific: Dict[str, GeneratorConfig] = field(default_factory=lambda: {})

    def get_for_file(self, xsd_name):
        for pattern, conf in self.specific.items():
            if re.match(pattern, xsd_name):
                base_dict = dataclasses.asdict(self.global_)
                override_dict = dataclasses.asdict(conf, dict_factory=lambda x: {k: v for (k, v) in x if v is not None})
                updated_dict = _recursive_update(base_dict, override_dict)
                return _map_to_class(updated_dict, GeneratorConfig, "")

        return self.global_


def load_config(file_path: str | None) -> "Config":
    if not file_path:
        return Config()
    with open(file_path, 'r') as file:
        config_data: dict[str, str] = yaml.safe_load(file) or {}
        return _map_to_class(config_data, Config, "")


def _map_to_class(data, cls, parent: str):
    # Обработка dataclass
    if dataclasses.is_dataclass(cls):
        class_fields: dict[str, Field] = cls.__dataclass_fields__
        required_fields: list[str] = []
        yaml_items: dict[str, Any] = {}

        for name, class_field in class_fields.items():
            if class_field.default is dataclasses.MISSING and class_field.default_factory is dataclasses.MISSING:
                required_fields.append(name)

        if data:
            for yaml_name, value in data.items():
                class_field_name = yaml_name if yaml_name != "global" else "global_"
                if class_field_name not in class_fields:
                    print(f"YAML parse error: unexpected property: {parent}.{yaml_name}", file=sys.stderr)
                    sys.exit(1)

                # Определяем тип поля
                field_type = class_fields[class_field_name].type
                yaml_items[class_field_name] = _map_to_class(value, field_type, f"{parent}.{yaml_name}")

        # Проверка на отсутствие обязательных полей
        missing_fields = required_fields - yaml_items.keys()
        if missing_fields:
            print(f"YAML parse error: missing required properties in {parent}:", file=sys.stderr)
            for missing_field in missing_fields:
                yaml_field_name = missing_field if missing_field != "global_" else "global"
                print(yaml_field_name, file=sys.stderr)
            sys.exit(1)

        return cls(**yaml_items)

    # Обработка словарей
    elif get_origin(cls) is dict:
        key_type, value_type = get_args(cls)
        if not data:
            data = {}
        return {
            k: _map_to_class(v, value_type, f"{parent}.{k}")
            for k, v in data.items()
        }

    # Обработка списков
    elif get_origin(cls) is list:
        item_type = get_args(cls)[0]
        return [_map_to_class(item, item_type, f"{parent}[{i}]") for i, item in enumerate(data)]

    # Базовые типы (int, str, bool и т.д.)
    else:
        return data


def _recursive_update(original, updates):
    for key, value in updates.items():
        if key in original and isinstance(original[key], dict) and isinstance(value, dict):
            _recursive_update(original[key], value)
        else:
            original[key] = value
    return original
