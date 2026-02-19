from typing import Optional
import ollama

class OllamaClient:
    def __init__(self, model: str):
        self.model = model

    def generate(self, prompt: str, system: Optional[str] = None, temperature: float = 0.2) -> str:
        messages = []
        if system:
            messages.append({"role": "system", "content": system})
        messages.append({"role": "user", "content": prompt})

        resp = ollama.chat(
            model=self.model,
            messages=messages,
            options={"temperature": temperature},
        )
        return (resp["message"]["content"] or "").strip()
