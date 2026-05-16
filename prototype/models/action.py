"""
Action model.
Represents a candidate action the decision engine can evaluate.
"""

from dataclasses import dataclass, field
from typing import List


@dataclass
class Action:
    """
    A candidate action with predicted outcome score and risk.

    Attributes:
        name:              Action identifier
        outcome_score:     Expected benefit (0-10 scale)
        risk_probability:  Probability of failure or harm (0.0-1.0)
        failure_conditions: Conditions under which this action becomes dangerous
        description:       Optional human-readable description
    """
    name: str
    outcome_score: float = 5.0
    risk_probability: float = 0.1
    failure_conditions: List[str] = field(default_factory=list)
    description: str = ""

    def to_dict(self) -> dict:
        return {
            "name": self.name,
            "outcome_score": self.outcome_score,
            "risk_probability": self.risk_probability,
            "failure_conditions": self.failure_conditions,
            "description": self.description,
        }

    def __repr__(self) -> str:
        return (
            f"Action({self.name}, outcome={self.outcome_score}, "
            f"risk={self.risk_probability})"
        )
