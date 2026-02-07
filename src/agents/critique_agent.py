import json
import re
from pathlib import Path
from typing import Any, Dict, List

from langchain_community.llms import Ollama
from langchain_core.prompts import PromptTemplate

from config import LLM_MODEL

PROMPT_PATH = Path("src/prompts/critic_prompt.txt")

ALLOWED = {"clarity", "completeness", "conciseness", "consistency", "concreteness", "courtesy"}


def extract_json_block(s: str) -> str:
    s = s.strip()
    m = re.search(r"\{.*\}", s, flags=re.DOTALL)
    return m.group(0) if m else ""


def sanitize_issues(x: Any) -> List[str]:
    if not isinstance(x, list):
        return []
    out = []
    for item in x:
        if isinstance(item, str):
            val = item.strip().lower()
            if val in ALLOWED and val not in out:
                out.append(val)
    return out


class CritiqueAgent:
    def __init__(self, model: str = LLM_MODEL):
        self.llm = Ollama(model=model, temperature=0.0)
        self.prompt = PromptTemplate(
        template=PROMPT_PATH.read_text(encoding="utf-8"),
        input_variables=["original", "revised"],
        template_format="f-string",
    )


    def critique(self, original: str, revised: str) -> Dict[str, Any]:
        formatted = self.prompt.format(original=original, revised=revised)
        resp = self.llm.invoke(formatted)

        js = extract_json_block(resp)
        if not js:
            return {
                "acceptable": True,
                "should_continue": False,
                "issues_remaining": [],
                "reasoning": "No JSON returned by critic; stopping.",
            }

        try:
            out = json.loads(js)
        except json.JSONDecodeError:
            return {
                "acceptable": True,
                "should_continue": False,
                "issues_remaining": [],
                "reasoning": "Invalid JSON returned by critic; stopping.",
            }

        acceptable = bool(out.get("acceptable", False))
        should_continue = bool(out.get("should_continue", False))
        issues = sanitize_issues(out.get("issues_remaining", []))
        reasoning = out.get("reasoning", "")
        if not isinstance(reasoning, str):
            reasoning = ""

        # safety: if acceptable -> stop looping
        if acceptable:
            should_continue = False

        return {
            "acceptable": acceptable,
            "should_continue": should_continue,
            "issues_remaining": issues,
            "reasoning": reasoning.strip(),
        }
