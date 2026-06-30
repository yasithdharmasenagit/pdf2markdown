# providers/ollama.py
import requests
from . import BaseLLMProvider

class OllamaProvider(BaseLLMProvider):
    """Integrates local offline models running via Ollama (e.g., llama3, mistral)."""
    def __init__(self, model_name: str = "llama3", api_base: str = "http://localhost:11434"):
        super().__init__(api_base=api_base)
        self.model_name = model_name

    def transform_text(self, raw_text: str) -> str:
        """Sends raw text to your local Ollama instance for offline processing."""
        url = f"{self.api_base}/api/generate"
        
        system_instruction = (
            "You are an expert document translation engine. Convert this raw text extracted from a PDF "
            "into clean, structural Markdown. Preserve all info, design clean tables, and omit footer/header noise."
        )

        payload = {
            "model": self.model_name,
            "prompt": f"{system_instruction}\n\nDocument Raw Text:\n{raw_text}",
            "stream": False
        }

        try:
            response = requests.post(url, json=payload, timeout=120)
            response.raise_for_status()
            return response.json().get("response", "")
        except Exception as e:
            raise RuntimeError(f"Failed to reach local Ollama engine: {str(e)}")