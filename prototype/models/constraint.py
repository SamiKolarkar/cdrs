"""
Constraint model.
Represents a single environmental condition, limit, or priority
that bounds the decision space.
"""

from dataclasses import dataclass
from typing import Literal

Priority = Literal["high", "medium", "low"]


@dataclass
class Constraint:
    """
    A single constraint on the decision environment.

    Attributes:
        name:     Constraint identifier (e.g. "traffic", "visibility")
        value:    Current value (e.g. "high", "good", 0.8)
        priority: How much this constraint influences decisions
        category: Optional grouping (environment, resource, safety, user)
    """
    name: str
    value: object
    priority: Priority = "medium"
    category: str = "environment"

    def is_high_priority(self) -> bool:
        return self.priority == "high"

    def to_dict(self) -> dict:
        return {
            "name": self.name,
            "value": self.value,
            "priority": self.priority,
            "category": self.category,
        }

    def __repr__(self) -> str:
        return f"Constraint({self.name}={self.value}, priority={self.priority})"
