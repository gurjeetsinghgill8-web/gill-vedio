"""GILL VEDIO - Idea Generator wrapper.

Kept as a separate module for blueprint alignment.
"""

from __future__ import annotations

from typing import List, Dict

from llm_harness import Harness


def generate_10_ideas(harness: Harness, topic: str) -> List[Dict]:
    return harness.generate_ideas(topic=topic, count=10, batch_step="ideation")

