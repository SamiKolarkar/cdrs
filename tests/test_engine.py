"""
Tests for CDRS engine components.
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

import unittest
from prototype.models.constraint import Constraint
from prototype.models.action import Action
from prototype.engine.constraint_extractor import ConstraintExtractor
from prototype.engine.wh_chain import WHChain
from prototype.engine.why_constructor import WHYConstructor
from prototype.engine.evaluator import Evaluator
from prototype.engine.constraint_matcher import ConstraintMatcher


class TestConstraintExtractor(unittest.TestCase):

    def setUp(self):
        self.extractor = ConstraintExtractor()

    def test_extracts_correct_count(self):
        raw = {"traffic": "medium", "visibility": "good", "road": "highway"}
        result = self.extractor.extract(raw)
        self.assertEqual(len(result), 3)

    def test_infers_high_priority_for_visibility(self):
        raw = {"visibility": "good"}
        result = self.extractor.extract(raw)
        self.assertEqual(result[0].priority, "high")

    def test_infers_medium_priority_for_traffic(self):
        raw = {"traffic": "medium"}
        result = self.extractor.extract(raw)
        self.assertEqual(result[0].priority, "medium")

    def test_value_critical_elevates_priority(self):
        raw = {"load": "critical"}
        result = self.extractor.extract(raw)
        self.assertEqual(result[0].priority, "high")

    def test_environment_category(self):
        raw = {"road": "highway"}
        result = self.extractor.extract(raw)
        self.assertEqual(result[0].category, "environment")

    def test_summarize_output(self):
        raw = {"visibility": "good", "traffic": "high"}
        constraints = self.extractor.extract(raw)
        summary = self.extractor.summarize(constraints)
        self.assertIn("visibility", summary)
        self.assertIn("traffic", summary)


class TestWHChain(unittest.TestCase):

    def setUp(self):
        self.wh = WHChain()
        self.constraints = [
            Constraint("visibility", "good", priority="high"),
            Constraint("road", "highway", priority="low"),
        ]

    def test_chain_has_all_keys(self):
        result = self.wh.run("reach faster", self.constraints)
        for key in ["why", "what", "who", "when", "where", "how"]:
            self.assertIn(key, result)

    def test_all_values_non_empty(self):
        result = self.wh.run("reach faster", self.constraints)
        for key, value in result.items():
            # confidence_modifier of 0.0 is valid (no danger constraints)
            if key == "confidence_modifier":
                self.assertIsNotNone(value)
            else:
                self.assertTrue(value, f"WHY chain key '{key}' is empty")

    def test_why_contains_goal(self):
        result = self.wh.run("reach destination faster", self.constraints)
        self.assertIn("reach destination faster", result["why"])

    def test_when_contains_high_priority_constraint(self):
        result = self.wh.run("test goal", self.constraints)
        self.assertIn("visibility", result["when"])

    def test_format_output(self):
        chain = self.wh.run("goal", self.constraints)
        formatted = self.wh.format(chain)
        self.assertIn("WHY", formatted)
        self.assertIn("HOW", formatted)


class TestWHYConstructor(unittest.TestCase):

    def setUp(self):
        self.constructor = WHYConstructor()
        self.constraints = [
            Constraint("visibility", "good", priority="high"),
            Constraint("traffic", "medium", priority="medium"),
        ]
        self.action = Action(
            "overtake",
            outcome_score=8,
            risk_probability=0.35,
            description="passing the truck at speed",
            failure_conditions=["blind turn", "high traffic"],
        )

    def test_returns_all_why_keys(self):
        result = self.constructor.construct(self.action, self.constraints)
        for key in ["benefit_why", "risk_why", "condition_why", "failure_why", "summary"]:
            self.assertIn(key, result)

    def test_all_values_non_empty(self):
        result = self.constructor.construct(self.action, self.constraints)
        for key, value in result.items():
            # llm_used=False is valid (Ollama not running in test env)
            if key == "llm_used":
                self.assertIsNotNone(value)
            else:
                self.assertTrue(value, f"WHY key '{key}' is empty")

    def test_failure_why_contains_failure_condition(self):
        result = self.constructor.construct(self.action, self.constraints)
        self.assertIn("blind turn", result["failure_why"])

    def test_condition_why_references_high_priority(self):
        result = self.constructor.construct(self.action, self.constraints)
        self.assertIn("visibility", result["condition_why"])

    def test_high_risk_reflected_in_risk_why(self):
        risky = Action("risky_action", outcome_score=5, risk_probability=0.8)
        result = self.constructor.construct(risky, self.constraints)
        self.assertIn("high", result["risk_why"].lower())


class TestEvaluator(unittest.TestCase):

    def setUp(self):
        self.evaluator = Evaluator()
        self.constraints_high = [
            Constraint("visibility", "good", priority="high"),
        ]
        self.constraints_low = [
            Constraint("road", "highway", priority="low"),
        ]

    def test_high_priority_lowers_score_more(self):
        action = Action("test", outcome_score=8, risk_probability=0.5)
        score_high = self.evaluator.score(action, self.constraints_high)
        score_low = self.evaluator.score(action, self.constraints_low)
        self.assertLess(score_high, score_low)

    def test_score_all_sorts_descending(self):
        actions = [
            Action("bad", outcome_score=2, risk_probability=0.8),
            Action("good", outcome_score=9, risk_probability=0.1),
            Action("medium", outcome_score=5, risk_probability=0.3),
        ]
        scored = self.evaluator.score_all(actions, self.constraints_low)
        scores = [s for s, _ in scored]
        self.assertEqual(scores, sorted(scores, reverse=True))

    def test_yes_verdict_high_score_low_risk(self):
        verdict, confidence = self.evaluator.verdict(score=8, risk=0.05)
        self.assertEqual(verdict, "yes")
        self.assertGreater(confidence, 0.7)

    def test_no_verdict_negative_score(self):
        verdict, confidence = self.evaluator.verdict(score=-2, risk=0.9)
        self.assertEqual(verdict, "no")

    def test_conditional_yes_moderate(self):
        verdict, confidence = self.evaluator.verdict(score=5, risk=0.3)
        self.assertEqual(verdict, "conditional_yes")

    def test_confidence_in_range(self):
        for score in [-5, 0, 5, 10]:
            for risk in [0.0, 0.5, 1.0]:
                _, conf = self.evaluator.verdict(score, risk)
                self.assertGreaterEqual(conf, 0.0)
                self.assertLessEqual(conf, 1.0)


class TestConstraintMatcher(unittest.TestCase):

    def setUp(self):
        self.matcher = ConstraintMatcher()
        self.current = [
            {"name": "traffic", "value": "medium"},
            {"name": "visibility", "value": "good"},
        ]

    def test_identical_configs_score_one(self):
        score = self.matcher.similarity(self.current, self.current)
        self.assertAlmostEqual(score, 1.0)

    def test_empty_configs_score_one(self):
        score = self.matcher.similarity([], [])
        self.assertAlmostEqual(score, 1.0)

    def test_completely_different_score_zero(self):
        other = [
            {"name": "cpu", "value": "high"},
            {"name": "memory", "value": "low"},
        ]
        score = self.matcher.similarity(self.current, other)
        self.assertAlmostEqual(score, 0.0)

    def test_partial_overlap(self):
        partial = [
            {"name": "traffic", "value": "medium"},
            {"name": "weather", "value": "rain"},
        ]
        score = self.matcher.similarity(self.current, partial)
        self.assertGreater(score, 0.0)
        self.assertLess(score, 1.0)

    def test_find_similar_returns_above_threshold(self):
        experiences = [
            {"constraints": self.current, "action": "overtake", "result": "success"},
            {"constraints": [{"name": "cpu", "value": "high"}], "action": "wait", "result": "success"},
        ]
        results = self.matcher.find_similar(self.current, experiences, threshold=0.5)
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0]["action"], "overtake")

    def test_find_similar_respects_top_k(self):
        experiences = [
            {"constraints": self.current, "action": f"action_{i}", "result": "success"}
            for i in range(10)
        ]
        results = self.matcher.find_similar(self.current, experiences, top_k=3)
        self.assertLessEqual(len(results), 3)


if __name__ == "__main__":
    unittest.main()
