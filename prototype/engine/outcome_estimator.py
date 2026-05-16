"""
Outcome Estimator (replaces manual outcome_score inputs).

Derives outcome_score and risk_probability from constraint configurations
and action types using a rule-based scoring system.

This removes the need for callers to manually pass scores.
The engine now reasons from the situation itself.

v0.2: Rule-based. v1.0 target: learned from experience records.
"""

from typing import List, Tuple
from prototype.models.constraint import Constraint


# ------------------------------------------------------------------
# Risk-increasing constraint patterns
# (constraint_name, constraint_value) → risk multiplier
# ------------------------------------------------------------------
_RISK_ELEVATORS = {
    ("visibility", "poor"):    0.40,
    ("visibility", "low"):     0.35,
    ("traffic", "high"):       0.30,
    ("traffic", "heavy"):      0.35,
    ("weather", "rain"):       0.20,
    ("weather", "fog"):        0.35,
    ("weather", "storm"):      0.45,
    ("road", "urban"):         0.15,
    ("memory", "critical"):    0.40,
    ("memory", "high"):        0.25,
    ("cpu_load", "high"):      0.20,
    ("safety", "critical"):    0.50,
    ("safety", "dangerous"):   0.60,
    ("time_critical", "yes"):  0.10,
}

# Risk-reducing constraint patterns
_RISK_REDUCERS = {
    ("visibility", "good"):    0.15,
    ("visibility", "clear"):   0.20,
    ("traffic", "low"):        0.15,
    ("traffic", "clear"):      0.20,
    ("weather", "clear"):      0.10,
    ("road", "highway"):       0.05,
    ("safety", "normal"):      0.05,
    ("memory", "low"):         0.10,
}

# Base outcome scores by action keyword
_ACTION_BASE_SCORES = {
    "overtake":          7.5,
    "pass":              7.0,
    "accelerate":        7.0,
    "process":           8.0,
    "execute":           8.0,
    "proceed":           7.5,
    "stay":              5.0,
    "wait":              4.5,
    "follow":            5.0,
    "slow":              3.5,
    "defer":             6.5,
    "queue":             6.0,
    "batch":             6.0,
    "stop":              3.0,
    "default":           5.0,
}

# Base risk probabilities by action keyword
_ACTION_BASE_RISKS = {
    "overtake":          0.30,
    "pass":              0.25,
    "accelerate":        0.25,
    "process":           0.20,
    "execute":           0.20,
    "proceed":           0.20,
    "stay":              0.05,
    "wait":              0.04,
    "follow":            0.06,
    "slow":              0.03,
    "defer":             0.08,
    "queue":             0.07,
    "batch":             0.07,
    "stop":              0.02,
    "default":           0.15,
}


class OutcomeEstimator:
    """
    Derives outcome_score and risk_probability from the action name
    and current constraint configuration.

    Replaces manual score inputs — callers only need to name their actions.
    """

    def estimate(
        self,
        action_name: str,
        constraints: List[Constraint],
    ) -> Tuple[float, float]:
        """
        Estimate (outcome_score, risk_probability) for an action.

        Args:
            action_name:  Name of the action (e.g. "overtake", "defer_low_priority")
            constraints:  Current constraint list

        Returns:
            (outcome_score in 0-10, risk_probability in 0.0-1.0)
        """
        base_score = self._base_score(action_name)
        base_risk = self._base_risk(action_name)

        score_adj, risk_adj = self._constraint_adjustments(constraints)

        outcome_score = max(0.0, min(10.0, base_score + score_adj))
        risk_probability = max(0.01, min(0.99, base_risk + risk_adj))

        return round(outcome_score, 2), round(risk_probability, 3)

    def _base_score(self, action_name: str) -> float:
        name = action_name.lower()
        for keyword, score in _ACTION_BASE_SCORES.items():
            if keyword in name:
                return score
        return _ACTION_BASE_SCORES["default"]

    def _base_risk(self, action_name: str) -> float:
        name = action_name.lower()
        for keyword, risk in _ACTION_BASE_RISKS.items():
            if keyword in name:
                return risk
        return _ACTION_BASE_RISKS["default"]

    def _constraint_adjustments(
        self,
        constraints: List[Constraint],
    ) -> Tuple[float, float]:
        score_adj = 0.0
        risk_adj = 0.0

        for c in constraints:
            key = (c.name.lower(), str(c.value).lower())

            if key in _RISK_ELEVATORS:
                penalty = _RISK_ELEVATORS[key]
                # High-priority constraints amplify the penalty
                if c.is_high_priority():
                    penalty *= 1.5
                risk_adj += penalty
                score_adj -= penalty * 2  # Risk increase hurts benefit

            if key in _RISK_REDUCERS:
                reduction = _RISK_REDUCERS[key]
                risk_adj -= reduction
                score_adj += reduction  # Safe environment improves benefit

        return score_adj, risk_adj
