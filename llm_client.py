import subprocess
import re

class OllamaClient:
    def __init__(self, model_name: str = "llama3"):
        self.model_name = model_name

    def generate(self, prompt: str) -> str:
        try:
            proc = subprocess.run(
                ["ollama", "run", self.model_name],
                input=prompt,
                capture_output=True,
                text=True,
                check=True
            )
            return self._clean_output(proc.stdout)
        except subprocess.CalledProcessError as e:
            raise RuntimeError(f"Ollama error: {e.stderr.strip()}")

    def _clean_output(self, response: str) -> str:
        # Clean terminal escape sequences
        response = re.sub(r'\x1B(?:[@-Z\\-_]|\[[0-?]*[ -/]*[@-~])', '', response)
        response = re.sub(r'\n{3,}', '\n\n', response)
        return response.strip()


