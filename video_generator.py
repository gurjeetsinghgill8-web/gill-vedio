"""GILL VEDIO - Video Generator wrapper."""

from __future__ import annotations

from typing import List, Dict

from llm_harness import Harness


def generate_videos(harness: Harness, selected_ideas: List[dict], duration_seconds: int, style: str = "", video_provider: str = None) -> List[Dict]:
    return harness.generate_videos(ideas=selected_ideas, duration_seconds=duration_seconds, style=style, video_provider=video_provider)

