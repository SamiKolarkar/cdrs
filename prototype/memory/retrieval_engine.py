
from typing import List, Dict


class RetrievalEngine:
    """
    Retrieves relevant past experiences using lightweight similarity scoring.
    Optimized for local Phi/Ollama runtimes.
    """

    def retrieve(self, experiences: List[Dict], context: Dict, limit: int = 3):
        scored = []

        for exp in experiences:
            score = 0

            stored_constraints = exp.get("constraints", {})

            for key, value in context.items():
                if stored_constraints.get(key) == value:
                    score += 1

            scored.append((score, exp))

        scored.sort(key=lambda x: x[0], reverse=True)

        return [x[1] for x in scored[:limit]]
