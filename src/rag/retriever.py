from langchain_community.vectorstores import Chroma
from rag.loader import load_six_cs_documents
from rag.embeddings import get_embedding_model
from config import CHROMA_PATH


def build_or_load_vectorstore():
    embedding = get_embedding_model()

    vectorstore = Chroma(
        persist_directory=str(CHROMA_PATH),
        embedding_function=embedding,
    )

    # Build only if empty
    if vectorstore._collection.count() == 0:
        documents = load_six_cs_documents()
        vectorstore.add_documents(documents)

    return vectorstore


def get_retriever(k=8):
    vectorstore = build_or_load_vectorstore()
    return vectorstore.as_retriever(search_kwargs={"k": k})


def retrieve_docs(query: str, k: int = 8):
    """
    Debug helper: returns the raw retrieved Documents for a query.
    """
    retriever = get_retriever(k=k)
    return retriever.invoke(query)
