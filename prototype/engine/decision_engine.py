"""
Decision Engine (Layer 7) — Full Pipeline.

Orchestrates all CDRS layers with two key changes from v0.1:

1. WH-chain confidence_modifier is applied to final confidence.
   The chain now *influences* the decision, not just describes it.

2. WHYConstructor calls Phi-2 via Ollama for natural language WHY.
   Falls back to templates automatically if Ollama is unavailable.
"""

from typing import List, Optional

from prototype.models.constraint import Constraint
from prototype.models.action import Action
from prototype.models.decision import Decision
from prototype.engine.wh_chain import WHChain
from prototype.engine.why_constructor import WHYConstructor
from prototype.engine.evaluator import Evaluator
from prototype.engine.constraint_matcher import ConstraintMatcher
from prototype.engine.ollama_client import OllamaClient
from prototype.memory.experience_store import ExperienceStore
from prototype.engine.arbitration import ArbitrationEngine
from prototype.models.why_model import WhyModel



class DecisionEngine:
    """
    Full CDRS decision pipeline.

    Usage (manual constraints):
        engine = DecisionEngine()
        result = engine.decide(constraints, actions, goal="reach faster")
        print(result.summary())

    Usage (natural language — requires Ollama):
        result = engine.decide_from_text(
            situation="Heavy traffic, poor visibility on a city road.",
            actions=[Action(...), ...]
        )
    """

    def __init__(self, experience_store: Optional[ExperienceStore] = None):
        self.client    = OllamaClient()
        self.wh_chain  = WHChain()
        self.why       = WHYConstructor(client=self.client)
        self.evaluator = Evaluator()
        self.matcher   = ConstraintMatcher()
        self.arbitrator = ArbitrationEngine()
        self.store     = experience_store or ExperienceStore()

    # ------------------------------------------------------------------
    # Primary entry point — structured constraints
    # ------------------------------------------------------------------

    def decide(
        self,
        constraints: List[Constraint],
        actions: List[Action],
        goal: str = "",
        domain: str = "general",
        verbose: bool = False,
    ) -> Decision:
        """
        Run a full CDRS decision cycle.

        Args:
            constraints: Structured constraint list
            actions:     Candidate actions to evaluate
            goal:        Intent driving this decision
            domain:      Context label (driving, scheduling, etc.)
            verbose:     Print reasoning trace to stdout

        Returns:
            Decision with verdict, confidence, LLM-composed explanation.
        """

        # Layer 1 — summarise constraints
        if verbose:
            self._print_constraints(constraints)

        # Layer 2 — WH-chain (now produces confidence_modifier)
        chain = self.wh_chain.run(goal, constraints, domain)
        if verbose:
            print(self.wh_chain.format(chain))
            print()

        # Layer 3 — retrieve similar past patterns
        constraint_dicts = [c.to_dict() for c in constraints]
        similar = self.matcher.find_similar(constraint_dicts, self.store.all())
        if verbose and similar:
            print(self.matcher.summarize_matches(similar))
            print()

        # Layers 4-5 — score all actions
        scored = self.evaluator.score_all(actions, constraints)
        best_score, best_action = scored[0]

        # Layer 6 — WHY construction (LLM or template)
        why = self.why.construct(best_action, constraints, goal, chain)
        if verbose:
            print("Multi-WHY Analysis:")
            print(self.why.format(why))
            print()

        # Layer 7 — verdict + confidence adjusted by WH-chain modifier
        verdict, raw_confidence = self.evaluator.verdict(
            best_score, best_action.risk_probability
        )
        final_confidence = self.evaluator.apply_chain_modifier(
            raw_confidence, chain.get("confidence_modifier", 0.0)
        )
        conditions = self.evaluator.conditions_for(best_action, constraints)

        decision = Decision(
            action=best_action.name,
            verdict=verdict,
            confidence=final_confidence,
            explanation=why["summary"],
            conditions=conditions,
            wh_chain=chain,
            score=best_score,
        )

        if verbose:
            print("=" * 60)
            print(decision.summary())

        # Store experience
        self.store.save({
            "constraints": constraint_dicts,
            "action":      best_action.name,
            "goal":        goal,
            "verdict":     verdict,
            "confidence":  final_confidence,
            "explanation": why["summary"],
            "result":      None,
        })

        return decision

    # ------------------------------------------------------------------
    # Natural language entry point — Ollama extracts constraints
    # ------------------------------------------------------------------

    def decide_from_text(
        self,
        situation: str,
        actions: List[Action],
        goal: str = "",
        domain: str = "general",
        verbose: bool = True,
    ) -> Decision:
        """
        Extract constraints from a plain-text situation description,
        then run the full decision cycle.

        Requires Ollama. Falls back to empty constraints if unavailable.
        """
        if verbose:
            print("=" * 60)
            print("CDRS — Natural Language Decision")
            print("=" * 60)
            print(f"Situation: {situation}")
            print()

        constraints = self._extract_constraints_from_text(situation, verbose)

        return self.decide(
            constraints=constraints,
            actions=actions,
            goal=goal or situation[:80],
            domain=domain,
            verbose=verbose,
        )

    def record_result(self, action: str, result: str) -> None:
        """Update the most recent experience record with the actual outcome."""
        self.store.update_latest(action, result)

    # ------------------------------------------------------------------
    # Private
    # ------------------------------------------------------------------

    def _extract_constraints_from_text(
        self,
        situation: str,
        verbose: bool,
    ) -> List[Constraint]:
        """Use Phi-2 to extract constraints from natural language."""
        from prototype.engine.constraint_extractor import ConstraintExtractor

        extractor = ConstraintExtractor()

        if not self.client.is_available():
            if verbose:
                print("[Ollama unavailable — no constraints extracted from text]")
                print()
            return []

        if verbose:
            print("Extracting constraints from situation (Phi-2)...")

        prompt = f"""Extract the key environmental constraints from this situation.
Return only a JSON object. Keys must be short (1-2 words). Values must be short (1 word).

Situation: {situation}

Example output: {{"traffic": "heavy", "visibility": "poor", "road": "urban"}}

JSON:"""

        data = self.client.extract_json(prompt, max_tokens=80)

        if data:
            constraints = extractor.extract(data)
            if verbose:
                print(extractor.summarize(constraints))
                print()
            return constraints

        if verbose:
            print("[Could not extract constraints — proceeding without them]")
            print()
        return []

    def _print_constraints(self, constraints: List[Constraint]) -> None:
        from prototype.engine.constraint_extractor import ConstraintExtractor
        print(ConstraintExtractor().summarize(constraints))
        print()


# ------------------------------------------------------------------
# Structured WHY generation
# ------------------------------------------------------------------

def build_why_model(self, goal, constraints, action, confidence):
    priorities = {}

    for c in constraints:
        if c.priority == "high":
            priorities[c.name] = 1.0
        elif c.priority == "medium":
            priorities[c.name] = 0.6
        else:
            priorities[c.name] = 0.3

    return WhyModel(
        objective=goal or "optimize decision outcome",
        constraints=[c.to_dict() for c in constraints],
        priorities=priorities,
        risks=action.failure_conditions,
        confidence=confidence,
        reasoning_summary=f"Selected action '{action.name}' "
                          f"under active constraints."
    )
