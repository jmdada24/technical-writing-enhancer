import re

def normalize_text(text: str) -> str:
    """
    Light, non-judgmental text normalization.
    No rules, no bias, no evaluation.
    """
    text = text.strip()
    text = re.sub(r"\s+", " ", text)
    return text.lower()
