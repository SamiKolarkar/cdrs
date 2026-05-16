"""
CDRS vs Baseline Benchmark

Compares CDRS decision quality against a naive baseline
that picks the highest outcome_score without constraint
weighting, WH-chain interrogation, or risk balancing.

This benchmark measures:
  1. Risk awareness     — does CDRS correctly avoid high-risk actions
                          under safety-critical constraints?
  2. Constraint respect — does CDRS change its decision when
                          constraints change, unlike the baseline?
  3. Conditional output — does CDRS produce nuanced verdicts
                          rather than binary yes/no?

Original concept: Sami Ahmed Yusuf Kolarkar, 2026.
"""

import sys
import os
import tempfile

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from prototype.models.constraint import Constraint
from prototype.models.action import Action
from prototype.engine.constraint_extractor import ConstraintExtractor
from prototype.engine.decision_engine import DecisionEngine
from prototype.memory.experience_store import ExperienceStore


# ------------------------------------------------------------------
# Baseline: no constraint weighting, no WH-chain, picks max score
# ------------------------------------------------------------------

def baseline_decide(actions):
    """Naive baseline: always picks highest outcome_score."""
    best = max(actions, key=lambda a: a.outcome_score)
    return {
        "action": best.name,
        "verdict": "yes",
        "confidence": 0.5,
        "explanation": f"Selected '{best.name}' because it has the highest outcome score.",
    }


# ------------------------------------------------------------------
# Test scenarios
# ------------------------------------------------------------------

SCENARIOS = [
    {
        "name": "Dangerous overtake — safety critical",
        "description": (
            "High risk action has highest score. "
            "CDRS should deprioritize it under safety=critical constraint. "
            "Baseline ignores risk entirely."
        ),
        "constraints": {"safety": "critical", "visibility": "poor", "traffic": "high"},
        "actions": [
            Action("aggressive_overtake", outcome_score=9, risk_probability=0.85,
                   failure_conditions=["poor visibility", "high traffic"]),
            Action("wait_for_gap", outcome_score=5, risk_probability=0.05),
            Action("slow_follow", outcome_score=4, risk_probability=0.02),
        ],
        "expected_cdrs_action": "wait_for_gap",
        "expected_baseline_action": "aggressive_overtake",
    },
    {
        "name": "Safe highway — low risk environment",
        "description": (
            "Low-risk environment. High-score action is also low-risk. "
            "Both CDRS and baseline should agree."
        ),
        "constraints": {"visibility": "good", "traffic": "low", "road": "highway"},
        "actions": [
            Action("overtake", outcome_score=8, risk_probability=0.15),
            Action("stay_behind", outcome_score=5, risk_probability=0.05),
        ],
        "expected_cdrs_action": "overtake",
        "expected_baseline_action": "overtake",
    },
    {
        "name": "Time-critical scheduling — resource constrained",
        "description": (
            "High memory pressure. Immediately processing has high benefit "
            "but also high failure risk. CDRS should prefer the safer strategy."
        ),
        "constraints": {"time_critical": "yes", "memory": "critical", "user_priority": "high"},
        "actions": [
            Action("process_immediately", outcome_score=9, risk_probability=0.70,
                   failure_conditions=["memory exhaustion"]),
            Action("defer_low_priority", outcome_score=7, risk_probability=0.08),
            Action("queue_and_batch", outcome_score=6, risk_probability=0.10),
        ],
        "expected_cdrs_action": "defer_low_priority",
        "expected_baseline_action": "process_immediately",
    },
    {
        "name": "Ambiguous — equal scores, different risk",
        "description": (
            "Two actions with identical outcome scores but different risks. "
            "CDRS should pick the lower-risk option."
        ),
        "constraints": {"safety": "normal", "road": "urban"},
        "actions": [
            Action("option_risky", outcome_score=7, risk_probability=0.6),
            Action("option_safe", outcome_score=7, risk_probability=0.1),
        ],
        "expected_cdrs_action": "option_safe",
        "expected_baseline_action": None,  # Tie — baseline picks arbitrarily
    },
]


# ------------------------------------------------------------------
# Run benchmark
# ------------------------------------------------------------------

def run():
    extractor = ConstraintExtractor()
    results = []

    print("=" * 70)
    print("CDRS BENCHMARK — vs Naive Baseline")
    print("=" * 70)
    print()

    cdrs_correct = 0
    baseline_correct = 0
    cdrs_conditional = 0

    for i, scenario in enumerate(SCENARIOS, 1):
        print(f"Scenario {i}: {scenario['name']}")
        print(f"  {scenario['description']}")
        print()

        constraints = extractor.extract(scenario["constraints"])
        actions = scenario["actions"]

        # Run CDRS
        tmp = tempfile.NamedTemporaryFile(suffix=".json", delete=False)
        tmp.close()
        store = ExperienceStore(path=tmp.name)
        engine = DecisionEngine(experience_store=store)
        cdrs_result = engine.decide(constraints, actions, goal="optimal outcome")
        os.unlink(tmp.name)

        # Run baseline
        baseline_result = baseline_decide(actions)

        # Evaluate
        exp_cdrs = scenario["expected_cdrs_action"]
        exp_base = scenario["expected_baseline_action"]

        cdrs_match = cdrs_result.action == exp_cdrs if exp_cdrs else True
        base_match = baseline_result["action"] == exp_base if exp_base else True

        if cdrs_match:
            cdrs_correct += 1
        if base_match:
            baseline_correct += 1
        if "conditional" in cdrs_result.verdict:
            cdrs_conditional += 1

        print(f"  CDRS     → action: {cdrs_result.action:<25} "
              f"verdict: {cdrs_result.verdict:<18} "
              f"confidence: {cdrs_result.confidence:.2f}  "
              f"{'✓' if cdrs_match else '✗'}")
        print(f"  Baseline → action: {baseline_result['action']:<25} "
              f"verdict: {baseline_result['verdict']:<18} "
              f"confidence: {baseline_result['confidence']:.2f}  "
              f"{'✓' if base_match else '✗'}")
        print(f"  WHY: {cdrs_result.explanation[:90]}...")
        print()

    print("=" * 70)
    print("RESULTS SUMMARY")
    print("=" * 70)
    total = len(SCENARIOS)
    print(f"  CDRS correct decisions:     {cdrs_correct}/{total}")
    print(f"  Baseline correct decisions: {baseline_correct}/{total}")
    print(f"  CDRS conditional verdicts:  {cdrs_conditional}/{total}  "
          f"(nuanced output vs baseline's binary yes)")
    print()

    if cdrs_correct > baseline_correct:
        print("  Result: CDRS outperforms baseline on safety-critical scenarios.")
    elif cdrs_correct == baseline_correct:
        print("  Result: CDRS and baseline agree on these scenarios.")
    else:
        print("  Result: Baseline matched more expected outputs — review scoring weights.")

    print()
    print("  Note: This benchmark tests known-answer scenarios.")
    print("  It does not measure generalization across unseen domains.")
    print("  See research/README.md for open evaluation questions.")
    print()

    return cdrs_correct, baseline_correct


if __name__ == "__main__":
    run()
