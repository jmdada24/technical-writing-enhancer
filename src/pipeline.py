import json
import re
from typing import Dict, Any, List

from config import GROQ_MODEL, SIX_CS_DIR, PROMPTS_DIR
from llm_client import GroqClient
from knowledge.loader import load_guidelines


ALLOWED_CS = {
    "clarity",
    "completeness",
    "conciseness",
    "concreteness",
    "consistency",
    "courtesy",
}


def _read_prompt(name: str) -> str:
    path = PROMPTS_DIR / name
    return path.read_text(encoding="utf-8")


def _extract_json_object(text: str) -> str:
    t = text.strip()

    # Remove ```json fences
    if t.startswith("```"):
        t = re.sub(r"^```(?:json)?\s*", "", t.strip(), flags=re.IGNORECASE)
        t = re.sub(r"\s*```$", "", t.strip())

    try:
        json.loads(t)
        return t
    except Exception:
        pass

    start = t.find("{")
    end = t.rfind("}")
    if start != -1 and end != -1 and end > start:
        return t[start:end + 1].strip()

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


def run_pipeline(
    user_text: str,
    rewrite_strength: str = "light",
    debug: bool = False
) -> Dict[str, Any]:

    original = (user_text or "").strip()

    if not original:
        return {
            "original": "",
            "enhanced": "",
            "applied_principles": [],
            "changed": False,
            "notes": [],
            **({"analysis": {}} if debug else {}),
        }

    client = GroqClient(model=GROQ_MODEL)

    # 🔹 LOAD ALL GUIDELINES FOR ANALYSIS PHASE
    all_cs = [
        "clarity",
        "completeness",
        "conciseness",
        "concreteness",
        "consistency",
        "courtesy",
    ]

    all_guidelines = load_guidelines(all_cs, SIX_CS_DIR)

    guidelines_block = "\n\n".join(
        [f"## {c.upper()}\n{all_guidelines[c]}" for c in all_cs if c in all_guidelines]
    ).strip()

    # 🔹 ANALYZE
    analyze_tpl = _read_prompt("analyze.txt")

    analyze_prompt = (
        analyze_tpl
        .replace("{{GUIDELINES}}", guidelines_block)
        .replace("{{TEXT}}", original)
    )

    analysis_raw = client.generate(analyze_prompt, temperature=0.0)
    analysis = _safe_json(analysis_raw)

    needs = bool(analysis.get("needs_enhancement", False))
    apply = _normalize_apply(analysis.get("apply", []) or [])

    strength = (
        analysis.get("rewrite_strength") or rewrite_strength or "light"
    ).strip().lower()

    if strength not in {"light", "medium", "strong"}:
        strength = rewrite_strength or "light"

    notes = analysis.get("notes", []) if isinstance(analysis, dict) else []

    # 🔹 If no enhancement needed
    if (not needs) or (not apply):
        return {
            "original": original,
            "enhanced": original,
            "applied_principles": [],
            "changed": False,
            "notes": notes,
            **({"analysis": analysis} if debug else {}),
        }

    # 🔹 Load only selected guidelines for enhancement
    selected_guidelines = load_guidelines(apply, SIX_CS_DIR)

    selected_block = "\n\n".join(
        [f"## {c.upper()}\n{selected_guidelines[c]}" for c in apply if c in selected_guidelines]
    ).strip()

    # 🔹 ENHANCE
    enhance_tpl = _read_prompt("enhance.txt")

    enhance_prompt = (
        enhance_tpl
        .replace("{{APPLY}}", ", ".join(apply))
        .replace("{{STRENGTH}}", strength)
        .replace("{{GUIDELINES}}", selected_block)
        .replace("{{TEXT}}", original)
    )

    enhanced = client.generate(enhance_prompt, temperature=0.2).strip()

    if not enhanced:
        enhanced = original

    changed = enhanced.strip() != original.strip()

    return {
        "original": original,
        "enhanced": enhanced,
        "applied_principles": apply if changed else [],
        "changed": changed,
        "notes": notes if changed else [],
        **({"analysis": analysis} if debug else {}),
    }