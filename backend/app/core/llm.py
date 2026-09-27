import os
import json
import logging
import httpx
from typing import Dict, Any, List, Optional
from app.core.config import settings

logger = logging.getLogger("factcheck.llm")

class LLMClient:
    def __init__(self):
        self.provider = settings.LLM_PROVIDER
        self.ollama_base = settings.OLLAMA_BASE_URL
        self.ollama_model = settings.OLLAMA_MODEL
        self.openai_key = settings.OPENAI_API_KEY
        self.gemini_key = settings.GEMINI_API_KEY
        
    async def is_ollama_available(self) -> bool:
        try:
            async with httpx.AsyncClient(timeout=1.5) as client:
                res = await client.get(f"{self.ollama_base}/api/tags")
                return res.status_code == 200
        except Exception:
            return False

    async def generate_json(self, prompt: str, system_prompt: str, fallback_func=None) -> Dict[str, Any]:
        """Calls the configured LLM and parses JSON output, falling back gracefully."""
        # Check active provider
        if self.provider == "auto":
            if self.openai_key:
                active_provider = "openai"
            elif self.gemini_key:
                active_provider = "gemini"
            elif await self.is_ollama_available():
                active_provider = "ollama"
            else:
                active_provider = "mock"
        else:
            active_provider = self.provider

        if active_provider == "ollama":
            try:
                async with httpx.AsyncClient(timeout=3.0) as client:
                    resp = await client.post(
                        f"{self.ollama_base}/api/generate",
                        json={
                            "model": self.ollama_model,
                            "prompt": f"{system_prompt}\n\nUser:\n{prompt}\n\nRespond ONLY with valid JSON conforming to the requested schema. No markdown formatting around the JSON.",
                            "stream": False,
                            "format": "json"
                        }
                    )
                    if resp.status_code == 200:
                        data = resp.json()
                        text = data.get("response", "{}")
                        return json.loads(text)
            except Exception as e:
                logger.info(f"Using local deterministic reasoning engine ({e})")

        elif active_provider == "openai" and self.openai_key:
            try:
                async with httpx.AsyncClient(timeout=25.0) as client:
                    resp = await client.post(
                        "https://api.openai.com/v1/chat/completions",
                        headers={"Authorization": f"Bearer {self.openai_key}"},
                        json={
                            "model": settings.OPENAI_MODEL,
                            "messages": [
                                {"role": "system", "content": system_prompt},
                                {"role": "user", "content": prompt}
                            ],
                            "response_format": {"type": "json_object"}
                        }
                    )
                    if resp.status_code == 200:
                        content = resp.json()["choices"][0]["message"]["content"]
                        return json.loads(content)
            except Exception as e:
                logger.warning(f"OpenAI call failed ({e}), falling back.")

        # Fallback to local deterministic reasoning function
        if fallback_func:
            return fallback_func()
        return {}

llm_client = LLMClient()
