"""
GILL VEDIO - Groq API Client
Free tier: Llama 3.3 70B — 30 requests/minute
Used for: Idea generation, captions, prompts, analysis
"""

import requests
import json
import logging
import time

logger = logging.getLogger(__name__)

GROQ_API_URL = "https://api.groq.com/openai/v1/chat/completions"

# Available free models
MODELS = {
    "llama-3.3-70b": "llama-3.3-70b-versatile",
    "llama-3.1-8b": "llama-3.1-8b-instant",
    "mixtral-8x7b": "mixtral-8x7b-32768",
    "gemma2-9b": "gemma2-9b-it",
}

DEFAULT_MODEL = "llama-3.3-70b"


class GroqClient:
    """Client for Groq's free LLM API."""

    def __init__(self, api_key: str, model: str = DEFAULT_MODEL):
        self.api_key = api_key
        self.model = MODELS.get(model, model)
        self.base_url = GROQ_API_URL
        self.headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        self._last_request_time = 0
        self._min_interval = 2.0  # 30 req/min = 2 sec between requests

    def _rate_limit(self):
        """Simple rate limiter to stay within free tier limits."""
        elapsed = time.time() - self._last_request_time
        if elapsed < self._min_interval:
            time.sleep(self._min_interval - elapsed)
        self._last_request_time = time.time()

    def chat(self, messages: list, temperature: float = 0.7, max_tokens: int = 2048) -> str:
        """
        Send a chat completion request.
        messages: [{"role": "system", "content": "..."}, {"role": "user", "content": "..."}]
        Returns: response text
        """
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
            logger.info(f"Groq response received ({len(content)} chars)")
            return content

        except requests.exceptions.RateLimitError:
            logger.warning("Groq rate limit hit, waiting 60 seconds...")
            time.sleep(60)
            return self.chat(messages, temperature, max_tokens)

        except requests.exceptions.HTTPError as e:
            logger.error(f"Groq HTTP error: {e}")
            if response.status_code == 429:
                retry_after = int(response.headers.get("retry-after", 60))
                logger.info(f"Rate limited. Retrying after {retry_after}s...")
                time.sleep(retry_after)
                return self.chat(messages, temperature, max_tokens)
            raise

        except Exception as e:
            logger.error(f"Groq request failed: {e}")
            raise

    def generate_json(self, messages: list, temperature: float = 0.7, max_tokens: int = 4096) -> dict:
        """
        Generate a JSON response (parsed from text).
        Adds instruction to return valid JSON.
        """
        system_msg = {
            "role": "system",
            "content": "You are a JSON generator. Always respond with valid JSON only. No markdown, no explanation, just raw JSON."
        }
        all_messages = [system_msg] + messages

        response_text = self.chat(all_messages, temperature, max_tokens)

        # Try to extract JSON from response
        try:
            # Remove markdown code blocks if present
            text = response_text.strip()
            if text.startswith("```"):
                text = text.split("\n", 1)[1] if "\n" in text else text[3:]
            if text.endswith("```"):
                text = text[:-3]
            text = text.strip()
            return json.loads(text)
        except json.JSONDecodeError:
            logger.warning("Failed to parse JSON from Groq response, returning raw text")
            return {"raw_response": response_text}

    def generate_ideas(self, topic: str, user_profile: str = "", count: int = 10) -> list:
        """Generate viral video ideas for a given topic."""
        messages = [
            {
                "role": "system",
                "content": """You are a viral content strategist for short-form video (Reels/Shorts).
You generate exactly 10 viral video ideas. Each idea must have:
- title: A catchy, click-worthy title (max 60 chars)
- hook: The first 3 seconds of the video to grab attention
- script_outline: Brief 3-4 line script structure
- viral_score: Rating 1-10 based on viral potential
- hashtags: List of 5 relevant trending hashtags

Return ONLY valid JSON array with exactly 10 objects. No other text."""
            },
            {
                "role": "user",
                "content": f"""Generate 10 viral short video ideas.

Topic: {topic}

Creator Profile: {user_profile if user_profile else 'Content creator making short-form videos'}

Return JSON array with 10 ideas. Each idea:
{{
    "title": "...",
    "hook": "...",
    "script_outline": "...",
    "viral_score": 8,
    "hashtags": ["#hashtag1", "#hashtag2", ...]
}}"""
            }
        ]

        result = self.generate_json(messages, temperature=0.85, max_tokens=4096)

        # Handle both array and object responses
        if isinstance(result, list):
            return result[:count]
        elif isinstance(result, dict) and "raw_response" in result:
            # Try to extract array from raw text
            import re
            match = re.search(r'\[.*\]', result["raw_response"], re.DOTALL)
            if match:
                try:
                    ideas = json.loads(match.group())
                    return ideas[:count]
                except:
                    pass
            return []
        elif isinstance(result, dict):
            # Maybe wrapped in a key
            for key in ["ideas", "video_ideas", "data"]:
                if key in result:
                    return result[key][:count]
            return []
        return []

    def generate_video_prompt(self, idea: dict, duration: int = 10, style: str = "") -> str:
        """Convert a video idea into an optimized prompt for Google Veo."""
        messages = [
            {
                "role": "system",
                "content": "You are a video prompt engineer for Google Veo AI video generation. Create detailed, cinematic video prompts that produce stunning visual content."
            },
            {
                "role": "user",
                "content": f"""Create a Google Veo video prompt for this idea:

Title: {idea.get('title', '')}
Hook: {idea.get('hook', '')}
Script: {idea.get('script_outline', '')}
Duration: {duration} seconds
Style: {style if style else 'cinematic, vibrant, professional'}

Requirements:
- Describe the visual scene in detail (camera angles, lighting, colors)
- Include motion and transitions
- Keep it under 200 words
- Make it compatible with Veo's prompt format
- Do NOT include any text overlays or captions in the prompt

Return ONLY the prompt text, nothing else."""
            }
        ]

        return self.chat(messages, temperature=0.7, max_tokens=1024)

    def generate_caption(self, idea: dict, platform: str = "instagram") -> dict:
        """Generate social media caption with hashtags."""
        messages = [
            {
                "role": "system",
                "content": "You are a social media copywriter. Generate engaging captions optimized for the given platform."
            },
            {
                "role": "user",
                "content": f"""Generate a caption for {platform}:

Video Title: {idea.get('title', '')}
Topic: {idea.get('topic', '')}

Return JSON:
{{
    "caption": "engaging caption text here",
    "hashtags": ["#tag1", "#tag2", "#tag3", "#tag4", "#tag5"],
    "cta": "call to action"
}}"""
            }
        ]

        return self.generate_json(messages, temperature=0.8, max_tokens=512)

    def test_connection(self) -> bool:
        """Test if the API key works."""
        try:
            response = self.chat([{"role": "user", "content": "Say 'OK' only."}], max_tokens=10)
            return "ok" in response.lower()
        except Exception as e:
            logger.error(f"Groq connection test failed: {e}")
            return False