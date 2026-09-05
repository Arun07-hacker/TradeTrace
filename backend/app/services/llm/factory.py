from app.core.config import settings
from app.services.llm.base import LLMProvider
from app.services.llm.mock_provider import MockLLMProvider


_llm_provider_instance: LLMProvider = None


def get_llm_provider() -> LLMProvider:
    """Singleton factory returning the configured LLM provider."""
    global _llm_provider_instance
    if _llm_provider_instance is None:
        if settings.LLM_PROVIDER.lower() == "mock":
            _llm_provider_instance = MockLLMProvider()
        else:
            # Fallback to MockLLMProvider for now; can be extended for OpenAI / Anthropic / Gemini
            _llm_provider_instance = MockLLMProvider()
    return _llm_provider_instance
