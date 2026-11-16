import json
from pathlib import Path
from typing import Optional, Dict, Any

ROOT = Path(__file__).resolve().parents[1]
KB_FILE = ROOT / "data" / "hcc_knowledge_base.json"


def load_knowledge_base():
    with KB_FILE.open(encoding="utf-8") as f:
        return json.load(f)


def get_knowledge_entry(category: str) -> Optional[Dict[str, Any]]:
    for entry in load_knowledge_base():
        if entry.get("category") == category:
            return entry
    return None
