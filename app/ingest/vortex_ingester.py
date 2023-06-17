from typing import List
from langchain.embeddings import OpenAIEmbeddings
from langchain.vectorstores import Chroma
import langchain.docstore.document as docstore
from loguru import logger
from .vortex_blog_parser import VortexBlogParser

from settings import COLLECTION_NAME, PERSIST_DIRECTORY

from .vortex_pdf_parser import VortexPdfParser
from .vortext_content_iterator import VortexContentIterator


class VortexIngester:

    def __init__(self, content_folder: str):
        self.content_folder = content_folder

    def ingest(self) -> None:
        vortex_content_iterator = VortexContentIterator(self.content_folder)
        vortex_pdf_parser = VortexPdfParser()
        vortex_blog_parser = VortexBlogParser()

        chunks: List[docstore.Document] = []
        for document in vortex_content_iterator:
            if document.endswith(".pdf"):
                vortex_pdf_parser.set_pdf_file_path(document)
                document_chunks = vortex_pdf_parser.clean_text_to_docs()
                chunks.extend(document_chunks)
            elif document.endswith(".txt"):
                chunks.extend(vortex_blog_parser.text_to_docs(document))
            logger.info(f"Extracted {len(chunks)} chunks from {document}")

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
