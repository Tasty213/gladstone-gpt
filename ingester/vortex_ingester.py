from typing import List
from langchain.embeddings import OpenAIEmbeddings
from langchain.vectorstores import Chroma
import langchain.docstore.document as docstore
from loguru import logger
from parsers.json import JsonParser
from vortext_content_iterator import VortexContentIterator

COLLECTION_NAME = "neonshield-2023-05"
PERSIST_DIRECTORY = "./data/chroma"


class VortexIngester:
    def __init__(self, content_folder: str):
        self.content_folder = content_folder

    def ingest(self) -> None:
        vortex_content_iterator = VortexContentIterator(self.content_folder)
        vortex_json_parser = JsonParser()

        chunks: List[docstore.Document] = []
        for document in vortex_content_iterator:
            try:
                new_chunks = vortex_json_parser.text_to_docs(document)
                logger.info(f"Extracted {len(new_chunks)} chunks from {document}")
                chunks.extend(new_chunks)
            except Exception as e:
                print(f"failed to ingest {document} because {e}")

        embeddings = OpenAIEmbeddings(client=None)
        logger.info("Loaded embeddings")
        vector_store = Chroma.from_documents(
            chunks,
            embeddings,
            collection_name=COLLECTION_NAME,
            persist_directory=PERSIST_DIRECTORY,
        )

        logger.info("Created Chroma vector store")
        vector_store.persist()
        logger.info("Persisted Chroma vector store")
