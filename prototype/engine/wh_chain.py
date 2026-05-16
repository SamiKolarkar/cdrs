"""
WH-Chain Layer (Layer 2).

The primary CDRS differentiator.

Chain order: WHY → WHAT → WHO → WHEN → WHERE → HOW

NEW in this version:
    The chain produces a `confidence_modifier` (float, -0.3 to 0.0)
    that the evaluator applies to the final confidence score.

    If WHEN conditions conflict with current constraints,
    confidence is reduced. This makes the chain output
    actually influence decisions — not just run in parallel.

Original concept: Sami Ahmed Yusuf Kolarkar, 2026.
"""

from typing import List
from prototype.models.constraint import Constraint


# Constraint values that signal dangerous/invalid conditions
_DANGER_VALUES  = {"high", "heavy", "poor", "critical", "dangerous", "wet", "icy"}
_SAFE_VALUES    = {"good", "clear", "low", "normal", "dry", "safe"}


class WHChain:
    """
    Runs the WH-question decomposition and produces a confidence modifier
    based on how well current constraints align with safe operating conditions.
    """

    def run(
        self,
        goal: str,
        constraints: List[Constraint],
        domain: str = "general",
    ) -> dict:
        """
        Execute the WH-chain and return the full chain dict
        including a confidence_modifier field.
        """
        constraint_map  = {c.name: c.value for c in constraints}
        high_priority   = [c for c in constraints if c.is_high_priority()]

        chain = {
            "why":   self._resolve_why(goal, constraints),
            "what":  self._resolve_what(goal, constraint_map),
            "who":   self._resolve_who(domain),
            "when":  self._resolve_when(high_priority),
            "where": self._resolve_where(constraint_map, domain),
            "how":   None,
        }
        chain["how"] = self._resolve_how(chain, constraint_map)

        # Key addition: derive confidence modifier from constraint alignment
        chain["confidence_modifier"] = self._confidence_modifier(
            constraints, high_priority
        )

        return chain

    def format(self, chain: dict) -> str:
        modifier = chain.get("confidence_modifier", 0.0)
        lines = ["WH-Chain Decomposition:"]
        for key in ["why", "what", "who", "when", "where", "how"]:
            lines.append(f"  {key.upper():6s}: {chain.get(key, '-')}")
        sign = "+" if modifier >= 0 else ""
        lines.append(f"  CONF MODIFIER: {sign}{modifier:.2f}")
        return "\n".join(lines)

    # ------------------------------------------------------------------
    # Confidence modifier — the key new mechanism
    # ------------------------------------------------------------------

    def _confidence_modifier(
        self,
        constraints: List[Constraint],
        high_priority: List[Constraint],
    ) -> float:
        """
        Compute how much current constraints should reduce confidence.

        Logic:
        - High-priority constraints with danger values  → large penalty
        - Medium-priority constraints with danger values → small penalty
        - Safe constraint values                         → no penalty

        Returns a value in [-0.30, 0.0]
        """
        modifier = 0.0

        for c in constraints:
            val = str(c.value).lower()
            if val in _DANGER_VALUES:
                if c.priority == "high":
                    modifier -= 0.15
                elif c.priority == "medium":
                    modifier -= 0.05

        # Cap at -0.30 so confidence never goes to zero from chain alone
        return max(-0.30, modifier)

    # ------------------------------------------------------------------
    # WH resolvers
    # ------------------------------------------------------------------

    def _resolve_why(self, goal: str, constraints: List[Constraint]) -> str:
        high = [c.name for c in constraints if c.is_high_priority()]
        if high:
            return (
                f"To achieve '{goal}' while respecting "
                f"high-priority constraints: {', '.join(high)}."
            )
        return f"To achieve '{goal}' under current conditions."

    def _resolve_what(self, goal: str, constraint_map: dict) -> str:
        return f"An action that fulfills '{goal}' within: {constraint_map}."

    def _resolve_who(self, domain: str) -> str:
        return f"The CDRS decision agent operating in domain '{domain}'."

    def _resolve_when(self, high_priority: List[Constraint]) -> str:
        if not high_priority:
            return "Under current conditions without critical constraints."
        conds = " and ".join(
            f"{c.name} is {c.value}" for c in high_priority
        )
        return f"When {conds}."

    def _resolve_where(self, constraint_map: dict, domain: str) -> str:
        env = (
            constraint_map.get("road")
            or constraint_map.get("environment")
            or domain
        )
        return f"In a '{env}' environment."

    def _resolve_how(self, chain: dict, constraint_map: dict) -> str:
        return (
            f"By evaluating actions against the goal ({chain['why']}) "
            f"within the context ({chain['where']}), valid under: {chain['when']}."
        )
