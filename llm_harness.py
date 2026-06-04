"""GILL VEDIO - LLM Harness (Orchestrator Brain)

Coordinates:
- user profile context retrieval
- ideation generation (10 ideas)
- video prompt generation
- captions / hashtags
- safety guardrails (lightweight checks)
- progress persistence to SQLite

This is intentionally model-agnostic; it uses LLMRouter + VeoClient.
"""

from __future__ import annotations

import json
import logging
from typing import Dict, List, Tuple

from database import (
    get_user,
    save_progress,
    save_message,
)
from models.llm_router import LLMRouter

# Veo is optional for development/testing; if no veo key exists we surface a clear error.
from models.veo_client import VeoClient
from models.fal_client import FalClient
from models.json2video_client import JSON2VideoClient
from security import get_api_key

logger = logging.getLogger(__name__)

FREE_STOCK_VIDEOS = [
    "https://vjs.zencdn.net/v/oceans.mp4",
    "https://www.w3schools.com/html/mov_bbb.mp4",
    "https://www.w3schools.com/html/movie.mp4"
]



class Guardrails:
    @staticmethod
    def validate_idea_text(idea: dict) -> None:
        # Minimal checks to prevent empty / obviously broken outputs.
        title = (idea.get("title") or "").strip()
        hook = (idea.get("hook") or "").strip()
        script_outline = (idea.get("script_outline") or "").strip()
        if not title or not hook or not script_outline:
            raise ValueError("Idea missing title/hook/script_outline")


class Harness:
    def __init__(self, master_password: str):
        self.master_password = master_password
        self.router = LLMRouter(master_password)

    def _get_veo_client(self) -> VeoClient:
        veo_key_data = get_api_key(self.master_password, "google_veo")
        if not veo_key_data:
            raise RuntimeError(
                "Google Veo key not configured. Add provider 'google_veo' in Settings."
            )
        return VeoClient(api_key=veo_key_data["key"])

    def _get_fal_client(self) -> FalClient:
        key_data = get_api_key(self.master_password, "fal_ai")
        if not key_data:
            raise RuntimeError(
                "Fal.ai key not configured. Add provider 'fal_ai' in Settings."
            )
        return FalClient(api_key=key_data["key"])

    def _get_json2video_client(self) -> JSON2VideoClient:
        key_data = get_api_key(self.master_password, "json2video")
        if not key_data:
            raise RuntimeError(
                "JSON2Video key not configured. Add provider 'json2video' in Settings."
            )
        return JSON2VideoClient(api_key=key_data["key"])

    def get_user_profile_context(self) -> str:
        user = get_user()
        if not user:
            return "Content creator making short-form videos"
        parts = [
            f"Name: {user.get('name','')}".strip(),
            f"Niche: {user.get('niche','')}".strip(),
            f"About: {user.get('about_me','')}".strip(),
            f"Style: {user.get('style_preference','')}".strip(),
        ]
        return "\n".join([p for p in parts if p])

    def generate_ideas(self, topic: str, count: int = 10, batch_step: str = "ideation") -> List[dict]:
        save_progress(batch_step, status="running", data={"topic": topic, "count": count})

        user_profile = self.get_user_profile_context()
        router_res = self.router.route_ideas()
        client = router_res.client

        save_message("user", f"Generate ideas for topic: {topic}", context_type="ideation", model_used=router_res.provider)
        ideas = client.generate_ideas(topic=topic, user_profile=user_profile, count=count)

        # Guardrails
        for idea in ideas:
            Guardrails.validate_idea_text(idea)

        save_message("assistant", json.dumps(ideas)[:2000], context_type="ideation", model_used=router_res.provider)
        save_progress(batch_step, status="completed", data={"topic": topic, "count": len(ideas)})
        return ideas

    def generate_video_prompt(self, idea: dict, duration_seconds: int, style: str = "") -> str:
        router_res = self.router.route_ideas()
        client = router_res.client

        prompt = client.generate_video_prompt(idea=idea, duration=duration_seconds, style=style)
        if not isinstance(prompt, str) or not prompt.strip():
            raise ValueError("Empty prompt generated")
        return prompt.strip()[:2000]

    def generate_caption(self, idea: dict, platform: str) -> Tuple[str, List[str], str]:
        router_res = self.router.route_caption()
        client = router_res.client

        data = client.generate_caption(idea=idea, platform=platform)
        caption = data.get("caption", "").strip()
        hashtags = data.get("hashtags", []) or []
        cta = data.get("cta", "").strip()
        return caption, hashtags, cta

    def generate_videos(self, ideas: List[dict], duration_seconds: int, style: str = "", video_provider: str = None) -> List[dict]:
        """Generate videos sequentially.

        Returns a list of dicts:
        {idea_id, prompt, veo_job_id, file_path, status}
        """

        import time

        if not video_provider:
            user = get_user()
            video_provider = user.get("video_provider", "mock") or "mock"

        # Initialize the selected client
        client = None
        if video_provider == "google_veo":
            client = self._get_veo_client()
        elif video_provider == "fal_ai":
            client = self._get_fal_client()
        elif video_provider == "json2video":
            client = self._get_json2video_client()

        outputs = []
        for i, idea in enumerate(ideas, start=1):
            idea_id = idea.get("id")
            prompt = self.generate_video_prompt(idea=idea, duration_seconds=duration_seconds, style=style)

            if client is not None:
                job = client.generate_video(prompt=prompt, duration_seconds=duration_seconds)
                job_id = job.job_id
                file_path = ""
            else:
                job_id = f"mock_job_{int(time.time())}_{idea_id}"
                
                # Download a free stock video to test player functionality
                from pathlib import Path
                import requests
                
                video_url = FREE_STOCK_VIDEOS[idea_id % len(FREE_STOCK_VIDEOS)]
                try:
                    output_dir = Path(__file__).parent / "output"
                    output_dir.mkdir(parents=True, exist_ok=True)
                    local_path = output_dir / f"video_idea_{idea_id}.mp4"
                    
                    logger.info(f"Downloading free stock video: {video_url}")
                    r = requests.get(video_url, stream=True, timeout=30)
                    if r.status_code == 200:
                        with open(local_path, 'wb') as f:
                            for chunk in r.iter_content(chunk_size=1024*1024):
                                if chunk:
                                    f.write(chunk)
                        file_path = f"output/video_idea_{idea_id}.mp4"
                        logger.info(f"Successfully downloaded stock video to {file_path}")
                    else:
                        file_path = ""
                except Exception as ex:
                    logger.error(f"Failed to download mock video: {ex}")
                    file_path = ""

            # In a real pipeline we would download output and save local file.
            # For now we persist metadata and mark as completed when polling succeeds.
            # Users can extend download logic once their Veo API is connected.
            outputs.append(
                {
                    "idea_id": idea_id,
                    "prompt": prompt,
                    "veo_job_id": job_id,
                    "status": "submitted",
                    "file_path": file_path,
                }
            )

        return outputs

