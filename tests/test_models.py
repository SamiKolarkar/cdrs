"""
Tests for CDRS data models.
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

import unittest
from prototype.models.constraint import Constraint
from prototype.models.action import Action
from prototype.models.outcome import Outcome
from prototype.models.risk import Risk
from prototype.models.decision import Decision


class TestConstraint(unittest.TestCase):

    def test_basic_creation(self):
        c = Constraint("traffic", "high")
        self.assertEqual(c.name, "traffic")
        self.assertEqual(c.value, "high")
        self.assertEqual(c.priority, "medium")

    def test_high_priority_flag(self):
        c = Constraint("visibility", "good", priority="high")
        self.assertTrue(c.is_high_priority())

    def test_medium_not_high_priority(self):
        c = Constraint("traffic", "medium", priority="medium")
        self.assertFalse(c.is_high_priority())

    def test_to_dict(self):
        c = Constraint("road", "highway", priority="low", category="environment")
        d = c.to_dict()
        self.assertEqual(d["name"], "road")
        self.assertEqual(d["value"], "highway")
        self.assertEqual(d["priority"], "low")
        self.assertEqual(d["category"], "environment")


class TestAction(unittest.TestCase):

    def test_basic_creation(self):
        a = Action("overtake", outcome_score=8, risk_probability=0.35)
        self.assertEqual(a.name, "overtake")
        self.assertEqual(a.outcome_score, 8)
        self.assertEqual(a.risk_probability, 0.35)

    def test_failure_conditions_default_empty(self):
        a = Action("stay_behind")
        self.assertEqual(a.failure_conditions, [])

    def test_to_dict(self):
        a = Action("overtake", outcome_score=7, risk_probability=0.3)
        d = a.to_dict()
        self.assertIn("name", d)
        self.assertIn("outcome_score", d)
        self.assertIn("risk_probability", d)


class TestOutcome(unittest.TestCase):

    def test_basic_creation(self):
        o = Outcome("overtake", "reach faster", 8.0)
        self.assertEqual(o.action_name, "overtake")
        self.assertEqual(o.score, 8.0)


class TestRisk(unittest.TestCase):

    def test_basic_creation(self):
        r = Risk("overtake", "collision", 0.35, severity="medium")
        self.assertEqual(r.action_name, "overtake")
        self.assertEqual(r.probability, 0.35)

    def test_critical_high_probability(self):
        r = Risk("action", "failure", 0.8, severity="high")
        self.assertTrue(r.is_critical())

    def test_not_critical_low(self):
        r = Risk("action", "minor", 0.1, severity="low")
        self.assertFalse(r.is_critical())

    def test_weighted_score(self):
        r = Risk("action", "failure", 0.5, severity="high")
        score = r.weighted_score()
        self.assertGreater(score, 0.5)


class TestDecision(unittest.TestCase):

    def test_basic_creation(self):
        d = Decision(
            action="overtake",
            verdict="conditional_yes",
            confidence=0.72,
            explanation="Safe under good visibility.",
        )
        self.assertEqual(d.action, "overtake")
        self.assertEqual(d.verdict, "conditional_yes")
        self.assertAlmostEqual(d.confidence, 0.72)

    def test_summary_contains_verdict(self):
        d = Decision("overtake", "yes", 0.9, "Clear road ahead.")
        summary = d.summary()
        self.assertIn("YES", summary)
        self.assertIn("overtake", summary)

    def test_to_dict(self):
        d = Decision("overtake", "no", 0.2, "Too risky.")
        result = d.to_dict()
        self.assertEqual(result["action"], "overtake")
        self.assertEqual(result["verdict"], "no")


if __name__ == "__main__":
    unittest.main()
