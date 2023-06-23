from typing import List
from langchain.embeddings import OpenAIEmbeddings
from langchain.vectorstores import Chroma
import langchain.docstore.document as docstore
from loguru import logger

from app.ingest.vortex_json_parser import VortexJsonParser

from settings import COLLECTION_NAME, PERSIST_DIRECTORY

from .vortex_pdf_parser import VortexPdfParser
from .vortext_content_iterator import VortexContentIterator


class VortexIngester:

    def __init__(self, content_folder: str):
        self.content_folder = content_folder

    def ingest(self) -> None:
        vortex_content_iterator = VortexContentIterator(self.content_folder)
        vortex_json_parser = VortexJsonParser()

        chunks: List[docstore.Document] = []
        try:
            for document in vortex_content_iterator:
                chunks.extend(vortex_json_parser.text_to_docs(document))
                logger.info(f"Extracted {len(chunks)} chunks from {document}")
        except Exception as e:
            print(f"failed to ingest {document} because {e.with_traceback()}")

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
