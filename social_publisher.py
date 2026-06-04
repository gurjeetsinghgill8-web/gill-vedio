"""GILL VEDIO - Social Publisher

Blueprint requires multi-platform publishing.

This project currently only has encrypted token storage.

This module implements:
- a safe publishing interface
- DB publish logging
- per-platform placeholder publishers (raise NotImplementedError with clear messages)

Once OAuth / API specifics are supplied, replace the stubs.
"""

from __future__ import annotations

import logging
import time
from typing import Dict, List, Optional

from database import (
    get_approved_videos,
    get_video,
    save_publish_log,
    update_publish_log,
)

logger = logging.getLogger(__name__)


class SocialPublisher:
    SUPPORTED_PLATFORMS = ["instagram", "facebook", "whatsapp", "youtube", "twitter"]

    def publish_video(self, video_id: int, platform: str, caption: str = "", hashtags: str = "") -> str:
        """Publish a video to a platform.

        Returns post URL if successful.
        """
        raise NotImplementedError("Platform publishers are not implemented yet. Use local preview or extend this module.")


class StubSocialPublisher(SocialPublisher):
    def publish_video(self, video_id: int, platform: str, caption: str = "", hashtags: str = "") -> str:
        # Stub implementation: mark failure but keep pipeline functional.
        raise RuntimeError(
            f"Publishing to {platform} is not wired in this build. Connect platform APIs and implement in social_publisher.py"
        )


def publish_batch(
    publisher: SocialPublisher,
    approved_video_ids: List[int],
    platforms: List[str],
    captions: Optional[Dict[int, Dict[str, str]]] = None,
) -> None:
    captions = captions or {}

    for video_id in approved_video_ids:
        video = get_video(video_id)
        if not video:
            continue

        for platform in platforms:
            cap = captions.get(video_id, {}).get("caption", "")
            tags = captions.get(video_id, {}).get("hashtags", "")

            log_id = save_publish_log(video_id=video_id, platform=platform, status="scheduled")
            try:
                post_url = publisher.publish_video(video_id=video_id, platform=platform, caption=cap, hashtags=tags)
                update_publish_log(log_id=log_id, status="published", published_at=time.strftime("%Y-%m-%d %H:%M:%S"), post_url=post_url)
            except Exception as e:
                update_publish_log(log_id=log_id, status="failed", error_message=str(e))

