import json
from abc import ABC
from typing import Dict, Any, Optional
from app.services.llm.base import LLMProvider, LLMMessage
from app.services.llm.factory import get_llm_provider


class BaseAgent(ABC):
    """Base class for autonomous specialized trading intelligence agents."""

    def __init__(self, llm_provider: Optional[LLMProvider] = None):
        self.llm = llm_provider or get_llm_provider()

    async def call_llm(self, system_prompt: str, user_content: str, temperature: float = 0.2) -> Dict[str, Any]:
        """Invoke LLM with system instructions and parse JSON payload safely."""
        messages = [
            LLMMessage(role="system", content=system_prompt),
            LLMMessage(role="user", content=user_content),
        ]
        raw_response = await self.llm.generate(messages, temperature=temperature, json_mode=True)
        try:
            return json.loads(raw_response)
        except Exception:
            # Attempt to extract JSON from markdown fencing if present
            clean = raw_response.strip()
            if "```json" in clean:
                clean = clean.split("```json")[1].split("```")[0].strip()
            elif "```" in clean:
                clean = clean.split("```")[1].split("```")[0].strip()
            return json.loads(clean)
