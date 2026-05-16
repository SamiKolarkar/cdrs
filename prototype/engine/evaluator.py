"""
Evaluator (Layers 4-5).

Scores actions and produces verdict + confidence.

NEW in this version:
    apply_chain_modifier() — takes the confidence_modifier from the
    WH-chain and applies it to the raw confidence score.

    This connects Layer 2 (WH-chain) to Layer 7 (decision output)
    so the chain actually influences the decision, not just describes it.

Score formula:
    score = outcome_score - (risk_probability × safety_weight)

Confidence formula:
    raw_confidence = f(score, risk)
    final_confidence = clamp(raw_confidence + chain_modifier, 0.05, 0.95)
"""

from typing import List, Dict
from prototype.models.action import Action
from prototype.models.constraint import Constraint

_PRIORITY_WEIGHTS: Dict[str, float] = {
    "high":   10.0,
    "medium":  5.0,
    "low":     2.0,
}


class Evaluator:

    def score(self, action: Action, constraints: List[Constraint]) -> float:
        """Raw score = benefit - weighted risk."""
        weight = self._safety_weight(constraints)
        return action.outcome_score - (action.risk_probability * weight)

    def score_all(
        self,
        actions: List[Action],
        constraints: List[Constraint],
    ) -> List[tuple]:
        """Returns [(score, action), ...] sorted descending."""
        scored = [(self.score(a, constraints), a) for a in actions]
        return sorted(scored, key=lambda x: x[0], reverse=True)

    def verdict(self, score: float, risk: float) -> tuple:
        """
        Returns (verdict, raw_confidence).
        Raw confidence is adjusted downstream by apply_chain_modifier().
        """
        if score >= 6 and risk <= 0.2:
            return "yes",            min(0.95, 0.70 + score / 20)
        if score >= 3 and risk <= 0.5:
            return "conditional_yes", min(0.85, 0.50 + score / 20)
        if score >= 0 and risk <= 0.7:
            return "conditional_no",  max(0.30, 0.50 - risk / 2)
        return "no",                  max(0.05, 0.40 - abs(score) / 20)

    def apply_chain_modifier(
        self,
        raw_confidence: float,
        chain_modifier: float,
    ) -> float:
        """
        Apply WH-chain confidence modifier to raw confidence.

        chain_modifier is in [-0.30, 0.0] — it only reduces confidence,
        never inflates it. Dangerous constraint conditions lower certainty.
        Final value clamped to [0.05, 0.95].
        """
        adjusted = raw_confidence + chain_modifier
        return max(0.05, min(0.95, adjusted))

    def conditions_for(
        self,
        action: Action,
        constraints: List[Constraint],
    ) -> List[str]:
        """List what must remain true for this decision to stay valid."""
        conds = [
            f"{c.name} remains {c.value}"
            for c in constraints if c.is_high_priority()
        ]
        if action.risk_probability > 0.3:
            conds.append("risk conditions do not deteriorate")
        return conds

    # ------------------------------------------------------------------

    def _safety_weight(self, constraints: List[Constraint]) -> float:
        if any(c.is_high_priority() for c in constraints):
            return _PRIORITY_WEIGHTS["high"]
        if any(c.priority == "medium" for c in constraints):
            return _PRIORITY_WEIGHTS["medium"]
        return _PRIORITY_WEIGHTS["low"]
