"""
Example: Vehicle Overtake Decision

Scenario: A vehicle is behind a slow-moving truck on a highway.
The agent must decide whether to overtake.

Demonstrates: constraint extraction, WH-chain, multi-WHY reasoning,
conditional decision output.
"""

from prototype.engine.constraint_extractor import ConstraintExtractor
from prototype.engine.decision_engine import DecisionEngine
from prototype.models.action import Action

print("=" * 60)
print("CDRS — Overtake Decision Example")
print("=" * 60)
print()

# --- Step 1: Define raw constraints ---
raw_constraints = {
    "traffic": "medium",
    "visibility": "good",
    "road": "highway",
    "weather": "clear",
    "safety": "normal",
}

extractor = ConstraintExtractor()
constraints = extractor.extract(raw_constraints)

print(extractor.summarize(constraints))
print()

# --- Step 2: Define candidate actions ---
actions = [
    Action(
        name="overtake",
        outcome_score=8,
        risk_probability=0.35,
        description="passing the slow truck at increased speed",
        failure_conditions=["blind turn ahead", "high traffic", "low visibility"],
    ),
    Action(
        name="stay_behind",
        outcome_score=5,
        risk_probability=0.05,
        description="maintaining safe following distance",
        failure_conditions=[],
    ),
    Action(
        name="slow_down",
        outcome_score=3,
        risk_probability=0.02,
        description="reducing speed and waiting for a safe gap",
        failure_conditions=[],
    ),
]

# --- Step 3: Run decision engine (verbose mode) ---
engine = DecisionEngine()

print("Running CDRS decision cycle...\n")
result = engine.decide(
    constraints=constraints,
    actions=actions,
    goal="reach destination faster",
    domain="driving",
    verbose=True,
)

print()
print("=" * 60)
print("FINAL DECISION")
print("=" * 60)
print(result.summary())
print()

# --- Step 4: Simulate execution and record result ---
engine.record_result(action=result.action, result="success")
print(f"Result recorded: '{result.action}' → success")
print()
print(engine.store.summary())
