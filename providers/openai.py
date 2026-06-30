# providers/openai.py
import time
from . import BaseLLMProvider

class OpenAIProvider(BaseLLMProvider):
    """Integrates OpenAI GPT models (e.g., gpt-4o, gpt-4o-mini) for layout reconstruction."""
    def __init__(self, api_key: str, model_name: str = "gpt-4o-mini"):
        super().__init__(api_key=api_key)
        self.model_name = model_name
        # Lazy import of the openai library to prevent errors if not installed
        try:
            import openai
            self.client = openai.OpenAI(api_key=self.api_key)
        except ImportError:
            self.client = None

    def transform_text(self, raw_text: str) -> str:
        if not self.client:
            raise ImportError("The 'openai' library is not installed. Please run: pip install openai")

        system_instruction = (
            "You are an expert document translation engine. Convert this raw text extracted from a PDF "
            "into clean, structural Markdown. Preserve all info, design clean tables, and omit footer/header noise."
        )

        backoff_delays = [1, 2, 4, 8, 16]
        last_error = None

        for attempt, delay in enumerate(backoff_delays):
            try:
                response = self.client.chat.completions.create(
                    model=self.model_name,
                    messages=[
                        {"role": "system", "content": system_instruction},
                        {"role": "user", "content": raw_text}
                    ]
                )
                return response.choices[0].message.content
            except Exception as e:
                last_error = e
                if attempt < len(backoff_delays) - 1:
                    time.sleep(delay)

        raise RuntimeError(f"OpenAI transformation failed after 5 attempts. Last Error: {last_error}")