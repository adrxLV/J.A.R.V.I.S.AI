import requests
import json

class StreamingOllama:
    def __init__(self, model="mistral", base_url="http://localhost:11434"):
        self.model = model
        self.base_url = base_url

    def generate_stream(self, prompt):
        url = f"{self.base_url}/api/generate"
        data = {"model": self.model, "prompt": prompt, "stream": True}
        try:
            response = requests.post(url, json=data, stream=True, timeout=120)
            response.raise_for_status()
            for line in response.iter_lines():
                if line:
                    try:
                        part = json.loads(line.decode("utf-8"))
                        token = part.get("response", "")
                        if token:
                            yield token
                    except Exception:
                        continue
        except Exception as e:
            yield f"[streaming error: {e}]"