from pathlib import Path

OLLAMA_MODEL = "llama3.1:8b"
OLLAMA_HOST = "https://technical-writing-enhancer-nlp-project.streamlit.app/"

PROJECT_ROOT = Path(__file__).resolve().parents[1]
SIX_CS_DIR = PROJECT_ROOT / "data" / "six_cs"
PROMPTS_DIR = Path(__file__).resolve().parent / "prompts"
