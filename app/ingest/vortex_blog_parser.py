from typing import List

import langchain.docstore.document as docstore
import langchain.text_splitter as splitter
from loguru import logger

class VortexBlogParser:
    """A parser for extracting and cleaning text from PDF documents."""

    def text_to_docs(self, file:str) -> List[docstore.Document]:
        """Split the text into chunks and return them as Documents."""
        doc_chunks: List[docstore.Document] = []
        
        with open(file, "r") as doc:
            text = doc.read()
        
        logger.info(f"Splitting file {file}")
        text_splitter = splitter.RecursiveCharacterTextSplitter(
            chunk_size=1000,
            separators=["\n\n", "\n", ".", "!", "?", ",", " ", ""],
            chunk_overlap=200,
        )
        chunks = text_splitter.split_text(text)
        for i, chunk in enumerate(chunks):
            doc = docstore.Document(
                page_content=chunk,
                metadata={
                    "chunk": i,
                    "source": f"{file}-{i}"
                },
            )
            doc_chunks.append(doc)
        return doc_chunks
