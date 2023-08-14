from hashlib import sha256
from pathlib import Path
from typing import List
from langchain.embeddings import OpenAIEmbeddings
from langchain.vectorstores import Chroma
import langchain.docstore.document as docstore
import logging as logger
from parsers.json import JsonParser
from tqdm import tqdm as progress_bar

COLLECTION_NAME = "neonshield-2023-05"
PERSIST_DIRECTORY = "./temp_data/chroma"


class VortexIngester:
    def __init__(self, content_folder: str):
        self.content_folder = content_folder

    def ingest(self) -> None:
        files_to_ingest = list(Path(self.content_folder).glob("*.json"))
        vortex_json_parser = JsonParser()

        chunks: List[docstore.Document] = []
        for document in progress_bar(files_to_ingest, total=len(files_to_ingest)):
            try:
                new_chunks = vortex_json_parser.text_to_docs(document)
                logger.debug(f"Extracted {len(new_chunks)} chunks from {document}")
                chunks.extend(new_chunks)
            except Exception as e:
                logger.error(f"failed to ingest {document} because {e}")

        embeddings = OpenAIEmbeddings(client=None)
        logger.info("Loaded embeddings")
        vector_store = Chroma.from_documents(
            chunks,
            embeddings,
            collection_name=COLLECTION_NAME,
            persist_directory=PERSIST_DIRECTORY,
            ids=[sha256(chunk.page_content) for chunk in chunks],
        )

        logger.info("Created Chroma vector store")
        vector_store.persist()
        logger.info("Persisted Chroma vector store")
