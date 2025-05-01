import dataclasses
import logging
import re
import sys
from dataclasses import dataclass, field, Field
from typing import Dict, get_args, get_origin, Any

import yaml

logger = logging.getLogger(__name__)


@dataclass
class RandomizationConfig:
    probability: float = field(default=None)
    min_occurs: int = field(default=None)
    max_occurs: int = field(default=None)
    min_length: int = field(default=None)
    max_length: int = field(default=None)
    min_inclusive: int = field(default=None)
    max_inclusive: int = field(default=None)


@dataclass
class GlobalRandomizationConfig(RandomizationConfig):
    probability: float = field(default=0.5)


@dataclass
class GeneratorConfig:
    source_filename: str = None
    output_filename: str = None
    randomization: RandomizationConfig = field(default_factory=lambda: RandomizationConfig())
    value_override: Dict[str, str] = field(default_factory=lambda: {})


@dataclass
class GlobalGeneratorConfig(GeneratorConfig):
    source_filename: str = field(default='(?P<extracted>.*).(xsd|XSD)')
    output_filename: str = field(default='{{ source_extracted }}_{{ uuid }}')
    randomization: GlobalRandomizationConfig = field(default_factory=lambda: GlobalRandomizationConfig())


@dataclass
class Config:
    global_: GlobalGeneratorConfig = field(default_factory=lambda: GlobalGeneratorConfig())
    specific: Dict[str, GeneratorConfig] = field(default_factory=lambda: {})

    def get_for_file(self, xsd_name):
        for pattern, conf in self.specific.items():
            if re.match(pattern, xsd_name):
                logger.debug("resolved configration with pattern '%s'", pattern)
                base_dict = dataclasses.asdict(self.global_)
                override_dict = dataclasses.asdict(conf, dict_factory=lambda x: {k: v for (k, v) in x if v is not None})
                updated_dict = _recursive_update(base_dict, override_dict)
                merged_config = _map_to_class(updated_dict, GeneratorConfig, "")
                local_override = conf.value_override
                global_override = self.global_.value_override
                merged_config.value_override = _merge_dicts(local_override, global_override)
                _log_configration('using specific configuration:', merged_config)
                return merged_config

        _log_configration('using global configration:', self.global_)
        return self.global_


def load_config(file_path: str | None) -> "Config":
    if not file_path:
        config = Config()
        _log_configration("created default configuration:", config)
        return config
    with open(file_path, 'r') as file:
        config_data: dict[str, str] = yaml.safe_load(file) or {}
        config = _map_to_class(config_data, Config, "")
        _log_configration(f"configuration loaded from {file_path}:", config)
        return config


def _map_to_class(data_dict: dict, cls, parent_path: str):
    # Обработка dataclass
    if dataclasses.is_dataclass(cls):
        class_fields: dict[str, Field] = cls.__dataclass_fields__
        required_fields: list[str] = []
        yaml_items: dict[str, Any] = {}

        for name, class_field in class_fields.items():
            if class_field.default is dataclasses.MISSING and class_field.default_factory is dataclasses.MISSING:
                required_fields.append(name)

        if data_dict:
            for yaml_name, value in data_dict.items():
                class_field_name = yaml_name if yaml_name != "global" else "global_"
                if class_field_name not in class_fields:
                    logger.error('YAML parse error: unexpected property: %s.%s', parent_path, yaml_name)
                    sys.exit(1)

                # Определяем тип поля
                field_type = class_fields[class_field_name].type
                yaml_items[class_field_name] = _map_to_class(value, field_type, f"{parent_path}.{yaml_name}")

        # Проверка на отсутствие обязательных полей
        missing_fields = required_fields - yaml_items.keys()
        if missing_fields:
            logger.error('YAML parse error: missing required properties in %s:', parent_path)
            for missing_field in missing_fields:
                yaml_field_name = missing_field if missing_field != "global_" else "global"
                logger.error(yaml_field_name)
            sys.exit(1)

        return cls(**yaml_items)

    # Обработка словарей
    elif get_origin(cls) is dict:
        key_type, value_type = get_args(cls)
        if not data_dict:
            data_dict = {}
        return {
            k: _map_to_class(v, value_type, f"{parent_path}.{k}")
            for k, v in data_dict.items()
        }

    # Обработка списков
    elif get_origin(cls) is list:
        item_type = get_args(cls)[0]
        return [_map_to_class(item, item_type, f"{parent_path}[{i}]") for i, item in enumerate(data_dict)]

    # Базовые типы (int, str, bool и т.д.)
    else:
        return data_dict


def _recursive_update(original, updates):
    for key, value in updates.items():
        if key in original and isinstance(original[key], dict) and isinstance(value, dict):
            _recursive_update(original[key], value)
        else:
            original[key] = value
    return original


def _merge_dicts(base_dict, extra_dict):
    merged_dict = dict(base_dict)
    for key, value in extra_dict.items():
        if key not in merged_dict:
            merged_dict[key] = value
    return merged_dict


def _log_configration(message, config):
    if logger.isEnabledFor(logging.DEBUG):
        logger.debug(message)
        as_dict = dataclasses.asdict(config)
        dumped = yaml.safe_dump(as_dict, allow_unicode=True, width=float("inf"), sort_keys=False, indent=4)
        for line in dumped.splitlines():
            logger.debug('|\t%s', line)
