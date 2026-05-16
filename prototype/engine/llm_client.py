"""
Ollama LLM Client.

Sends structured prompts to a locally running Ollama instance.
No external dependencies — uses Python's built-in urllib only.

Default model: phi (Phi-2, already installed).
Default endpoint: http://localhost:11434

The LLM is used ONLY for WHY construction.
All scoring, constraint matching, and decision logic
remain deterministic Python — the LLM is a non-critical
explainer with a template fallback.

Original concept: Sami Ahmed Yusuf Kolarkar, 2026.
"""

import json
import urllib.request
import urllib.error
from typing import Optional


class OllamaClient:
    """
    Minimal HTTP client for Ollama's /api/generate endpoint.

    Usage:
        client = OllamaClient()
        response = client.generate("Explain why...")
        if response:
            print(response)
        else:
            # Ollama unavailable — use fallback
    """

    def __init__(
        self,
        model: str = "phi",
        host: str = "http://localhost:11434",
        timeout: int = 60,
    ):
        self.model = model
        self.endpoint = f"{host}/api/generate"
        self.timeout = timeout

    def generate(self, prompt: str, max_tokens: int = 300) -> Optional[str]:
        """
        Send a prompt to Ollama and return the response text.

        Returns None if Ollama is unreachable or returns an error.
        Callers must handle None and use a fallback.

        Args:
            prompt:     The full prompt string
            max_tokens: Approximate response length limit

        Returns:
            Response text, or None on failure.
        """
        payload = json.dumps({
            "model": self.model,
            "prompt": prompt,
            "stream": False,
            "options": {
                "num_predict": max_tokens,
                "temperature": 0.3,   # Low temp for consistent reasoning
                "top_p": 0.9,
            },
        }).encode("utf-8")

        request = urllib.request.Request(
            self.endpoint,
            data=payload,
            headers={"Content-Type": "application/json"},
            method="POST",
        )

        try:
            with urllib.request.urlopen(request, timeout=self.timeout) as resp:
                body = json.loads(resp.read().decode("utf-8"))
                return body.get("response", "").strip()
        except urllib.error.URLError:
            return None
        except (json.JSONDecodeError, KeyError):
            return None
        except Exception:
            return None

    def is_available(self) -> bool:
        """Check if Ollama is running and the model is loaded."""
        try:
            req = urllib.request.Request(
                self.endpoint.replace("/api/generate", "/api/tags"),
                method="GET",
            )
            with urllib.request.urlopen(req, timeout=5) as resp:
                body = json.loads(resp.read().decode("utf-8"))
                models = [m["name"] for m in body.get("models", [])]
                return any(self.model in m for m in models)
        except Exception:
            return False


class MockLLMClient:
    """
    Drop-in replacement for OllamaClient in tests.
    Returns a fixed response without making any HTTP calls.
    """

    def __init__(self, response: str = "Mock WHY explanation for testing."):
        self._response = response

    def generate(self, prompt: str, max_tokens: int = 300) -> Optional[str]:
        return self._response

    def is_available(self) -> bool:
        return True
