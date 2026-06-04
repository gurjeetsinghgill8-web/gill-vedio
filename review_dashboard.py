"""GILL VEDIO - Review Dashboard logic (Streamlit UI helpers).

The actual Streamlit components live in app.py; this module contains state helpers.
"""

from __future__ import annotations

from typing import List, Dict


def toggle_selected(ideas: List[Dict], idea_id: int, selected: bool) -> None:
    for idea in ideas:
        if idea.get("id") == idea_id:
            idea["is_selected"] = 1 if selected else 0
            break

