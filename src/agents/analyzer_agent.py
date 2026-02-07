import json
import re
from pathlib import Path
from typing import Any, Dict, List

from langchain_community.llms import Ollama
from langchain_core.prompts import PromptTemplate

from config import LLM_MODEL, TOP_K
from rag.retriever import get_retriever
from utils.text_checks import normalize_text

PROMPT_PATH = Path("src/prompts/analyzer_prompt.txt")

ALLOWED = {"clarity", "completeness", "conciseness", "consistency", "concreteness", "courtesy"}
DEFAULT_ANALYSIS = {
    "clarity": "not_applicable",
    "completeness": "not_applicable",
    "conciseness": "not_applicable",
    "consistency": "not_applicable",
    "concreteness": "not_applicable",
    "courtesy": "not_applicable",
}

def extract_json_block(s: str) -> str:
    s = (s or "").strip()
    m = re.search(r"\{.*\}", s, flags=re.DOTALL)
    return m.group(0) if m else ""

def sanitize_targets(targets: Any) -> List[str]:
    if not isinstance(targets, list):
        return []
    clean = []
    for t in targets:
        if isinstance(t, str):
            t = t.strip().lower()
            if t in ALLOWED and t not in clean:
                clean.append(t)
    return clean

class AnalyzerAgent:
    def __init__(self, model: str = LLM_MODEL, k: int = TOP_K):
        self.llm = Ollama(model=model, temperature=0.0)
        self.retriever = get_retriever(k=k)
        
        self.prompt = PromptTemplate(
        template=PROMPT_PATH.read_text(encoding="utf-8"),
        input_variables=["text", "context"],
        template_format="f-string",
    )

    def analyze(self, text: str) -> Dict[str, Any]:
        text = normalize_text(text)

        # ✅ Generic query expansion (no biased keywords)
        queries = [
            text,
            f"relevant examples: {text}",
            f"which 6C principle applies: {text}",
        ]

        docs = []
        for q in queries:
            docs += self.retriever.invoke(q)

        # de-duplicate
        seen = set()
        unique_docs = []
        for d in docs:
            key = (d.page_content or "").strip()
            if key and key not in seen:
                seen.add(key)
                unique_docs.append(d)

        context = "\n\n".join(d.page_content for d in unique_docs)

        formatted = self.prompt.format(text=text, context=context)
        resp = self.llm.invoke(formatted)

        js = extract_json_block(resp)
        if not js:
            return {
                "needs_enhancement": False,
                "target_cs": [],
                "analysis": DEFAULT_ANALYSIS,
                "reasoning": "No valid JSON returned by analyzer.",
            }

        try:
            out = json.loads(js)
        except json.JSONDecodeError:
            return {
                "needs_enhancement": False,
                "target_cs": [],
                "analysis": DEFAULT_ANALYSIS,
                "reasoning": "Analyzer returned invalid JSON.",
            }

        targets = sanitize_targets(out.get("target_cs", []))
        needs = bool(targets)

        analysis = out.get("analysis", {})
        if not isinstance(analysis, dict):
            analysis = {}

        final_analysis = dict(DEFAULT_ANALYSIS)
        for kk in DEFAULT_ANALYSIS:
            vv = analysis.get(kk, DEFAULT_ANALYSIS[kk])
            if isinstance(vv, str):
                vv = vv.strip().lower()
            if vv not in {"ok", "violation", "not_applicable"}:
                vv = "not_applicable"
            final_analysis[kk] = vv

        reasoning = out.get("reasoning", "")
        if not isinstance(reasoning, str):
            reasoning = ""

        return {
            "needs_enhancement": needs,
            "target_cs": targets,
            "analysis": final_analysis,
            "reasoning": reasoning.strip(),
        }
