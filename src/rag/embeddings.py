from langchain_community.embeddings import OllamaEmbeddings

def get_embedding_model(model: str = "nomic-embed-text"):
    """
    Returns an Ollama embedding model.
    Make sure 'ollama serve' is running and the embedding model is pulled.
    """
    return OllamaEmbeddings(model=model)
