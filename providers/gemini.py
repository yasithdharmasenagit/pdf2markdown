import google.generativeai as genai
from .base import BaseProvider

class GeminiProvider(BaseProvider):
    def __init__(self, api_key: str):
        super().__init__(api_key, model_name='gemini-2.5-flash')
        genai.configure(api_key=self.api_key)
        self.model = genai.GenerativeModel(self.model_name)

    def _execute_request(self, system_prompt: str, user_prompt: str) -> str:
        # Combine system parameters natively into the execution call context
        full_prompt = f"{system_prompt}\n\n--- RAW TEXT BLOCK ---\n{user_prompt}"
        response = self.model.generate_content(full_prompt)
        if response.text:
            return response.text
        raise ValueError("Empty string payload received back from Google AI Studio.")