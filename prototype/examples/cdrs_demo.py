"""
CDRS Demo — Real Decision from a Real Situation

Type a situation. CDRS extracts constraints, reasons through the
WH-chain, derives action scores, calls Phi-2 for WHY construction,
and returns a full decision with explanation.

Usage:
    PYTHONPATH=. python prototype/examples/cdrs_demo.py

Requires Ollama running with phi model:
    ollama serve
    ollama pull phi
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "../.."))

from prototype.engine.constraint_extractor import ConstraintExtractor
from prototype.engine.decision_engine import DecisionEngine
from prototype.engine.ollama_client import OllamaClient
from prototype.models.action import Action


# ------------------------------------------------------------------
# Pre-defined scenarios (no typing required in demo mode)
# ------------------------------------------------------------------

SCENARIOS = {
    "1": {
        "name": "Highway overtake",
        "goal": "reach destination faster",
        "domain": "driving",
        "constraints": {
            "traffic": "medium",
            "visibility": "good",
            "road": "highway",
            "weather": "clear",
            "safety": "normal",
        },
        "actions": ["overtake", "stay_behind", "slow_down"],
    },
    "2": {
        "name": "Dangerous conditions overtake",
        "goal": "reach destination faster",
        "domain": "driving",
        "constraints": {
            "traffic": "high",
            "visibility": "poor",
            "road": "urban",
            "weather": "rain",
            "safety": "critical",
        },
        "actions": ["overtake", "stay_behind", "slow_down"],
    },
    "3": {
        "name": "Backend task scheduling",
        "goal": "meet deadline without system failure",
        "domain": "task_scheduling",
        "constraints": {
            "memory": "critical",
            "time_critical": "yes",
            "user_priority": "high",
            "cpu_load": "high",
        },
        "actions": ["process_immediately", "defer_low_priority", "queue_and_batch"],
    },
    "4": {
        "name": "Low-risk server maintenance",
        "goal": "apply security patch with minimal downtime",
        "domain": "devops",
        "constraints": {
            "traffic": "low",
            "time_critical": "no",
            "safety": "normal",
            "user_priority": "medium",
        },
        "actions": ["deploy_now", "schedule_maintenance_window", "defer_patch"],
    },
}


def run_scenario(scenario: dict, engine: DecisionEngine, extractor: ConstraintExtractor):
    print(f"\nScenario: {scenario['name']}")
    print(f"Goal:     {scenario['goal']}")
    print("-" * 60)

    constraints = extractor.extract(scenario["constraints"])
    actions = [Action(name) for name in scenario["actions"]]

    print("Running CDRS decision cycle...\n")
    result = engine.decide(
        constraints=constraints,
        actions=actions,
        goal=scenario["goal"],
        domain=scenario["domain"],
        verbose=True,
    )

    print()
    print("=" * 60)
    print("FINAL DECISION")
    print("=" * 60)
    print(result.summary())
    print()

    # Simulate result
    engine.record_result(result.action, "success")
    print(f"Recorded: '{result.action}' → success")


def main():
    print("=" * 60)
    print("CDRS — Constraint-Driven Reasoning System")
    print("Powered by Phi-2 via Ollama (local, free)")
    print("Original concept: Sami Ahmed Yusuf Kolarkar, 2026")
    print("=" * 60)
    print()

    # Check Ollama
    client = OllamaClient()
    if client.is_available():
        print("✓ Ollama is running — Phi-2 WHY construction active")
    else:
        print("⚠ Ollama not detected — using template fallback")
        print("  To enable: run 'ollama serve' in a terminal")
    print()

    extractor = ConstraintExtractor()
    engine    = DecisionEngine()

    # Show menu
    print("Select a scenario to run:")
    for key, s in SCENARIOS.items():
        print(f"  {key}. {s['name']}")
    print("  a. Run all scenarios")
    print()

    choice = input("Choice [1-4 / a]: ").strip().lower()

    if choice == "a":
        for scenario in SCENARIOS.values():
            run_scenario(scenario, engine, extractor)
    elif choice in SCENARIOS:
        run_scenario(SCENARIOS[choice], engine, extractor)
    else:
        print("Invalid choice. Running scenario 1.")
        run_scenario(SCENARIOS["1"], engine, extractor)

    print()
    print(engine.store.summary())


if __name__ == "__main__":
    main()
