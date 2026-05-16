"""
Tests for CDRS memory components.
"""

import sys
import os
import tempfile
import json

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

import unittest
from prototype.memory.experience_store import ExperienceStore
from prototype.memory.pattern_store import PatternStore


class TestExperienceStore(unittest.TestCase):

    def setUp(self):
        # Use a temp file so tests don't pollute real data
        self.tmp = tempfile.NamedTemporaryFile(suffix=".json", delete=False)
        self.tmp.close()
        self.store = ExperienceStore(path=self.tmp.name)

    def tearDown(self):
        os.unlink(self.tmp.name)

    def _sample_record(self, action="overtake", result=None):
        return {
            "constraints": [{"name": "traffic", "value": "medium", "priority": "medium", "category": "environment"}],
            "action": action,
            "goal": "reach faster",
            "verdict": "conditional_yes",
            "confidence": 0.72,
            "explanation": "Safe under current conditions.",
            "result": result,
        }

    def test_save_and_count(self):
        self.store.save(self._sample_record())
        self.assertEqual(self.store.count(), 1)

    def test_save_persists_to_file(self):
        self.store.save(self._sample_record())
        with open(self.tmp.name) as f:
            data = json.load(f)
        self.assertEqual(len(data), 1)

    def test_all_returns_all_records(self):
        self.store.save(self._sample_record("overtake"))
        self.store.save(self._sample_record("stay_behind"))
        self.assertEqual(len(self.store.all()), 2)

    def test_update_latest_sets_result(self):
        self.store.save(self._sample_record("overtake", result=None))
        updated = self.store.update_latest("overtake", "success")
        self.assertTrue(updated)
        record = self.store.all()[-1]
        self.assertEqual(record["result"], "success")

    def test_update_latest_returns_false_if_not_found(self):
        self.store.save(self._sample_record("overtake", result=None))
        updated = self.store.update_latest("nonexistent", "success")
        self.assertFalse(updated)

    def test_successful_filters_correctly(self):
        self.store.save(self._sample_record("overtake", result="success"))
        self.store.save(self._sample_record("stay_behind", result="failure"))
        self.store.save(self._sample_record("slow_down", result=None))
        self.assertEqual(len(self.store.successful()), 1)
        self.assertEqual(len(self.store.failed()), 1)

    def test_clear_removes_all(self):
        self.store.save(self._sample_record())
        self.store.save(self._sample_record())
        self.store.clear()
        self.assertEqual(self.store.count(), 0)

    def test_timestamp_added_on_save(self):
        self.store.save(self._sample_record())
        record = self.store.all()[0]
        self.assertIn("timestamp", record)

    def test_reload_from_file(self):
        self.store.save(self._sample_record("overtake"))
        reloaded = ExperienceStore(path=self.tmp.name)
        self.assertEqual(reloaded.count(), 1)

    def test_summary_output(self):
        self.store.save(self._sample_record("a", result="success"))
        self.store.save(self._sample_record("b", result="failure"))
        summary = self.store.summary()
        self.assertIn("2 records", summary)


class TestPatternStore(unittest.TestCase):

    def setUp(self):
        self.exp_tmp = tempfile.NamedTemporaryFile(suffix=".json", delete=False)
        self.pat_tmp = tempfile.NamedTemporaryFile(suffix=".json", delete=False)
        self.exp_tmp.close()
        self.pat_tmp.close()
        self.exp_store = ExperienceStore(path=self.exp_tmp.name)
        self.pattern_store = PatternStore(path=self.pat_tmp.name)

    def tearDown(self):
        os.unlink(self.exp_tmp.name)
        os.unlink(self.pat_tmp.name)

    def _add_experience(self, action, result, constraints=None):
        constraints = constraints or [
            {"name": "traffic", "value": "medium", "priority": "medium", "category": "environment"},
            {"name": "visibility", "value": "good", "priority": "high", "category": "environment"},
        ]
        self.exp_store.save({
            "constraints": constraints,
            "action": action,
            "goal": "reach faster",
            "verdict": "conditional_yes",
            "confidence": 0.72,
            "explanation": "Test explanation.",
            "result": result,
        })

    def test_consolidate_insufficient_data(self):
        self._add_experience("overtake", "success")
        count = self.pattern_store.consolidate(self.exp_store)
        self.assertEqual(count, 0)

    def test_consolidate_produces_patterns(self):
        for _ in range(3):
            self._add_experience("overtake", "success")
        count = self.pattern_store.consolidate(self.exp_store)
        self.assertGreater(count, 0)

    def test_pattern_success_rate_correct(self):
        self._add_experience("overtake", "success")
        self._add_experience("overtake", "success")
        self._add_experience("overtake", "failure")
        self.pattern_store.consolidate(self.exp_store)
        patterns = self.pattern_store.all()
        self.assertTrue(len(patterns) > 0)
        p = patterns[0]
        self.assertAlmostEqual(p["success_rate"], 2/3, places=2)

    def test_lookup_finds_similar_patterns(self):
        for _ in range(3):
            self._add_experience("overtake", "success")
        self.pattern_store.consolidate(self.exp_store)
        current = [
            {"name": "traffic", "value": "medium"},
            {"name": "visibility", "value": "good"},
        ]
        results = self.pattern_store.lookup(current)
        self.assertGreater(len(results), 0)

    def test_summary_no_patterns(self):
        summary = self.pattern_store.summary()
        self.assertIn("no patterns", summary)


if __name__ == "__main__":
    unittest.main()
