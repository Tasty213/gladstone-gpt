from pathlib import Path
from datetime import date
from typing import Dict, List, Tuple
from parsers.base import BaseParser
import langchain.docstore.document as docstore
import pdfplumber
import logging as logger
from pypdf import PdfReader

from utils import getattr_or_default


class PdfParser(BaseParser):
    """A parser for extracting and cleaning text from PDF documents."""

    def text_to_docs(
        self, pdf_file_path: Path, metadata: Dict[str, str]
    ) -> List[docstore.Document]:
        raw_pages, metadata_parsed = self.parse_pdf(pdf_file_path)
        cleaned_text_pdf = self.clean_text(raw_pages)

        combined_metadata = {
            **metadata,
            **metadata_parsed,
        }

        return self._docs_builder(cleaned_text_pdf, combined_metadata)

    def parse_pdf(self, pdf_file_path: Path) -> Tuple[list[str], Dict[str, str]]:
        """Extract and return the pages and metadata from the PDF."""
        metadata = self.extract_metadata_from_pdf(pdf_file_path)
        pages = self.extract_pages_from_pdf(pdf_file_path)
        return pages, metadata

    def extract_metadata_from_pdf(self, pdf_file_path: Path) -> Dict[str, str]:
        """Extract and return the metadata from the PDF."""
        logger.debug("Extracting metadata")
        with open(pdf_file_path, "rb") as pdf_file:
            reader = PdfReader(pdf_file)
            metadata = reader.metadata
            logger.debug(f"{getattr(metadata, 'title', 'no title')}")
            return {
                "title": getattr_or_default(metadata, "title", "").strip(),
                "author": getattr_or_default(metadata, "author", "").strip(),
            }

    def extract_pages_from_pdf(self, pdf_file_path) -> list[str]:
        """Extract and return the text of each page from the PDF."""
        logger.debug("Extracting pages")
        with pdfplumber.open(pdf_file_path) as pdf:
            all_pages = map(lambda page: page.extract_text(), pdf.pages)
            non_whitespace_pages = filter(lambda page: page.strip(), all_pages)
            return list(non_whitespace_pages)
