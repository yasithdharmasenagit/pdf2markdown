# providers/claude.py
import time
from . import BaseLLMProvider

class ClaudeProvider(BaseLLMProvider):
    """Integrates Anthropic's Claude models (e.g., claude-3-5-sonnet) for structural translation."""
    def __init__(self, api_key: str, model_name: str = "claude-3-5-sonnet-latest"):
        super().__init__(api_key=api_key)
        self.model_name = model_name
        try:
            import anthropic
            self.client = anthropic.Anthropic(api_key=self.api_key)
        except ImportError:
            self.client = None

    def transform_text(self, raw_text: str) -> str:
        if not self.client:
            raise ImportError("The 'anthropic' library is not installed. Please run: pip install anthropic")

        system_instruction = (
            "You are an expert document translation engine. Convert this raw text extracted from a PDF "
            "into clean, structural Markdown. Preserve all info, design clean tables, and omit footer/header noise."
        )

        backoff_delays = [1, 2, 4, 8, 16]
        last_error = None

        for attempt, delay in enumerate(backoff_delays):
            try:
                response = self.client.messages.create(
                    model=self.model_name,
                    max_tokens=4096,
                    system=system_instruction,
                    messages=[
                        {"role": "user", "content": raw_text}
                    ]
                )
                return response.content[0].text
            except Exception as e:
                last_error = e
                if attempt < len(backoff_delays) - 1:
                    time.sleep(delay)

        raise RuntimeError(f"Claude transformation failed after 5 attempts. Last Error: {last_error}")