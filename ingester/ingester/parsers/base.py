from abc import abstractmethod
import re
from typing import Callable, Dict, List
import langchain.docstore.document as docstore
import langchain.text_splitter as splitter
import logging as logger


class BaseParser:
    """A parser for extracting and cleaning text from PDF documents."""

    def __init__(
        self,
        chunk_size=250,
        model_name="gpt-3.5-turbo",
        chunk_overlap=25,
        split_document_text=True,
    ):
        self.chunk_size = chunk_size
        self.model_name = model_name
        self.chunk_overlap = chunk_overlap
        self.split_document_text = split_document_text

    @abstractmethod
    def text_to_docs(self, metadata: Dict[str, str]) -> List[docstore.Document]:
        pass

    def clean_text(
        self,
        pages: List[str],
        cleaning_functions: List[Callable[[str], str]] = None,
    ) -> str:
        """
        Apply the cleaning functions to the text of each page. Then combine the
        result into one long string.
        """

        if cleaning_functions is None:
            cleaning_functions = [
                self.merge_hyphenated_words,
                self.fix_newlines,
                self.remove_multiple_newlines,
            ]

        logger.debug("Cleaning text of each page")
        cleaned_pages = []
        for text in pages:
            for cleaning_function in cleaning_functions:
                text = cleaning_function(text)
            cleaned_pages.append(text)
        return "\n".join(cleaned_pages)

    @staticmethod
    def merge_hyphenated_words(text: str) -> str:
        """Merge words in the text that have been split with a hyphen."""
        return re.sub(r"(\w)-\n(\w)", r"\1\2", text)

    @staticmethod
    def fix_newlines(text: str) -> str:
        """Replace single newline characters in the text with spaces."""
        return re.sub(r"(?<!\n)\n(?!\n)", " ", text)

    @staticmethod
    def remove_multiple_newlines(text: str) -> str:
        """Reduce multiple newline characters in the text to a single newline."""
        return re.sub(r"\n{2,}", "\n", text)

    def _docs_builder(
        self,
        text: str,
        metadata_parsed: Dict[str, str],
    ) -> List[docstore.Document]:
        """Split the text into chunks and return them as Documents."""
        doc_chunks: List[docstore.Document] = []

        if self.split_document_text:
            text_splitter = splitter.TokenTextSplitter(
                chunk_size=self.chunk_size,
                model_name=self.model_name,
                chunk_overlap=self.chunk_overlap,
            )
            chunks = text_splitter.split_text(text)
        else:
            chunks = [text]

        for i, chunk in enumerate(chunks):
            chunk_with_date = f"{metadata_parsed.get('date')}\n\n{chunk}"
            chunk_with_date = chunk_with_date.replace("\n", " ")
            doc = docstore.Document(
                page_content=chunk_with_date,
                metadata={
                    "page_number": 0,
                    "chunk": i,
                    **metadata_parsed,
                },
            )
            doc_chunks.append(doc)
        return doc_chunks
