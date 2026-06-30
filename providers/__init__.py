# providers/__init__.py

class BaseLLMProvider:
    """Abstract base class establishing the contract for all AI translation models."""
    def __init__(self, api_key: str = None, api_base: str = None):
        self.api_key = api_key
        self.api_base = api_base

    def transform_text(self, raw_text: str) -> str:
        """Transforms raw layout text into clean markdown structures."""
        raise NotImplementedError("Each provider model must implement its own transformation logic.")

# Expose the providers cleanly so they can be imported directly from 'providers'
from .gemini import GeminiProvider
from .openai import OpenAIProvider
from .claude import ClaudeProvider
from .ollama import OllamaProvider