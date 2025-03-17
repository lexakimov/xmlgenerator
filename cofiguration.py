from dataclasses import dataclass, is_dataclass
from typing import List, Dict

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

@dataclass
class GlobalConfig:
    value_override: Dict[str, str]
    randomization: RandomizationConfig


@dataclass
class Config:
    debug: bool
    source: SourceConfig
    output: OutputConfig
    global_: GlobalConfig
    specific: Dict[str, str] = None


def load_config(file_path: str) -> Config:
    with open(file_path, 'r') as file:
        config_data = yaml.safe_load(file)

    def map_to_class(data, cls):
        if is_dataclass(cls):
            field_types = {str(f.name).rstrip("_"): f.type for f in cls.__dataclass_fields__.values()}
            return cls(**{k if k != 'global' else f'{k}_': map_to_class(v, field_types[k]) for k, v in data.items()})
        elif isinstance(data, list):
            return [map_to_class(item, cls.__args__[0]) for item in data]
        else:
            return data

    return map_to_class(config_data, Config)
