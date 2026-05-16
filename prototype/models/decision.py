"""
Decision model.
The output of the CDRS decision engine.
"""

from dataclasses import dataclass, field
from typing import List, Literal

Verdict = Literal["yes", "no", "conditional_yes", "conditional_no"]


@dataclass
class Decision:
    """
    The full output of one CDRS decision cycle.

    Attributes:
        action:       The selected action name
        verdict:      yes / no / conditional_yes / conditional_no
        confidence:   Estimated reliability of this decision (0.0-1.0)
        explanation:  Dynamically constructed WHY
        conditions:   If conditional, what must hold for the decision to be valid
        wh_chain:     The WH-question decomposition that informed this decision
        score:        Raw numeric decision score
    """
    action: str
    verdict: Verdict
    confidence: float
    explanation: str
    conditions: List[str] = field(default_factory=list)
    wh_chain: dict = field(default_factory=dict)
    score: float = 0.0

    def summary(self) -> str:
        verdict_label = self.verdict.upper().replace("_", " ")
        lines = [
            f"Decision: {verdict_label} | Action: {self.action} | Confidence: {self.confidence:.2f}",
            f"WHY: {self.explanation}",
        ]
        if self.conditions:
            lines.append(f"Conditions: {', '.join(self.conditions)}")
        return "\n".join(lines)

    def to_dict(self) -> dict:
        return {
            "action": self.action,
            "verdict": self.verdict,
            "confidence": self.confidence,
            "explanation": self.explanation,
            "conditions": self.conditions,
            "wh_chain": self.wh_chain,
            "score": self.score,
        }

    def __repr__(self) -> str:
        return f"Decision({self.verdict.upper()}: {self.action}, confidence={self.confidence:.2f})"
