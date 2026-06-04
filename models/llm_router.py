"""GILL VEDIO - LLM Router

Routes between available free LLM providers (Groq/Gemini/Nvidia) based on tier and
configured master-password vault keys.

Paid-model routing is left as a simple extension point: if a paid key exists in the
vault for a provider, it will be preferred.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Optional

from models.groq_client import GroqClient
from models.gemini_client import GeminiClient
from models.nvidia_client import NvidiaClient
from security import get_api_key


@dataclass
class RouterResult:
    client: object
    provider: str
    tier: str


class LLMRouter:
    """Central router for free-tier LLMs."""

    FREE_PROVIDER_ORDER = ["groq", "gemini", "nvidia"]

    def __init__(self, master_password: str):
        self.master_password = master_password

    def _make_client(self, provider: str) -> Optional[RouterResult]:
        key_data = get_api_key(self.master_password, provider)
        if not key_data:
            return None

        api_key = key_data["key"]
        tier = key_data.get("tier", "free")

        if provider == "groq":
            # client accepts a model string, but we store only tier/key here; keep default model.
            return RouterResult(client=GroqClient(api_key=api_key), provider=provider, tier=tier)
        if provider == "gemini":
            return RouterResult(client=GeminiClient(api_key=api_key), provider=provider, tier=tier)
        if provider == "nvidia":
            return RouterResult(client=NvidiaClient(api_key=api_key), provider=provider, tier=tier)

        return None

    def route_ideas(self) -> RouterResult:
        """Route for ideation (returns a ready client)."""
        for provider in self.FREE_PROVIDER_ORDER:
            res = self._make_client(provider)
            if res:
                return res
        raise RuntimeError(
            "No LLM API keys found. Add one of: groq, gemini, nvidia in Settings first."
        )

    def route_caption(self) -> RouterResult:
        """Route for caption generation."""
        return self.route_ideas()

