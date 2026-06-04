"""GILL VEDIO - Scheduling Manager

Blueprint suggests APScheduler to schedule publishing.

This implementation schedules a background job that calls SocialPublisher.

In Streamlit, long-running schedulers can be tricky; this module provides a
function to initialize scheduler inside app.py.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import List, Optional

from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.date import DateTrigger

import logging

logger = logging.getLogger(__name__)


@dataclass
class ScheduleConfig:
    interval_hours: float = 3.0
    platforms: Optional[List[str]] = None


def start_scheduler(publish_callback, interval_seconds: int = 10800) -> BackgroundScheduler:
    scheduler = BackgroundScheduler()
    scheduler.add_job(publish_callback, "interval", seconds=interval_seconds, max_instances=1, coalesce=True)
    scheduler.start()
    return scheduler

