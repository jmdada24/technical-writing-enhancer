from pathlib import Path
from typing import List
from langchain_core.documents import Document

from config import DATA_PATH
from rag.chunker import chunk_markdown_by_h2

def load_six_cs_documents() -> List[Document]:
    """
    Loads all markdown files in data/six_cs and chunks them using semantic headers.
    """
    documents: List[Document] = []

    for md_file in DATA_PATH.glob("*.md"):
        principle = md_file.stem  # clarity, completeness, etc.
        content = md_file.read_text(encoding="utf-8")

        # chunk per section
        documents.extend(chunk_markdown_by_h2(content, principle))

    return documents
