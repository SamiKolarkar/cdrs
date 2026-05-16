"""
Constraint Matcher (part of Learning Layer).

Retrieves past experiences whose constraint configurations
are similar to the current situation.

Retrieval is constraint-based — not text similarity.
This is a key architectural distinction of CDRS.
"""

from typing import List, Dict, Any


class ConstraintMatcher:
    """
    Compares constraint configurations by shared keys and values.

    Similarity metric (v0.1): Jaccard-style overlap on constraint key-value pairs.

    Future versions: weighted similarity that respects priority levels,
    or embedding-based constraint vectors.
    """

    def similarity(
        self,
        current: List[Dict],
        past: List[Dict],
    ) -> float:
        """
        Compute similarity between two constraint configurations.

        Args:
            current: List of constraint dicts from current session
            past:    List of constraint dicts from a past experience

        Returns:
            Similarity score in [0.0, 1.0]
        """
        current_pairs = {(c["name"], str(c["value"])) for c in current}
        past_pairs = {(c["name"], str(c["value"])) for c in past}

        if not current_pairs and not past_pairs:
            return 1.0
        if not current_pairs or not past_pairs:
            return 0.0

        intersection = len(current_pairs & past_pairs)
        union = len(current_pairs | past_pairs)
        return intersection / union

    def find_similar(
        self,
        current_constraints: List[Dict],
        experiences: List[Dict],
        threshold: float = 0.4,
        top_k: int = 3,
    ) -> List[Dict]:
        """
        Find past experiences with constraint similarity above threshold.

        Args:
            current_constraints: Current session constraint dicts
            experiences:         All stored experience records
            threshold:           Minimum similarity to include
            top_k:               Maximum number of results

        Returns:
            List of matching experience records, sorted by similarity desc.
        """
        scored = []
        for exp in experiences:
            past_constraints = exp.get("constraints", [])
            sim = self.similarity(current_constraints, past_constraints)
            if sim >= threshold:
                scored.append((sim, exp))

        scored.sort(key=lambda x: x[0], reverse=True)
        return [exp for _, exp in scored[:top_k]]

    def summarize_matches(self, matches: List[Dict]) -> str:
        if not matches:
            return "No similar past experiences found."
        lines = [f"Found {len(matches)} similar past experience(s):"]
        for i, m in enumerate(matches, 1):
            lines.append(
                f"  {i}. Action: {m.get('action')} | "
                f"Result: {m.get('result')} | "
                f"Confidence: {m.get('confidence', '?')}"
            )
        return "\n".join(lines)
