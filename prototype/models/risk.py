"""
Risk model.
Represents a failure condition and its estimated probability.
"""

from dataclasses import dataclass, field
from typing import List


@dataclass
class Risk:
    """
    A risk associated with an action.

    Attributes:
        action_name:   Which action this risk belongs to
        description:   What could go wrong
        probability:   Estimated failure probability (0.0-1.0)
        severity:      Impact if failure occurs: low / medium / high / critical
        triggers:      Constraint conditions that elevate this risk
    """
    action_name: str
    description: str
    probability: float
    severity: str = "medium"
    triggers: List[str] = field(default_factory=list)

    def is_critical(self) -> bool:
        return self.severity == "critical" or self.probability > 0.7

    def weighted_score(self, severity_weights: dict = None) -> float:
        """Returns probability scaled by severity weight."""
        weights = severity_weights or {
            "low": 1.0, "medium": 2.0, "high": 4.0, "critical": 8.0
        }
        return self.probability * weights.get(self.severity, 2.0)

    def to_dict(self) -> dict:
        return {
            "action_name": self.action_name,
            "description": self.description,
            "probability": self.probability,
            "severity": self.severity,
            "triggers": self.triggers,
        }

    def __repr__(self) -> str:
        return (
            f"Risk({self.action_name}: {self.description}, "
            f"p={self.probability}, severity={self.severity})"
        )
