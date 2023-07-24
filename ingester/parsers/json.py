import json
from typing import List
from parsers.base import BaseParser
from parsers.pdf import PdfParser
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
                file_path = metadata.get("path")
                return self.vortex_pdf_parser.text_to_docs(file_path, metadata)
            case "json":
                return self.load_pure_json(data, metadata)

    def load_pure_json(self, data: dict, metadata: dict):
        text_list = self.clean_text([data.get("content")])
        return self._docs_builder(text_list, data.get("metadata"))
