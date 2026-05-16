
class ConfidenceEngine:
    """
    Converts constraints + risk into stable runtime confidence scores.
    """

    def calculate(self, base_confidence, risk_probability, constraint_count):
        penalty = risk_probability * 0.4
        complexity_penalty = min(constraint_count * 0.03, 0.15)

        final = base_confidence - penalty - complexity_penalty

        return round(max(0.05, min(final, 0.99)), 2)
