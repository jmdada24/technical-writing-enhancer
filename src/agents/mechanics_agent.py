from pathlib import Path
from langchain_community.llms import Ollama
from langchain_core.prompts import PromptTemplate
from config import LLM_MODEL

PROMPT_PATH = Path(__file__).resolve().parents[1] / "prompts" / "mechanics_prompt.txt"


class MechanicsAgent:
    """
    Conservative grammar/mechanics correction only:
    - grammar, spelling, punctuation, capitalization
    - NO style rewrites
    - NO 6C improvements
    """

    def __init__(self, model: str = LLM_MODEL):
        self.llm = Ollama(model=model, temperature=0.0)
        self.prompt = PromptTemplate(
            template=PROMPT_PATH.read_text(encoding="utf-8"),
            input_variables=["text"],
            template_format="f-string",
        )

    def correct(self, text: str) -> str:
        text = (text or "").strip()
        if not text:
            return text

        formatted = self.prompt.format(text=text)
        out = self.llm.invoke(formatted)

        # Extra safety: if model returns empty, fallback
        out = (out or "").strip()
        return out if out else text
