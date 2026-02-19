from typing import List, Dict
from pathlib import Path
from knowledge.registry import C_TO_FILE

def load_guidelines(selected_cs: List[str], six_cs_dir: Path) -> Dict[str, str]:
    docs: Dict[str, str] = {}
    for c in selected_cs:
        fname = C_TO_FILE.get(c)
        if not fname:
            continue
        path = six_cs_dir / fname
        if path.exists():
            docs[c] = path.read_text(encoding="utf-8").strip()
    return docs
