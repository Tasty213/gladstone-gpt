import json
from typing import List
from parsers.base import BaseParser
from parsers.pdf import PdfParser
from metadata import Metadata
import langchain.docstore.document as docstore


class JsonParser(BaseParser):
    """A parser for extracting and cleaning text from PDF documents."""

    def __init__(self) -> None:
        super().__init__()

    def text_to_docs(self, file: str) -> List[docstore.Document]:
        """Split the text into chunks and return them as Documents."""
        self.vortex_pdf_parser = PdfParser()
        with open(file, "r") as doc:
            data = json.load(doc)
        metadata = data.get("metadata")
        match metadata.get("type"):
            case "pdf":
                self.vortex_pdf_parser.set_pdf_file_path(metadata.get("path"))
                return self.vortex_pdf_parser.clean_text_to_docs(
                    Metadata(
                        metadata.get("link"),
                        metadata.get("name"),
                        metadata.get("author"),
                        metadata.get("date"),
                    )
                )
            case "json":
                return self.load_pure_json(data, metadata)

    def load_pure_json(self, data: dict, metadata: dict):
        text_list = self.clean_text([data.get("content")])
        self._docs_builder(text_list, metadata)
        return self._docs_builder(text_list, data.get("metadata"))
