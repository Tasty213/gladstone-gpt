from dataclasses import asdict
import json
from typing import List
from vortex_pdf_parser import VortexPdfParser
from metadata import Metadata
import langchain.docstore.document as docstore
from langchain.schema import Document


class VortexJsonParser:
    """A parser for extracting and cleaning text from PDF documents."""

    def text_to_docs(self, file: str) -> List[docstore.Document]:
        """Split the text into chunks and return them as Documents."""
        self.vortex_pdf_parser = VortexPdfParser()
        with open(file, "r") as doc:
            data = json.load(doc)

        match data.get("type"):
            case "pdf":
                self.vortex_pdf_parser.set_pdf_file_path(data.get("path"))
                return self.vortex_pdf_parser.clean_text_to_docs(
                    Metadata(
                        data.get("link"),
                        data.get("name"),
                        data.get("author"),
                        data.get("date"),
                    )
                )
            case "json":
                return [
                    Document(
                        page_content=data.get("content"),
                        metadata=asdict(
                            Metadata(
                                data.get("link", "https://www.libdems.org.uk"),
                                data.get("name", "Lib Dem Website"),
                                data.get("author", "Liberal Democrats"),
                                data.get("date", "Unkown"),
                            )
                        ),
                    )
                ]
