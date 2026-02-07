from pathlib import Path
from langchain_core.prompts import PromptTemplate
from langchain_community.llms import Ollama

PROMPT_PATH = Path("src/prompts/justification_prompt.txt")


class JustificationAgent:
    def __init__(self, model="llama3.1:8b"):
        self.llm = Ollama(model=model)
        self.prompt = PromptTemplate(
        template=PROMPT_PATH.read_text(encoding="utf-8"),
        input_variables=["text", "enhanced", "principles"],
        template_format="f-string",
    )


    def justify(self, text: str, enhanced: str, principles: list[str]) -> str:
        if not principles:
            return "No enhancement needed; the sentence is already effective."

        formatted_prompt = self.prompt.format(
            text=text,
            enhanced=enhanced,
            principles=", ".join(principles),
        )
        return self.llm(formatted_prompt).strip()
