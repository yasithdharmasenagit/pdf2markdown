from anthropic import Anthropic
from .base import BaseProvider

class AnthropicProvider(BaseProvider):
    def __init__(self, api_key: str):
        super().__init__(api_key, model_name='claude-3-5-haiku-20241022')
        self.client = Anthropic(api_key=self.api_key)

    def _execute_request(self, system_prompt: str, user_prompt: str) -> str:
        response = self.client.messages.create(
            model=self.model_name,
            max_tokens=4000,
            temperature=0.1,
            system=system_prompt,
            messages=[{"role": "user", "content": user_prompt}]
        )
        return response.content[0].text