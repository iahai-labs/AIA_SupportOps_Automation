from __future__ import annotations

import json
from abc import ABC, abstractmethod

import httpx

from app.core.config import settings


class LLMProvider(ABC):
    @abstractmethod
    def complete_json(self, *, system_prompt: str, user_prompt: str) -> dict[str, object]:
        raise NotImplementedError


class OpenAICompatibleProvider(LLMProvider):
    def complete_json(self, *, system_prompt: str, user_prompt: str) -> dict[str, object]:
        if not settings.ai_api_key:
            raise RuntimeError("AI_API_KEY is not configured")

        url = f"{settings.ai_base_url.rstrip('/')}/chat/completions"
        headers = {
            "Authorization": f"Bearer {settings.ai_api_key}",
            "Content-Type": "application/json",
        }
        payload = {
            "model": settings.ai_model,
            "temperature": 0,
            "response_format": {"type": "json_object"},
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt},
            ],
        }

        with httpx.Client(timeout=settings.ai_timeout_seconds) as client:
            response = client.post(url, headers=headers, json=payload)
            response.raise_for_status()
            data = response.json()

        content = data["choices"][0]["message"]["content"]
        parsed = json.loads(content)
        if not isinstance(parsed, dict):
            raise ValueError("LLM response must be a JSON object")
        return parsed
