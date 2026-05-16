"""
Integration test — full CDRS decision cycle end-to-end.

Tests that all layers work together correctly:
constraint extraction → WH-chain → scoring → WHY construction
→ decision output → experience storage → pattern consolidation.
"""

import sys
import os
import tempfile

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

import unittest
from prototype.models.constraint import Constraint
from prototype.models.action import Action
from prototype.models.decision import Decision
from prototype.engine.constraint_extractor import ConstraintExtractor
from prototype.engine.decision_engine import DecisionEngine
from prototype.memory.experience_store import ExperienceStore
from prototype.memory.pattern_store import PatternStore


class TestFullDecisionCycle(unittest.TestCase):

    def setUp(self):
        self.tmp = tempfile.NamedTemporaryFile(suffix=".json", delete=False)
        self.tmp.close()
        self.store = ExperienceStore(path=self.tmp.name)
        self.engine = DecisionEngine(experience_store=self.store)

        self.extractor = ConstraintExtractor()
        self.constraints = self.extractor.extract({
            "traffic": "medium",
            "visibility": "good",
            "road": "highway",
        })
        self.actions = [
            Action("overtake", outcome_score=8, risk_probability=0.35,
                   failure_conditions=["blind turn", "high traffic"]),
            Action("stay_behind", outcome_score=5, risk_probability=0.05),
            Action("slow_down", outcome_score=3, risk_probability=0.02),
        ]

    def tearDown(self):
        os.unlink(self.tmp.name)

    def test_decide_returns_decision_object(self):
        result = self.engine.decide(self.constraints, self.actions, goal="reach faster")
        self.assertIsInstance(result, Decision)

    def test_decision_has_valid_verdict(self):
        result = self.engine.decide(self.constraints, self.actions)
        self.assertIn(result.verdict, ["yes", "no", "conditional_yes", "conditional_no"])

    def test_confidence_in_valid_range(self):
        result = self.engine.decide(self.constraints, self.actions)
        self.assertGreaterEqual(result.confidence, 0.0)
        self.assertLessEqual(result.confidence, 1.0)

    def test_explanation_non_empty(self):
        result = self.engine.decide(self.constraints, self.actions)
        self.assertTrue(len(result.explanation) > 0)

    def test_action_is_one_of_candidates(self):
        result = self.engine.decide(self.constraints, self.actions)
        action_names = [a.name for a in self.actions]
        self.assertIn(result.action, action_names)

    def test_wh_chain_populated_in_result(self):
        result = self.engine.decide(self.constraints, self.actions, goal="test")
        self.assertIn("why", result.wh_chain)
        self.assertIn("how", result.wh_chain)

    def test_experience_stored_after_decide(self):
        initial = self.store.count()
        self.engine.decide(self.constraints, self.actions)
        self.assertEqual(self.store.count(), initial + 1)

    def test_record_result_updates_store(self):
        result = self.engine.decide(self.constraints, self.actions)
        self.engine.record_result(result.action, "success")
        records = self.store.all()
        completed = [r for r in records if r.get("result") == "success"]
        self.assertGreater(len(completed), 0)

    def test_summary_output(self):
        result = self.engine.decide(self.constraints, self.actions)
        summary = result.summary()
        self.assertIn(result.action, summary)
        self.assertIn(result.verdict.upper().replace("_", " "), summary)

    def test_high_risk_action_not_preferred_over_safe(self):
        # With high-priority safety constraint, high-risk action should lose
        constraints = self.extractor.extract({
            "safety": "critical",
            "visibility": "poor",
        })
        dangerous = Action("dangerous_move", outcome_score=9, risk_probability=0.9)
        safe = Action("safe_wait", outcome_score=4, risk_probability=0.05)
        result = self.engine.decide(constraints, [dangerous, safe])
        self.assertEqual(result.action, "safe_wait")

    def test_pattern_consolidation_after_multiple_cycles(self):
        pat_tmp = tempfile.NamedTemporaryFile(suffix=".json", delete=False)
        pat_tmp.close()
        pattern_store = PatternStore(path=pat_tmp.name)

        for _ in range(4):
            result = self.engine.decide(self.constraints, self.actions)
            self.engine.record_result(result.action, "success")

        count = pattern_store.consolidate(self.store)
        self.assertGreaterEqual(count, 0)
        os.unlink(pat_tmp.name)


class TestEdgeCases(unittest.TestCase):

    def setUp(self):
        self.tmp = tempfile.NamedTemporaryFile(suffix=".json", delete=False)
        self.tmp.close()
        self.store = ExperienceStore(path=self.tmp.name)
        self.engine = DecisionEngine(experience_store=self.store)

    def tearDown(self):
        os.unlink(self.tmp.name)

    def test_single_action_still_decides(self):
        constraints = [Constraint("road", "clear", priority="low")]
        actions = [Action("only_option", outcome_score=5, risk_probability=0.2)]
        result = self.engine.decide(constraints, actions)
        self.assertEqual(result.action, "only_option")

    def test_empty_goal_still_works(self):
        constraints = [Constraint("traffic", "low")]
        actions = [Action("proceed", outcome_score=7, risk_probability=0.1)]
        result = self.engine.decide(constraints, actions, goal="")
        self.assertIsNotNone(result)

    def test_no_constraints_still_produces_decision(self):
        actions = [
            Action("option_a", outcome_score=8, risk_probability=0.1),
            Action("option_b", outcome_score=4, risk_probability=0.05),
        ]
        result = self.engine.decide([], actions)
        self.assertIn(result.action, ["option_a", "option_b"])


if __name__ == "__main__":
    unittest.main()
