
from typing import Dict


class ArbitrationEngine:
    """
    Resolves competing priorities using weighted scoring.
    """

    DEFAULT_WEIGHTS = {
        "safety": 1.0,
        "risk": 0.9,
        "speed": 0.5,
        "efficiency": 0.6,
        "cost": 0.4,
    }

    def score(self, action_score: float, risk_probability: float,
              priorities: Dict[str, float]) -> float:

        weight_bonus = 0.0

        for key, value in priorities.items():
            base = self.DEFAULT_WEIGHTS.get(key, 0.3)
            weight_bonus += base * value

        final_score = (
            action_score
            + weight_bonus
            - (risk_probability * 10)
        )

        return round(final_score, 3)
