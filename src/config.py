from pathlib import Path

OLLAMA_MODEL = "llama3.1:8b"
OLLAMA_HOST = "http://127.0.0.1:11434"

PROJECT_ROOT = Path(__file__).resolve().parents[1]
SIX_CS_DIR = PROJECT_ROOT / "data" / "six_cs"
PROMPTS_DIR = Path(__file__).resolve().parent / "prompts"
