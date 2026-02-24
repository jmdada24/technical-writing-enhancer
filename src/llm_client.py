from typing import Optional
from groq import Groq
from config import GROQ_API_KEY, GROQ_MODEL

class GroqClient:
    def __init__(self, model: str = GROQ_MODEL):
        self.client = Groq(api_key=GROQ_API_KEY)
        self.model = model

    def generate(self, prompt: str, system: Optional[str] = None, temperature: float = 0.2) -> str:
        messages = []
        if system:
            messages.append({"role": "system", "content": system})
        messages.append({"role": "user", "content": prompt})

        resp = self.client.chat.completions.create(
            model=self.model,
            messages=messages,
            temperature=temperature,
        )
        return (resp.choices[0].message.content or "").strip()