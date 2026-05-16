
from collections import defaultdict
from typing import List, Dict


class MemoryConsolidator:
    """
    Converts experiences into reusable patterns.
    """

    def consolidate(self, experiences: List[Dict]) -> List[Dict]:
        grouped = defaultdict(list)

        for exp in experiences:
            key = (
                exp.get("goal"),
                exp.get("action"),
                exp.get("verdict")
            )

            grouped[key].append(exp)

        patterns = []

        for key, items in grouped.items():
            avg_conf = (
                sum(i.get("confidence", 0.0) for i in items)
                / len(items)
            )

            common_constraints = {}

            for item in items:
                for c_key, c_val in item.get("constraints", {}).items():
                    common_constraints[c_key] = c_val

            patterns.append({
                "goal": key[0],
                "action": key[1],
                "verdict": key[2],
                "sample_count": len(items),
                "avg_confidence": round(avg_conf, 2),
                "constraints": common_constraints
            })

        return patterns
