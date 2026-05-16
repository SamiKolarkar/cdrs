"""
Ollama Client

Lightweight HTTP client for local Ollama inference.
Uses Python standard library only — no external dependencies.

Model:   phi:latest (Phi-2, 2.7B)
Endpoint: http://localhost:11434
"""

import urllib.request
import urllib.error
import json
import re

DEFAULT_MODEL   = "phi:latest"
DEFAULT_BASE_URL = "http://localhost:11434"
DEFAULT_TIMEOUT  = 90  # seconds — i3 CPU needs time


class OllamaClient:
    """
    Wraps Ollama's /api/generate endpoint.

    All public methods return None on failure.
    Callers must handle None by falling back to templates.
    """

    def __init__(
        self,
        model: str = DEFAULT_MODEL,
        base_url: str = DEFAULT_BASE_URL,
        timeout: int = DEFAULT_TIMEOUT,
    ):
        self.model    = model
        self.base_url = base_url.rstrip("/")
        self.timeout  = timeout

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def generate(self, prompt: str, max_tokens: int = 200) -> str | None:
        """
        Send a prompt to Ollama. Returns response text or None.
        Temperature 0.3 — structured, consistent output.
        """
        url     = f"{self.base_url}/api/generate"
        payload = json.dumps({
            "model":   self.model,
            "prompt":  prompt,
            "stream":  False,
            "options": {
                "num_predict": max_tokens,
                "temperature":  0.3,
                "top_p":        0.9,
            },
        }).encode("utf-8")

        req = urllib.request.Request(
            url, data=payload,
            headers={"Content-Type": "application/json"},
            method="POST",
        )

        try:
            with urllib.request.urlopen(req, timeout=self.timeout) as resp:
                result = json.loads(resp.read().decode("utf-8"))
                return result.get("response", "").strip()
        except Exception:
            return None

    def extract_json(self, prompt: str, max_tokens: int = 150) -> dict | None:
        """Ask Phi for JSON. Parses and returns dict or None."""
        raw = self.generate(prompt, max_tokens=max_tokens)
        return self._parse_json(raw) if raw else None

    def is_available(self) -> bool:
        """Return True if Ollama is running and model is loaded."""
        try:
            with urllib.request.urlopen(
                f"{self.base_url}/api/tags", timeout=5
            ) as resp:
                data   = json.loads(resp.read().decode("utf-8"))
                models = [m.get("name", "") for m in data.get("models", [])]
                return any(self.model.split(":")[0] in m for m in models)
        except Exception:
            return False

    # ------------------------------------------------------------------
    # Private
    # ------------------------------------------------------------------

    def _parse_json(self, text: str) -> dict | None:
        text = re.sub(r"```(?:json)?", "", text).strip()
        try:
            return json.loads(text)
        except json.JSONDecodeError:
            pass
        match = re.search(r"\{[^{}]+\}", text, re.DOTALL)
        if match:
            try:
                return json.loads(match.group())
            except json.JSONDecodeError:
                pass
        return None
