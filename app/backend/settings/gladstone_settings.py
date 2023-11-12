from dataclasses import dataclass

import yaml


@dataclass
class GladstoneSettings:
    system_prompt: str
    collection_name: str = "neonshield-2023-05"
    persist_directory: str = "./query/temp_data/chroma"
    model_name: str = "gpt-4"

    @classmethod
    def from_yaml(cls, file_name):
        with open(file_name, "r", newline="\n") as yaml_file:
            file = yaml.safe_load(yaml_file)
        return cls(**file)
