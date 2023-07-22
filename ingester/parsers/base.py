from abc import abstractmethod
import re
from typing import Callable, Dict, List
import langchain.docstore.document as docstore
import langchain.text_splitter as splitter
from loguru import logger


class BaseParser:
    """A parser for extracting and cleaning text from PDF documents."""

    @abstractmethod
    def text_to_docs(self, metadata: Dict[str, str]) -> List[docstore.Document]:
        pass

    def clean_text(
        self,
        pages: List[str],
        cleaning_functions: List[Callable[[str], str]] = None,
    ) -> List[str]:
        """Apply the cleaning functions to the text of each page."""

        if cleaning_functions is None:
            cleaning_functions = [
                self.merge_hyphenated_words,
                self.fix_newlines,
                self.remove_multiple_newlines,
            ]

        logger.info("Cleaning text of each page")
        cleaned_pages = []
        for page_num, text in enumerate(pages):
            for cleaning_function in cleaning_functions:
                text = cleaning_function(text)
            cleaned_pages.append(text)
        return cleaned_pages

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
        text: List[str],
        metadata_parsed: Dict[str, str],
    ) -> List[docstore.Document]:
        """Split the text into chunks and return them as Documents."""
        doc_chunks: List[docstore.Document] = []

        for page_num, page in enumerate(text):
            text_splitter = splitter.RecursiveCharacterTextSplitter(
                chunk_size=1000,
                separators=["\n\n", "\n", ".", "!", "?", ",", " ", ""],
                chunk_overlap=200,
            )
            chunks = text_splitter.split_text(page)
            for i, chunk in enumerate(chunks):
                doc = docstore.Document(
                    page_content=chunk,
                    metadata={
                        "page_number": page_num,
                        "chunk": i,
                        **metadata_parsed,
                    },
                )
                doc_chunks.append(doc)
        return doc_chunks
