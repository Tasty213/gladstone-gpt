import os

COLLECTION_NAME = "neonshield-2023-05"
PERSIST_DIRECTORY = "./query/temp_data/chroma"
MODEL_NAME = os.environ.get("MODEL_NAME", "gpt-4")
