"""GILL VEDIO - Config Manager

Wraps Settings operations:
- initialize vault
- save API keys
- save user profile in DB

UI uses these functions for consistent behavior.
"""

from __future__ import annotations

from typing import Optional

from database import save_user, update_user_preferences
from security import initialize_vault, save_api_key, verify_password, is_vault_initialized


def init_or_unlock_vault(master_password: str) -> bool:
    return initialize_vault(master_password)


def unlock_vault(master_password: str) -> bool:
    # initialize_vault already verifies password if vault exists.
    if not is_vault_initialized():
        return False
    return verify_password(master_password)


def save_user_profile(
    name: str,
    email: str = "",
    phone: str = "",
    niche: str = "",
    about_me: str = "",
    style_preference: str = "",
    avatar_path: str = "",
) -> int:
    return save_user(
        name=name,
        email=email,
        phone=phone,
        niche=niche,
        about_me=about_me,
        style_preference=style_preference,
        avatar_path=avatar_path,
    )


def save_api_provider_key(master_password: str, provider: str, api_key: str, tier: str = "free"):
    save_api_key(master_password=master_password, provider=provider, api_key=api_key, tier=tier)


def update_preferences(video_length: Optional[int] = None, model: Optional[str] = None, tier: Optional[str] = None):
    update_user_preferences(video_length=video_length, model=model, tier=tier)

