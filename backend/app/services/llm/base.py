from abc import ABC, abstractmethod
from typing import List, Dict, Any, Optional
from pydantic import BaseModel


class LLMMessage(BaseModel):
    role: str  # "system", "user", "assistant"
    content: str


class LLMProvider(ABC):
    """Abstract interface for LLM completion providers."""

    @abstractmethod
    async def generate(
        self,
        messages: List[LLMMessage],
        temperature: float = 0.2,
        json_mode: bool = False,
    ) -> str:
        """Generate response given a list of chat messages."""
        pass
