from pathlib import Path
try:
    from llama_cpp import Llama
except Exception:
    Llama = None

class LocalLLM:
    def __init__(self, model_path: str = 'models/tinyllama.bin'):
        self.model_path = model_path
        self.client = None
        if Llama:
            self.client = Llama(model_path=str(model_path))

    def generate(self, prompt: str, max_tokens: int = 128):
        if not self.client:
            return 'Local LLM not available.'
        out = self.client(prompt=prompt, max_tokens=max_tokens)
        return out.get('choices', [{}])[0].get('text', '')
