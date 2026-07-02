# providers/anthropic.py
import time
from anthropic import Anthropic

class AnthropicProvider:
    def __init__(self, api_key: str):
        if not api_key:
            raise ValueError("Anthropic API Key missing.")
        self.client = Anthropic(api_key=api_key)
        # Claude 3.5 Haiku is blazing fast and exceptional at structured markdown parsing
        self.model = "claude-3-5-haiku-20241022"

    def transform_text(self, raw_text: str, chunk_index: int = None) -> str:
        if not raw_text.strip():
            return ""

        max_retries = 5
        backoff_factor = 2

        for attempt in range(max_retries):
            try:
                response = self.client.messages.create(
                    model=self.model,
                    max_tokens=4000,
                    temperature=0.1,
                    system="You are an expert layout engineer. Convert raw text into clean Markdown. Do NOT add preamble. Output ONLY raw markdown.",
                    messages=[{"role": "user", "content": raw_text}]
                )
                return response.content[0].text
            except Exception as e:
                if "429" in str(e):
                    time.sleep(backoff_factor ** attempt)
                    continue
                raise e
        raise Exception(f"Anthropic failed to process chunk {chunk_index}")