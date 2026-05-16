"""
Example: Task Scheduling Decision

Scenario: A backend system must decide how to prioritize a set of tasks
given memory pressure, a time-critical deadline, and a user priority flag.

Demonstrates: resource constraint handling, different domain,
cross-session pattern retrieval after multiple runs.
"""

from prototype.engine.constraint_extractor import ConstraintExtractor
from prototype.engine.decision_engine import DecisionEngine
from prototype.memory.pattern_store import PatternStore
from prototype.models.action import Action

print("=" * 60)
print("CDRS — Task Scheduling Decision Example")
print("=" * 60)
print()

# --- Constraints ---
raw_constraints = {
    "memory": "high",
    "time_critical": "yes",
    "user_priority": "high",
    "cpu_load": "medium",
    "queue_depth": "large",
}

extractor = ConstraintExtractor()
constraints = extractor.extract(raw_constraints)

print(extractor.summarize(constraints))
print()

# --- Candidate actions ---
actions = [
    Action(
        name="process_immediately",
        outcome_score=9,
        risk_probability=0.45,
        description="processing the high-priority task right now",
        failure_conditions=["memory exhaustion", "cpu spike"],
    ),
    Action(
        name="queue_and_batch",
        outcome_score=6,
        risk_probability=0.10,
        description="batching with upcoming tasks for efficiency",
        failure_conditions=["deadline exceeded if queue grows"],
    ),
    Action(
        name="defer_low_priority",
        outcome_score=7,
        risk_probability=0.08,
        description="deferring non-critical tasks to free resources",
        failure_conditions=["starvation of deferred tasks"],
    ),
]

# --- Decision ---
engine = DecisionEngine()

print("Running CDRS decision cycle...\n")
result = engine.decide(
    constraints=constraints,
    actions=actions,
    goal="meet the deadline without system failure",
    domain="task_scheduling",
    verbose=True,
)

print()
print("=" * 60)
print("FINAL DECISION")
print("=" * 60)
print(result.summary())
print()

# --- Record result ---
engine.record_result(action=result.action, result="success")
print(f"Result recorded: '{result.action}' → success")
print()

# --- Demonstrate pattern consolidation ---
print("Running pattern consolidation (dreaming layer)...")
pattern_store = PatternStore()
count = pattern_store.consolidate(engine.store)
print(f"Patterns consolidated: {count}")
print()
print(pattern_store.summary())
