"""
Constraint Extractor (Layer 1).

Receives raw input (dict or natural language description) and
extracts a structured list of Constraint objects.

This is the first layer every decision cycle runs.
No reasoning begins before constraints are mapped.
"""

from typing import List, Dict, Any
from prototype.models.constraint import Constraint


# Default priority rules: constraint names that are treated as high priority
_HIGH_PRIORITY_NAMES = {
    "safety", "visibility", "emergency", "risk_level",
    "time_critical", "user_priority",
}

_MEDIUM_PRIORITY_NAMES = {
    "traffic", "weather", "load", "memory", "capacity",
}


class ConstraintExtractor:
    """
    Converts raw input into a structured constraint map.

    For v0.1 (prototype), accepts a plain dict.
    Future versions: accept natural language and extract via LLM.
    """

    def extract(self, raw: Dict[str, Any]) -> List[Constraint]:
        """
        Extract constraints from a dict of {name: value} pairs.
        Priority is inferred from known constraint names.

        Args:
            raw: Dict of constraint name → value

        Returns:
            List of Constraint objects with inferred priorities.
        """
        constraints = []
        for name, value in raw.items():
            priority = self._infer_priority(name, value)
            category = self._infer_category(name)
            constraints.append(
                Constraint(
                    name=name,
                    value=value,
                    priority=priority,
                    category=category,
                )
            )
        return constraints

    def extract_from_list(self, items: List[Constraint]) -> List[Constraint]:
        """Pass-through for already-structured constraint lists."""
        return items

    def summarize(self, constraints: List[Constraint]) -> str:
        lines = ["Constraints:"]
        for c in constraints:
            marker = "!" if c.is_high_priority() else " "
            lines.append(f"  [{marker}] {c.name} = {c.value} ({c.priority})")
        return "\n".join(lines)

    # ------------------------------------------------------------------

    def _infer_priority(self, name: str, value: Any) -> str:
        name_lower = name.lower()
        # High-priority names always win
        if name_lower in _HIGH_PRIORITY_NAMES:
            return "high"
        # Value keywords override medium-name defaults
        if isinstance(value, str):
            if value.lower() in {"critical", "emergency", "dangerous"}:
                return "high"
            if value.lower() in {"low", "good", "clear", "safe"}:
                return "low"
        if name_lower in _MEDIUM_PRIORITY_NAMES:
            return "medium"
        return "medium"

    def _infer_category(self, name: str) -> str:
        name_lower = name.lower()
        if name_lower in {"traffic", "road", "weather", "visibility", "environment"}:
            return "environment"
        if name_lower in {"memory", "cpu", "bandwidth", "capacity", "load"}:
            return "resource"
        if name_lower in {"safety", "risk_level", "emergency"}:
            return "safety"
        return "environment"
