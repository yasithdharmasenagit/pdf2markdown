from openai import OpenAI
from .base import BaseProvider

class OpenAIProvider(BaseProvider):
    def __init__(self, api_key: str):
        super().__init__(api_key, model_name='gpt-4o-mini')
        self.client = OpenAI(api_key=self.api_key)

    def _execute_request(self, system_prompt: str, user_prompt: str) -> str:
        response = self.client.chat.completions.create(
            model=self.model_name,
            temperature=0.1,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ]
        )
        return response.choices[0].message.content