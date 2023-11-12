from dataclasses import dataclass

import yaml


# pylint: disable=too-many-instance-attributes
@dataclass
class GladstoneSettings:
    system_prompt: str
    database_region: str
    database_name_message: str

    collection_name: str = "neonshield-2023-05"
    persist_directory: str = "./query/temp_data/chroma"

    model_name: str = "gpt-4"
    documents_returned: str = "4"
    documents_considered: str = "20"
    lambda_mult: str = "0.5"
    temperature: str = "0.7"

    build_directory: str = "../dist"
    document_store_bucket: str = "gladstone-gpt-data"

    @classmethod
    def from_yaml(cls, file_name):
        with open(file_name, "r", newline="\n") as yaml_file:
            file = yaml.safe_load(yaml_file)
        return cls(**file)
