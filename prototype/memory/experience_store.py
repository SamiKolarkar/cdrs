"""
Experience Store (Learning Layer).

Stores decision records from the current session and persists them
to a JSON file for cross-session retrieval.

Every stored record contains:
    constraints, action, goal, verdict, confidence, explanation, result

The result field is initially None and is updated after execution
via record_result() on the DecisionEngine.
"""

import json
import os
from typing import List, Dict, Any, Optional
from datetime import datetime, timezone


_DEFAULT_PATH = os.path.join(
    os.path.dirname(__file__), "..", "memory", "experiences.json"
)


class ExperienceStore:
    """
    Persistent JSON-backed store for decision experiences.

    Thread-safety: not guaranteed in v0.1.
    Future: replace with SQLite or vector DB for scale.
    """

    def __init__(self, path: str = None):
        self.path = os.path.abspath(path or _DEFAULT_PATH)
        self._records: List[Dict] = self._load()

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def save(self, record: Dict[str, Any]) -> None:
        """Append a new experience record."""
        record["timestamp"] = datetime.now(timezone.utc).isoformat()
        self._records.append(record)
        self._persist()

    def all(self) -> List[Dict]:
        """Return all stored experience records."""
        return list(self._records)

    def successful(self) -> List[Dict]:
        """Return only records where result == 'success'."""
        return [r for r in self._records if r.get("result") == "success"]

    def failed(self) -> List[Dict]:
        """Return only records where result == 'failure'."""
        return [r for r in self._records if r.get("result") == "failure"]

    def update_latest(self, action: str, result: str) -> bool:
        """
        Update the result field of the most recent record matching action.
        Returns True if found and updated.
        """
        for record in reversed(self._records):
            if record.get("action") == action and record.get("result") is None:
                record["result"] = result
                self._persist()
                return True
        return False

    def count(self) -> int:
        return len(self._records)

    def clear(self) -> None:
        """Remove all records. Use with caution."""
        self._records = []
        self._persist()

    def summary(self) -> str:
        total = self.count()
        success = len(self.successful())
        failed = len(self.failed())
        pending = total - success - failed
        return (
            f"ExperienceStore: {total} records | "
            f"{success} success | {failed} failure | {pending} pending"
        )

    # ------------------------------------------------------------------
    # Private
    # ------------------------------------------------------------------

    def _load(self) -> List[Dict]:
        if os.path.exists(self.path):
            try:
                with open(self.path, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    return data if isinstance(data, list) else []
            except (json.JSONDecodeError, IOError):
                return []
        return []

    def _persist(self) -> None:
        os.makedirs(os.path.dirname(self.path), exist_ok=True)
        with open(self.path, "w", encoding="utf-8") as f:
            json.dump(self._records, f, indent=2, ensure_ascii=False)
