"""
GILL VEDIO - Nvidia NIM API Client
Free tier: Llama 3.1 8B and other models — 50 requests/minute
Used for: Quick tasks, classification, simple generation
"""

import requests
import json
import logging
import time

logger = logging.getLogger(__name__)

NVIDIA_API_URL = "https://integrate.api.nvidia.com/v1/chat/completions"

MODELS = {
    "llama-3.1-8b": "meta/llama-3.1-8b-instruct",
    "llama-3.1-70b": "meta/llama-3.1-70b-instruct",
    "mistral-7b": "mistralai/mistral-7b-instruct-v0.3",
    "phi-3-mini": "microsoft/phi-3-mini-128k-instruct",
}

DEFAULT_MODEL = "llama-3.1-8b"


class NvidiaClient:
    """Client for Nvidia NIM free LLM API."""

    def __init__(self, api_key: str, model: str = DEFAULT_MODEL):
        self.api_key = api_key
        self.model = MODELS.get(model, model)
        self.base_url = NVIDIA_API_URL
        self.headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        self._last_request_time = 0
        self._min_interval = 1.2  # 50 req/min

    def _rate_limit(self):
        elapsed = time.time() - self._last_request_time
        if elapsed < self._min_interval:
            time.sleep(self._min_interval - elapsed)
        self._last_request_time = time.time()

    def chat(self, messages: list, temperature: float = 0.7, max_tokens: int = 2048) -> str:
        """Send chat completion request to Nvidia NIM."""
        self._rate_limit()

        payload = {
            "model": self.model,
            "messages": messages,
            "temperature": temperature,
            "max_tokens": max_tokens,
            "stream": False
        }

        try:
            response = requests.post(
                self.base_url,
                headers=self.headers,
                json=payload,
                timeout=60
            )
            response.raise_for_status()
            data = response.json()
            content = data["choices"][0]["message"]["content"]
            logger.info(f"Nvidia response received ({len(content)} chars)")
            return content

        except requests.exceptions.HTTPError as e:
            logger.error(f"Nvidia HTTP error: {e}")
            if response.status_code == 429:
                time.sleep(60)
                return self.chat(messages, temperature, max_tokens)
            raise
        except Exception as e:
            logger.error(f"Nvidia request failed: {e}")
            raise

    def generate_json(self, messages: list, temperature: float = 0.7, max_tokens: int = 4096) -> dict:
        """Generate JSON response."""
        system_msg = {
            "role": "system",
            "content": "Respond with valid JSON only. No markdown, no explanation."
        }
        response_text = self.chat([system_msg] + messages, temperature, max_tokens)

        try:
            text = response_text.strip()
            if text.startswith("```"):
                text = text.split("\n", 1)[1] if "\n" in text else text[3:]
            if text.endswith("```"):
                text = text[:-3]
            return json.loads(text.strip())
        except json.JSONDecodeError:
            return {"raw_response": response_text}

    def generate_ideas(self, topic: str, user_profile: str = "", count: int = 10) -> list:
        """Generate viral video ideas."""
        messages = [
            {
                "role": "system",
                "content": "You are a viral content strategist. Generate exactly 10 video ideas as JSON array. Each: title, hook, script_outline, viral_score (1-10), hashtags (5)."
            },
            {
                "role": "user",
                "content": f"Generate 10 viral short video ideas.\nTopic: {topic}\nCreator: {user_profile or 'Video creator'}\nReturn JSON array only."
            }
        ]
        result = self.generate_json(messages, temperature=0.85, max_tokens=4096)
        if isinstance(result, list):
            return result[:count]
        elif isinstance(result, dict):
            if "raw_response" in result:
                import re
                match = re.search(r'\[.*\]', result["raw_response"], re.DOTALL)
                if match:
                    try:
                        return json.loads(match.group())[:count]
                    except:
                        pass
        return []

    def test_connection(self) -> bool:
        """Test API key."""
        try:
            response = self.chat([{"role": "user", "content": "Say 'OK' only."}], max_tokens=10)
            return "ok" in response.lower()
        except Exception as e:
            logger.error(f"Nvidia connection test failed: {e}")
            return False