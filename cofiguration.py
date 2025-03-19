from dataclasses import dataclass, is_dataclass, field
from typing import List, Dict, get_args, Optional

import yaml


@dataclass
class SourceConfig:
    directory: str
    file_names: List[str]

@dataclass
class OutputConfig:
    directory: str
    encoding: str
    pretty: bool
    log_result: bool
    post_validate: str
    fail_fast: bool

@dataclass
class RandomizationConfig:
    max_occurs: int
    probability: Optional[float] = None

@dataclass
class GeneratorConfig:
    value_override: Dict[str, str]
    randomization: RandomizationConfig

@dataclass
class Config:
    debug: bool
    source: SourceConfig
    output: OutputConfig
    global_: GeneratorConfig
    specific: Dict[str, GeneratorConfig] = field(default_factory=lambda: {})


def load_config(file_path: str) -> Config:
    with open(file_path, 'r') as file:
        config_data = yaml.safe_load(file)

    loaded_config = _map_to_class(config_data, Config)
    _validate(loaded_config)

    return loaded_config


def _map_to_class(data, cls):
    if is_dataclass(cls):
        field_types = {str(f.name).rstrip("_"): f.type for f in cls.__dataclass_fields__.values()}
        return cls(**{k if k != 'global' else f'{k}_': _map_to_class(v, field_types[k]) for k, v in data.items()})
    elif isinstance(data, dict):
        val_cls = get_args(cls)[1]
        return dict(**{k: _map_to_class(v, val_cls) for k, v in data.items()})
    elif isinstance(data, list):
        return [_map_to_class(item, cls.__args__[0]) for item in data]
    else:
        return data


def _validate(config: Config):
    pass
