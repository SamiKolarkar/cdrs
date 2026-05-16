"""
Pattern Store (Cross-Session Consolidation Layer).

This is the CDRS "dreaming" layer.

Just as the brain consolidates episodic memory into semantic patterns
during sleep, the PatternStore reviews all stored experiences and
extracts recurring patterns:

    - Constraint configurations that reliably lead to success
    - Constraint configurations that reliably lead to failure
    - Actions that consistently outperform alternatives
    - Risk thresholds that predict outcome quality

This layer runs as a scheduled or on-demand process — not in-line
with every decision.

Original concept: Sami Ahmed Yusuf Kolarkar, 2026.
"""

import json
import os
from typing import List, Dict, Any
from collections import defaultdict
from datetime import datetime, timezone

from prototype.memory.experience_store import ExperienceStore


_DEFAULT_PATH = os.path.join(
    os.path.dirname(__file__), "patterns.json"
)


class PatternStore:
    """
    Consolidates experience records into reusable decision patterns.

    A pattern is:
    {
        "constraint_signature": {"traffic": "medium", "visibility": "good"},
        "recommended_action": "overtake",
        "success_rate": 0.83,
        "sample_count": 6,
        "avg_confidence": 0.74,
        "consolidated_at": "ISO timestamp"
    }
    """

    def __init__(self, path: str = None):
        self.path = os.path.abspath(path or _DEFAULT_PATH)
        self._patterns: List[Dict] = self._load()

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def consolidate(self, store: ExperienceStore) -> int:
        """
        Run consolidation over all experience records.
        Extracts patterns and saves them.

        Returns the number of patterns generated.
        """
        records = store.all()
        completed = [r for r in records if r.get("result") is not None]

        if len(completed) < 2:
            return 0  # Not enough data to consolidate

        # Group by (action, constraint signature)
        groups: Dict[str, List[Dict]] = defaultdict(list)
        for rec in completed:
            sig = self._signature(rec.get("constraints", []))
            key = f"{rec['action']}::{sig}"
            groups[key].append(rec)

        new_patterns = []
        for key, group in groups.items():
            if len(group) < 2:
                continue
            action = group[0]["action"]
            sig_dict = self._signature_dict(group[0].get("constraints", []))
            successes = sum(1 for r in group if r.get("result") == "success")
            success_rate = successes / len(group)
            avg_conf = sum(r.get("confidence", 0.5) for r in group) / len(group)

            new_patterns.append({
                "constraint_signature": sig_dict,
                "recommended_action": action,
                "success_rate": round(success_rate, 3),
                "sample_count": len(group),
                "avg_confidence": round(avg_conf, 3),
                "consolidated_at": datetime.now(timezone.utc).isoformat(),
            })

        self._patterns = new_patterns
        self._persist()
        return len(new_patterns)

    def lookup(self, constraints: List[Dict], threshold: float = 0.5) -> List[Dict]:
        """
        Find patterns whose constraint signature matches current constraints.

        Returns patterns with success_rate above threshold, sorted desc.
        """
        current_pairs = {(c["name"], str(c["value"])) for c in constraints}
        results = []

        for pattern in self._patterns:
            sig = pattern.get("constraint_signature", {})
            sig_pairs = {(k, str(v)) for k, v in sig.items()}
            if not sig_pairs:
                continue
            overlap = len(current_pairs & sig_pairs) / len(current_pairs | sig_pairs)
            if overlap >= 0.4 and pattern["success_rate"] >= threshold:
                results.append((overlap, pattern))

        results.sort(key=lambda x: x[0], reverse=True)
        return [p for _, p in results]

    def all(self) -> List[Dict]:
        return list(self._patterns)

    def count(self) -> int:
        return len(self._patterns)

    def summary(self) -> str:
        if not self._patterns:
            return "PatternStore: no patterns consolidated yet."
        lines = [f"PatternStore: {self.count()} pattern(s)"]
        for p in self._patterns[:5]:
            lines.append(
                f"  Action: {p['recommended_action']} | "
                f"Success: {p['success_rate']:.0%} | "
                f"n={p['sample_count']}"
            )
        return "\n".join(lines)

    # ------------------------------------------------------------------

    def _signature(self, constraints: List[Dict]) -> str:
        pairs = sorted(
            (c["name"], str(c["value"])) for c in constraints
        )
        return "|".join(f"{k}={v}" for k, v in pairs)

    def _signature_dict(self, constraints: List[Dict]) -> Dict:
        return {c["name"]: c["value"] for c in constraints}

    def _load(self) -> List[Dict]:
        if os.path.exists(self.path):
            try:
                with open(self.path, "r", encoding="utf-8") as f:
                    return json.load(f)
            except (json.JSONDecodeError, IOError):
                return []
        return []

    def _persist(self) -> None:
        os.makedirs(os.path.dirname(self.path), exist_ok=True)
        with open(self.path, "w", encoding="utf-8") as f:
            json.dump(self._patterns, f, indent=2, ensure_ascii=False)
