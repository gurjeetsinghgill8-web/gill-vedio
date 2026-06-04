"""
GILL VEDIO - Google Gemini API Client
Free tier: Gemini 2.0 Flash — 15 requests/minute
Used for: Idea generation, analysis, video prompts
"""

import requests
import json
import logging
import time

logger = logging.getLogger(__name__)

GEMINI_API_URL = "https://generativelanguage.googleapis.com/v1beta/models"

MODELS = {
    "gemini-2.0-flash": "gemini-2.0-flash",
    "gemini-1.5-flash": "gemini-1.5-flash",
    "gemini-1.5-pro": "gemini-1.5-pro",
}

DEFAULT_MODEL = "gemini-2.0-flash"


class GeminiClient:
    """Client for Google Gemini free LLM API."""

    def __init__(self, api_key: str, model: str = DEFAULT_MODEL):
        self.api_key = api_key
        self.model = MODELS.get(model, model)
        self._last_request_time = 0
        self._min_interval = 4.0  # 15 req/min = 4 sec between requests

    def _rate_limit(self):
        """Rate limiter for free tier."""
        elapsed = time.time() - self._last_request_time
        if elapsed < self._min_interval:
            time.sleep(self._min_interval - elapsed)
        self._last_request_time = time.time()

    def _build_url(self) -> str:
        return f"{GEMINI_API_URL}/{self.model}:generateContent?key={self.api_key}"

    def chat(self, messages: list, temperature: float = 0.7, max_tokens: int = 2048) -> str:
        """
        Send a chat request to Gemini.
        messages: [{"role": "system"/"user"/"assistant", "content": "..."}]
        """
        self._rate_limit()

        # Convert OpenAI-style messages to Gemini format
        system_instruction = ""
        contents = []
        for msg in messages:
            if msg["role"] == "system":
                system_instruction = msg["content"]
            elif msg["role"] == "user":
                contents.append({"role": "user", "parts": [{"text": msg["content"]}]})
            elif msg["role"] == "assistant":
                contents.append({"role": "model", "parts": [{"text": msg["content"]}]})

        payload = {
            "contents": contents,
            "generationConfig": {
                "temperature": temperature,
                "maxOutputTokens": max_tokens,
            }
        }

        if system_instruction:
            payload["systemInstruction"] = {
                "parts": [{"text": system_instruction}]
            }

        try:
            response = requests.post(
                self._build_url(),
                json=payload,
                timeout=60
            )
            response.raise_for_status()
            data = response.json()

            # Extract text from response
            content = data["candidates"][0]["content"]["parts"][0]["text"]
            logger.info(f"Gemini response received ({len(content)} chars)")
            return content

        except requests.exceptions.HTTPError as e:
            logger.error(f"Gemini HTTP error: {e}")
            if response.status_code == 429:
                logger.warning("Gemini rate limit hit, waiting 60 seconds...")
                time.sleep(60)
                return self.chat(messages, temperature, max_tokens)
            raise

        except Exception as e:
            logger.error(f"Gemini request failed: {e}")
            raise

    def generate_json(self, messages: list, temperature: float = 0.7, max_tokens: int = 4096) -> dict:
        """Generate a JSON response."""
        system_msg = {
            "role": "system",
            "content": "You are a JSON generator. Always respond with valid JSON only. No markdown, no explanation."
        }
        all_messages = [system_msg] + messages

        response_text = self.chat(all_messages, temperature, max_tokens)

        try:
            text = response_text.strip()
            if text.startswith("```"):
                text = text.split("\n", 1)[1] if "\n" in text else text[3:]
            if text.endswith("```"):
                text = text[:-3]
            text = text.strip()
            return json.loads(text)
        except json.JSONDecodeError:
            logger.warning("Failed to parse JSON from Gemini response")
            return {"raw_response": response_text}

    def generate_ideas(self, topic: str, user_profile: str = "", count: int = 10) -> list:
        """Generate viral video ideas."""
        messages = [
            {
                "role": "system",
                "content": """You are a viral content strategist for short-form video.
Generate exactly 10 viral video ideas as a JSON array.
Each idea: title, hook, script_outline, viral_score (1-10), hashtags (list of 5).
Return ONLY valid JSON array."""
            },
            {
                "role": "user",
                "content": f"""Generate 10 viral short video ideas.

Topic: {topic}
Creator: {user_profile if user_profile else 'Short-form video creator'}

Return JSON array only:
[
  {{
    "title": "catchy title (max 60 chars)",
    "hook": "first 3 seconds attention grabber",
    "script_outline": "3-4 line script structure",
    "viral_score": 8,
    "hashtags": ["#tag1", "#tag2", "#tag3", "#tag4", "#tag5"]
  }}
]"""
            }
        ]

        result = self.generate_json(messages, temperature=0.85, max_tokens=4096)

        if isinstance(result, list):
            return result[:count]
        elif isinstance(result, dict):
            for key in ["raw_response"]:
                if key in result:
                    import re
                    match = re.search(r'\[.*\]', result[key], re.DOTALL)
                    if match:
                        try:
                            return json.loads(match.group())[:count]
                        except:
                            pass
            for key in ["ideas", "video_ideas", "data"]:
                if key in result:
                    return result[key][:count]
        return []

    def generate_video_prompt(self, idea: dict, duration: int = 10, style: str = "") -> str:
        """Convert idea to Veo video prompt."""
        messages = [
            {
                "role": "system",
                "content": "You are a video prompt engineer for Google Veo. Create detailed cinematic prompts."
            },
            {
                "role": "user",
                "content": f"""Create a Google Veo video prompt:

Title: {idea.get('title', '')}
Hook: {idea.get('hook', '')}
Script: {idea.get('script_outline', '')}
Duration: {duration}s
Style: {style if style else 'cinematic, vibrant'}

Create a detailed visual prompt with camera angles, lighting, colors, motion. Under 200 words. No text overlays.
Return ONLY the prompt text."""
            }
        ]
        return self.chat(messages, temperature=0.7, max_tokens=1024)

    def generate_caption(self, idea: dict, platform: str = "instagram") -> dict:
        """Generate social media caption."""
        messages = [
            {
                "role": "system",
                "content": "You are a social media copywriter. Return JSON only."
            },
            {
                "role": "user",
                "content": f"""Generate {platform} caption for: {idea.get('title', '')}

Return JSON: {{"caption": "...", "hashtags": ["#t1", "#t2"], "cta": "..."}}"""
            }
        ]
        return self.generate_json(messages, temperature=0.8, max_tokens=512)

    def test_connection(self) -> bool:
        """Test API key."""
        try:
            response = self.chat([{"role": "user", "content": "Say 'OK' only."}], max_tokens=10)
            return "ok" in response.lower()
        except Exception as e:
            logger.error(f"Gemini connection test failed: {e}")
            return False