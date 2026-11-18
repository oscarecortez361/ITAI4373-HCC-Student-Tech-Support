"""Local knowledge base of public HCC support guidance.

The data is a JSON snapshot of selected public HCC support pages, with the
source name and URL kept next to each entry. It is a snapshot, so if the HCC
pages change it has to be reverified and updated by hand. This module only
reads the file. Nothing here talks to HCC systems.
"""
import json
from pathlib import Path
from typing import Optional, Dict, Any

ROOT = Path(__file__).resolve().parents[1]
KB_FILE = ROOT / "data" / "hcc_knowledge_base.json"


def load_knowledge_base():
    """Read data/hcc_knowledge_base.json and return the list of entries."""
    with KB_FILE.open(encoding="utf-8") as f:
        return json.load(f)


def get_knowledge_entry(category: str) -> Optional[Dict[str, Any]]:
    """Return the knowledge base entry for a category, or None if there is none.

    category: a category name exactly as the classifier spells it.
    The file is small, so we reload it on each call instead of caching.
    """
    for entry in load_knowledge_base():
        if entry.get("category") == category:
            return entry
    return None
