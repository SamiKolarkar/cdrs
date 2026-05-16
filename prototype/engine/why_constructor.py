"""
WHY Construction Layer (Layer 6) — LLM-Powered.

WHY is dynamically composed by Phi-2 via Ollama from:
    outcomes · constraints · risks · goals · failure conditions

If Ollama is unavailable, falls back to structured templates.
The fallback ensures the system always produces output.

Original concept: Sami Ahmed Yusuf Kolarkar, 2026.
"""

from typing import List
from prototype.models.constraint import Constraint
from prototype.models.action import Action
from prototype.engine.ollama_client import OllamaClient


class WHYConstructor:
    """
    Dynamically constructs WHY explanation using Phi-2 via Ollama.

    Produces four components:
        benefit_why   — why this action produces value
        risk_why      — why this action could fail
        condition_why — when this action is valid
        failure_why   — when this action becomes dangerous
        summary       — LLM-composed natural language explanation
    """

    def __init__(self, client: OllamaClient = None):
        self.client = client or OllamaClient()
        self._llm_available = None  # cached after first check

    def construct(
        self,
        action: Action,
        constraints: List[Constraint],
        goal: str = "",
        wh_chain: dict = None,
    ) -> dict:
        """
        Build multi-dimensional WHY for the given action.
        Uses LLM if available, templates otherwise.
        """
        constraint_map  = {c.name: c.value for c in constraints}
        high_priority   = [c for c in constraints if c.is_high_priority()]

        benefit   = self._benefit_why(action, goal, constraint_map)
        risk      = self._risk_why(action, constraint_map)
        condition = self._condition_why(action, high_priority)
        failure   = self._failure_why(action)

        # Try LLM summary — fall back to template if unavailable
        summary = self._llm_summary(
            action, constraint_map, goal, wh_chain
        ) or self._template_summary(action, benefit, risk, condition, failure)

        return {
            "benefit_why":   benefit,
            "risk_why":      risk,
            "condition_why": condition,
            "failure_why":   failure,
            "summary":       summary,
            "llm_used":      self._llm_available,
        }

    def format(self, why: dict) -> str:
        mode = "LLM (Phi-2)" if why.get("llm_used") else "template fallback"
        return "\n".join([
            f"  [WHY mode: {mode}]",
            f"  Benefit:    {why['benefit_why']}",
            f"  Risk:       {why['risk_why']}",
            f"  Valid when: {why['condition_why']}",
            f"  Fails when: {why['failure_why']}",
            f"  Summary:    {why['summary']}",
        ])

    # ------------------------------------------------------------------
    # LLM path
    # ------------------------------------------------------------------

    def _llm_summary(
        self,
        action: Action,
        constraint_map: dict,
        goal: str,
        wh_chain: dict,
    ) -> str | None:
        """Call Phi-2 for a natural language WHY summary."""
        if self._llm_available is False:
            return None
        if self._llm_available is None:
            self._llm_available = self.client.is_available()
            if not self._llm_available:
                return None

        constraints_text = ", ".join(
            f"{k}={v}" for k, v in constraint_map.items()
        )
        failures_text = (
            "; ".join(action.failure_conditions)
            if action.failure_conditions else "none specified"
        )
        when_text = wh_chain.get("when", "") if wh_chain else ""

        prompt = f"""You are a decision reasoning assistant. Write a clear 2-sentence explanation.

Action taken: {action.name.replace("_", " ")}
Goal: {goal or "achieve optimal outcome"}
Constraints: {constraints_text}
Risk probability: {action.risk_probability:.0%}
Dangerous when: {failures_text}
Valid conditions: {when_text}

Write exactly 2 sentences:
Sentence 1: Why this action is beneficial under the current constraints.
Sentence 2: Why this action carries risk and when it becomes unsafe.

Explanation:"""

        response = self.client.generate(prompt, max_tokens=120)
        if not response:
            self._llm_available = False
            return None

        # Clean up — take first two sentences from response
        return self._extract_two_sentences(response)

    def _extract_two_sentences(self, text: str) -> str:
        """Extract and return the first two clean sentences."""
        # Remove prompt echoing if model repeats it
        for marker in ["Explanation:", "Sentence 1:", "Answer:"]:
            if marker in text:
                text = text.split(marker)[-1].strip()

        # Split on sentence boundaries
        import re
        sentences = re.split(r"(?<=[.!?])\s+", text.strip())
        sentences = [s.strip() for s in sentences if len(s.strip()) > 10]

        if len(sentences) >= 2:
            return " ".join(sentences[:2])
        return text[:300].strip()

    # ------------------------------------------------------------------
    # Template fallback (always works)
    # ------------------------------------------------------------------

    def _benefit_why(self, action: Action, goal: str, constraint_map: dict) -> str:
        desc     = action.description or f"executing '{action.name}'"
        goal_str = f" toward '{goal}'" if goal else ""
        env      = constraint_map.get("road") or constraint_map.get("environment", "")
        env_str  = f" on {env}" if env else ""
        return f"{desc.capitalize()} advances progress{goal_str}{env_str}."

    def _risk_why(self, action: Action, constraint_map: dict) -> str:
        p       = action.risk_probability
        parts   = []
        if p > 0.5:
            parts.append(f"high failure probability ({p:.0%})")
        elif p > 0.2:
            parts.append(f"moderate failure probability ({p:.0%})")
        else:
            parts.append(f"low failure probability ({p:.0%})")
        if constraint_map.get("traffic") in {"high", "heavy"}:
            parts.append("high traffic elevates collision risk")
        if constraint_map.get("visibility") in {"low", "poor"}:
            parts.append("poor visibility limits reaction time")
        return "; ".join(parts) + "."

    def _condition_why(self, action: Action, high_priority: List[Constraint]) -> str:
        if not high_priority:
            return "Valid under current conditions."
        conds = " and ".join(f"{c.name} is {c.value}" for c in high_priority)
        return f"Valid when {conds}."

    def _failure_why(self, action: Action) -> str:
        if action.failure_conditions:
            return "Dangerous when: " + "; ".join(action.failure_conditions) + "."
        return "Risk remains manageable under stated constraints."

    def _template_summary(
        self, action, benefit, risk, condition, failure
    ) -> str:
        return (
            f"'{action.name.replace('_', ' ').capitalize()}' selected. "
            f"{benefit} {risk} {condition}"
        )
