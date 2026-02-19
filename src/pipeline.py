import json
import re
from typing import Dict, Any, List

from config import OLLAMA_MODEL, SIX_CS_DIR, PROMPTS_DIR
from llm_client import OllamaClient
from knowledge.loader import load_guidelines

ALLOWED_CS = {"clarity", "completeness", "conciseness", "concreteness", "consistency", "courtesy"}


def _read_prompt(name: str) -> str:
    path = PROMPTS_DIR / name
    return path.read_text(encoding="utf-8")


def _extract_json_object(text: str) -> str:
    """
    Robustly extract the first JSON object from a string.
    Handles cases where the model adds extra commentary or wraps in code fences.
    """
    t = text.strip()

    # Strip ```json ... ``` fences if present
    if t.startswith("```"):
        t = re.sub(r"^```(?:json)?\s*", "", t.strip(), flags=re.IGNORECASE)
        t = re.sub(r"\s*```$", "", t.strip())

    # Try direct parse first
    try:
        json.loads(t)
        return t
    except Exception:
        pass

    # Otherwise, find first {...} block (best-effort)
    start = t.find("{")
    end = t.rfind("}")
    if start != -1 and end != -1 and end > start:
        candidate = t[start : end + 1].strip()
        return candidate

    # Nothing found
    raise ValueError(f"Could not extract JSON from model output:\n{t}")


def _safe_json(text: str) -> Dict[str, Any]:
    obj = _extract_json_object(text)
    return json.loads(obj)


def _normalize_apply(apply: List[str]) -> List[str]:
    cleaned = []
    for c in apply or []:
        if not isinstance(c, str):
            continue
        key = c.strip().lower()
        if key in ALLOWED_CS and key not in cleaned:
            cleaned.append(key)
    return cleaned


def run_pipeline(user_text: str, rewrite_strength: str = "light", debug: bool = False) -> Dict[str, Any]:
    original = (user_text or "").strip()
    if not original:
        return {
            "original": "",
            "enhanced": "",
            "applied_principles": [],
            "changed": False,
            **({"analysis": {}} if debug else {}),
        }

    client = OllamaClient(model=OLLAMA_MODEL)

    # 1) Analyze (agentic planning)
    analyze_tpl = _read_prompt("analyze.txt")
    analyze_prompt = analyze_tpl.replace("{{TEXT}}", original)

    analysis_raw = client.generate(analyze_prompt, temperature=0.0)
    analysis = _safe_json(analysis_raw)

    needs = bool(analysis.get("needs_enhancement", False))
    apply = _normalize_apply(analysis.get("apply", []) or [])

    # Strength: allow UI default, but analyzer can override
    strength = (analysis.get("rewrite_strength") or rewrite_strength or "light").strip().lower()
    if strength not in {"light", "medium", "strong"}:
        strength = rewrite_strength or "light"

    # If no enhancement is needed, return original unchanged
    if (not needs) or (not apply):
        return {
            "original": original,
            "enhanced": original,
            "applied_principles": [],
            "changed": False,
            **({"analysis": analysis} if debug else {}),
        }

    # 2) Retrieve guidelines (deterministic file load)
    guidelines = load_guidelines(apply, SIX_CS_DIR)
    guidelines_block = "\n\n".join(
        [f"## {c.upper()}\n{guidelines[c]}" for c in apply if c in guidelines]
    ).strip()

    # 3) Enhance
    enhance_tpl = _read_prompt("enhance.txt")
    enhance_prompt = (
        enhance_tpl
        .replace("{{APPLY}}", ", ".join(apply))
        .replace("{{STRENGTH}}", strength)
        .replace("{{GUIDELINES}}", guidelines_block)
        .replace("{{TEXT}}", original)
    )

    enhanced = client.generate(enhance_prompt, temperature=0.2).strip()

    # Safety fallback
    if not enhanced:
        enhanced = original

    changed = enhanced.strip() != original.strip()

    return {
        "original": original,
        "enhanced": enhanced,
        "applied_principles": apply if changed else [],
        "changed": changed,
        **({"analysis": analysis} if debug else {}),
    }
