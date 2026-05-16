"""
Example: Natural Language Input → CDRS Decision

This is the real working demo.

You describe a situation in plain English.
Phi-2 (via Ollama) extracts the constraints.
CDRS runs the full 7-layer reasoning pipeline.
Phi-2 composes the WHY explanation in natural language.
You get a decision with a confidence score and reasoning.

Requirements:
    Ollama running: ollama serve
    Model pulled:   ollama pull phi:latest

Run:
    PYTHONPATH=. python prototype/examples/natural_input_example.py
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))

from prototype.engine.decision_engine import DecisionEngine
from prototype.engine.ollama_client import OllamaClient
from prototype.models.action import Action
import tempfile
from prototype.memory.experience_store import ExperienceStore

# ------------------------------------------------------------------
# Check Ollama is running
# ------------------------------------------------------------------

client = OllamaClient()
if not client.is_available():
    print("ERROR: Ollama is not running or phi:latest is not loaded.")
    print()
    print("To fix:")
    print("  1. Start Ollama:     ollama serve")
    print("  2. Pull the model:   ollama pull phi:latest")
    print("  3. Run this again.")
    sys.exit(1)

print("Ollama is running. Model: phi:latest")
print()

# ------------------------------------------------------------------
# Scenario 1: Driving — natural language situation
# ------------------------------------------------------------------

print("=" * 60)
print("SCENARIO 1: Driving Decision")
print("=" * 60)

situation_1 = (
    "I am driving on a busy city road. It is raining heavily "
    "and visibility is poor. There is a slow truck ahead of me."
)

actions_1 = [
    Action(
        name="overtake",
        outcome_score=7,
        risk_probability=0.70,
        description="passing the truck at increased speed",
        failure_conditions=["poor visibility", "wet road", "heavy traffic"],
    ),
    Action(
        name="follow_safely",
        outcome_score=5,
        risk_probability=0.08,
        description="maintaining safe distance behind the truck",
        failure_conditions=[],
    ),
    Action(
        name="slow_down_and_wait",
        outcome_score=3,
        risk_probability=0.03,
        description="reducing speed and waiting for conditions to improve",
        failure_conditions=[],
    ),
]

tmp1 = tempfile.NamedTemporaryFile(suffix=".json", delete=False)
tmp1.close()
store1 = ExperienceStore(path=tmp1.name)
engine1 = DecisionEngine(experience_store=store1)

result1 = engine1.decide_from_text(
    situation=situation_1,
    actions=actions_1,
    goal="reach destination safely",
    domain="driving",
    verbose=True,
)

engine1.record_result(result1.action, "success")
os.unlink(tmp1.name)

# ------------------------------------------------------------------
# Scenario 2: Task scheduling — different domain
# ------------------------------------------------------------------

print()
print("=" * 60)
print("SCENARIO 2: Backend Task Scheduling")
print("=" * 60)

situation_2 = (
    "The server memory is critically high. "
    "A high-priority user request just arrived. "
    "Response time is critical and the task queue is large."
)

actions_2 = [
    Action(
        name="process_immediately",
        outcome_score=9,
        risk_probability=0.65,
        description="processing the request right now",
        failure_conditions=["memory exhaustion", "system crash"],
    ),
    Action(
        name="defer_low_priority_tasks",
        outcome_score=7,
        risk_probability=0.10,
        description="freeing memory by deferring non-critical tasks first",
        failure_conditions=["starvation of deferred tasks if not resumed"],
    ),
    Action(
        name="queue_and_schedule",
        outcome_score=5,
        risk_probability=0.08,
        description="adding request to the queue with high priority flag",
        failure_conditions=["deadline missed if queue is too long"],
    ),
]

tmp2 = tempfile.NamedTemporaryFile(suffix=".json", delete=False)
tmp2.close()
store2 = ExperienceStore(path=tmp2.name)
engine2 = DecisionEngine(experience_store=store2)

result2 = engine2.decide_from_text(
    situation=situation_2,
    actions=actions_2,
    goal="handle the request without system failure",
    domain="task_scheduling",
    verbose=True,
)

engine2.record_result(result2.action, "success")
os.unlink(tmp2.name)

# ------------------------------------------------------------------
# Summary
# ------------------------------------------------------------------

print()
print("=" * 60)
print("SUMMARY")
print("=" * 60)
print(f"Scenario 1 → {result1.verdict.upper():16s} | "
      f"{result1.action:<25} | confidence: {result1.confidence:.2f}")
print(f"Scenario 2 → {result2.verdict.upper():16s} | "
      f"{result2.action:<25} | confidence: {result2.confidence:.2f}")
print()
print("WHY explanations were composed by Phi-2 (Ollama) from")
print("real constraint values — not from pre-written templates.")
