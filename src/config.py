from pathlib import Path

# Models (Ollama)
LLM_MODEL = "llama3.1:8b"
EMBED_MODEL = "nomic-embed-text"

# Paths
PROJECT_ROOT = Path(__file__).resolve().parents[1]
DATA_PATH = PROJECT_ROOT / "data" / "six_cs"
CHROMA_PATH = PROJECT_ROOT / "vectorstore" / "chroma_db"

# Retrieval defaults
TOP_K = 4
