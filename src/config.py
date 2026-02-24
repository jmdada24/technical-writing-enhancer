from pathlib import Path
import streamlit as st

# Primary: Groq
GROQ_API_KEY = st.secrets.get("GROQ_API_KEY")
GROQ_MODEL = "llama-3.1-70b-versatile"  

PROJECT_ROOT = Path(__file__).resolve().parents[1]
SIX_CS_DIR = PROJECT_ROOT / "data" / "six_cs"
PROMPTS_DIR = Path(__file__).resolve().parent / "prompts"