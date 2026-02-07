from pathlib import Path
import re
from typing import List

from langchain_community.llms import Ollama
from langchain_core.prompts import PromptTemplate
from rag.retriever import get_retriever

PROMPT_PATH = Path("src/prompts/enhancer_prompt.txt")


def _clean_single_sentence(output: str, fallback: str) -> str:
    s = (output or "").strip()

    # Remove common prefaces like "Here is the revised sentence:"
    s = re.sub(
        r'^\s*(here is|here\'s)\s+(the\s+)?(revised|revision|corrected)\s+(sentence|text)\s*[:\-]\s*',
        "",
        s,
        flags=re.IGNORECASE,
    ).strip()

    # If model outputs multiple lines, take the last non-empty line
    lines = [ln.strip() for ln in s.splitlines() if ln.strip()]
    if len(lines) > 1:
        s = lines[-1]

    # Strip wrapping quotes
    s = s.strip('"\'')

    # If empty, fallback
    if not s:
        return fallback

    # Keep it to one sentence (soft guard)
    # If there are multiple sentences, keep the first one.
    # (You can remove this if you want multi-sentence paragraph support later.)
    m = re.match(r"(.+?[.!?])\s+.+", s)
    if m:
        s = m.group(1).strip()

    return s


class EnhancementAgent:
    def __init__(self, model: str = "llama3.1:8b", k: int = 6):
        self.llm = Ollama(model=model, temperature=0.0)
        self.retriever = get_retriever(k=k)
        self.prompt = PromptTemplate(
            template=PROMPT_PATH.read_text(encoding="utf-8"),
            input_variables=["text", "principles", "context"],
            template_format="f-string",
        )

    def enhance(self, text: str, target_cs: List[str]) -> str:
        if not target_cs:
            return text

        # Retrieve context (dedupe + limit)
        context_docs = []
        seen = set()
        for principle in target_cs:
            docs = self.retriever.invoke(f"{principle}: {text}")
            for d in docs:
                pc = (d.page_content or "").strip()
                if pc and pc not in seen:
                    seen.add(pc)
                    context_docs.append(d)

        context = "\n\n".join(d.page_content for d in context_docs)[:4000]

        formatted_prompt = self.prompt.format(
            text=text,
            principles=", ".join(target_cs),
            context=context,
        )

        raw = self.llm.invoke(formatted_prompt)
        return _clean_single_sentence(raw, fallback=text)
