
from dataclasses import dataclass, field
from typing import List, Dict


@dataclass
class WhyModel:
    """
    Structured WHY representation.

    Converts free-form reasoning into machine-usable signals.
    """

    objective: str
    constraints: List[Dict] = field(default_factory=list)
    priorities: Dict[str, float] = field(default_factory=dict)
    risks: List[str] = field(default_factory=list)
    confidence: float = 0.0
    reasoning_summary: str = ""

    def to_dict(self) -> dict:
        return {
            "objective": self.objective,
            "constraints": self.constraints,
            "priorities": self.priorities,
            "risks": self.risks,
            "confidence": self.confidence,
            "reasoning_summary": self.reasoning_summary,
        }
