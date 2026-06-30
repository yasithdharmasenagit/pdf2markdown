# providers/gemini.py
import time
import google.generativeai as genai
from . import BaseLLMProvider

class GeminiProvider(BaseLLMProvider):
    """Integrates Google's Gemini models with built-in retry resilience."""
    def __init__(self, api_key: str):
        super().__init__(api_key=api_key)
        genai.configure(api_key=self.api_key)
        self.model_name = "gemini-2.5-flash"

    def transform_text(self, raw_text: str) -> str:
        """Sends raw text to Gemini to turn it into structured Markdown."""
        system_instruction = (
            "You are an expert document translation engine. Your sole task is to take messy, raw text "
            "extracted from a PDF and restructure it into flawless, clean, and highly professional Markdown (.md).\n\n"
            "Rules:\n"
            "1. Preserve ALL original information, details, and text content accurately.\n"
            "2. Identify natural titles, sections, and lists and apply correct Markdown tags (#, ##, -, *, etc.).\n"
            "3. Reconstruct tables and tabular data into clean Markdown tables.\n"
            "4. Eliminate layout artifacts such as page numbers, repeating running headers, and running footers."
        )

        # Exponential backoff parameters: retry up to 5 times
        # Delays: 1s, 2s, 4s, 8s, 16s
        backoff_delays = [1, 2, 4, 8, 16]
        last_error = None

        for attempt, delay in enumerate(backoff_delays):
            try:
                model = genai.GenerativeModel(
                    model_name=self.model_name,
                    system_instruction=system_instruction
                )
                response = model.generate_content(raw_text)
                return response.text
            except Exception as e:
                last_error = e
                # Wait silently before retrying
                if attempt < len(backoff_delays) - 1:
                    time.sleep(delay)

        raise RuntimeError(
            f"Failed to process text using Gemini API after 5 attempts. Last Error: {last_error}"
        )