from pathlib import Path
import streamlit as st

# Primary: Groq
GROQ_API_KEY = st.secrets.get("GROQ_API_KEY")
GROQ_MODEL = "mixtral-8x7b-32768"

# Fallback: Ollama
OLLAMA_HOST = "http://localhost:11434"
OLLAMA_MODEL = "llama3.1:8b"

PROJECT_ROOT = Path(__file__).resolve().parents[1]
SIX_CS_DIR = PROJECT_ROOT / "data" / "six_cs"
PROMPTS_DIR = Path(__file__).resolve().parent / "prompts"