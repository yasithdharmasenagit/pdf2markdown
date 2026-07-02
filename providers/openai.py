# providers/openai.py
import time
from openai import OpenAI

class OpenAIProvider:
    def __init__(self, api_key: str):
        if not api_key:
            raise ValueError("OpenAI API Key missing.")
        self.client = OpenAI(api_key=api_key)
        # Using gpt-4o-mini for incredible speed, low costs, and high structural accuracy
        self.model = "gpt-4o-mini"

    def transform_text(self, raw_text: str, chunk_index: int = None) -> str:
        if not raw_text.strip():
            return ""

        max_retries = 5
        backoff_factor = 2

        for attempt in range(max_retries):
            try:
                response = self.client.chat.completions.create(
                    model=self.model,
                    temperature=0.1,
                    messages=[
                        {"role": "system", "content": "You are an expert layout engineer. Convert raw text into clean Markdown. Do NOT add preamble. Output ONLY raw markdown."},
                        {"role": "user", "content": raw_text}
                    ]
                )
                return response.choices[0].message.content
            except Exception as e:
                if "429" in str(e): # Rate limit handler
                    time.sleep(backoff_factor ** attempt)
                    continue
                raise e
        raise Exception(f"OpenAI failed to process chunk {chunk_index}")