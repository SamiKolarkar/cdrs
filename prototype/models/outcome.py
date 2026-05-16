"""
Outcome model.
Represents the predicted result of an action under given constraints.
"""

from dataclasses import dataclass


@dataclass
class Outcome:
    """
    Predicted result of executing an action.

    Attributes:
        action_name:  Which action this outcome belongs to
        description:  Human-readable prediction
        score:        Numeric benefit score (0-10)
        condition:    Constraint condition under which this outcome holds
    """
    action_name: str
    description: str
    score: float
    condition: str = "general"

    def to_dict(self) -> dict:
        return {
            "action_name": self.action_name,
            "description": self.description,
            "score": self.score,
            "condition": self.condition,
        }

    def __repr__(self) -> str:
        return f"Outcome({self.action_name}: {self.description} [score={self.score}])"
