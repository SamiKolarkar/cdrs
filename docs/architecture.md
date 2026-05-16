# CDRS Architecture — Seven Layers

---

## System Overview

```
┌────────────────────────────────────────────────────┐
│             CDRS Decision Cycle                    │
├────────────────────────────────────────────────────┤
│  Layer 1: Constraint Layer                         │
│  → Extract environment, limits, priorities         │
├────────────────────────────────────────────────────┤
│  Layer 2: WH-Chain Layer                           │
│  → WHY → WHAT → WHO → WHEN → WHERE → HOW          │
├────────────────────────────────────────────────────┤
│  Layer 3: Action Layer                             │
│  → Generate decision candidates                    │
├────────────────────────────────────────────────────┤
│  Layer 4: Outcome Layer                            │
│  → Predict expected effect per action              │
├────────────────────────────────────────────────────┤
│  Layer 5: Risk Layer                               │
│  → Identify failure conditions + severity          │
├────────────────────────────────────────────────────┤
│  Layer 6: WHY Construction Layer                   │
│  → Compose explanation dynamically                 │
├────────────────────────────────────────────────────┤
│  Layer 7: Decision + Learning Layer                │
│  → Decide, execute, store, consolidate             │
└────────────────────────────────────────────────────┘
```

---

## Layer 1 — Constraint Layer

**File:** `prototype/engine/constraint_extractor.py`

**Responsibility:** Map the decision environment before any reasoning begins.

Every decision cycle starts here. No action is evaluated without a constraint map.

**Constraint schema:**
```python
Constraint(
    name="visibility",
    value="good",
    priority="high",     # high | medium | low
    category="environment"
)
```

**Priority inference rules:**
- `safety`, `visibility`, `emergency`, `user_priority` → `high`
- `traffic`, `weather`, `load` → `medium`
- Value keywords `"critical"`, `"dangerous"` → elevate to `high`

---

## Layer 2 — WH-Chain Layer *(CDRS Differentiator)*

**File:** `prototype/engine/wh_chain.py`

**Responsibility:** Structured goal interrogation before action selection.

This layer is the primary differentiator between CDRS and standard agent architectures. HOW is always computed last — it is the *output* of reasoning, not the starting point.

**Chain order:**
```
WHY    → What is the underlying intent?
WHAT   → What is needed to fulfill it?
WHO    → What entities/resources are involved?
WHEN   → Under what conditions does this apply?
WHERE  → In what environment?
HOW    → Execution strategy (derived from all above)
```

**Stopping condition:** The chain halts when further decomposition produces no new actionable information. Useful understanding > infinite understanding.

---

## Layer 3 — Action Layer

**File:** `prototype/models/action.py`

**Responsibility:** Define candidate actions with predicted scores and risks.

```python
Action(
    name="overtake",
    outcome_score=8,          # 0-10 benefit scale
    risk_probability=0.35,    # 0.0-1.0 failure probability
    failure_conditions=["blind turn", "high traffic"],
    description="passing the truck at increased speed"
)
```

In v0.1, actions are defined externally. Future versions: automatic action generation from domain plugins.

---

## Layer 4 — Outcome Layer

**File:** `prototype/engine/evaluator.py` (outcome scoring)

**Responsibility:** Predict expected effects per action.

In v0.1, outcome scores are provided with actions. Future versions: predict outcomes from constraint + action + past experience combinations.

---

## Layer 5 — Risk Layer

**File:** `prototype/engine/evaluator.py` (risk weighting)

**Responsibility:** Scale risk by importance weights from constraint priorities.

**Safety weight formula:**
```
safety_weight = max priority weight among constraints
             = 10.0 if any high-priority constraint exists
             = 5.0  if medium-priority only
             = 2.0  if low-priority only
```

**Score formula:**
```
score = outcome_score - (risk_probability × safety_weight)
```

---

## Layer 6 — WHY Construction Layer

**File:** `prototype/engine/why_constructor.py`

**Responsibility:** Compose WHY dynamically from four types.

**WHY is never stored as a fixed answer.** It is generated from:

| WHY Type | Derived From |
|---|---|
| benefit_why | outcome_score + goal + constraint context |
| risk_why | risk_probability + high-risk constraint values |
| condition_why | high-priority constraints that must hold |
| failure_why | action.failure_conditions |
| summary | composition of all four |

**Formula:**
```
WHY = f(outcomes, constraints, risks, goals, timing)
```

---

## Layer 7 — Decision + Learning Layer

**Files:** `prototype/engine/decision_engine.py`, `prototype/memory/`

**Responsibility:** Produce verdict, store experience, consolidate patterns.

**Decision output:**
```python
Decision(
    action="overtake",
    verdict="conditional_yes",   # yes | no | conditional_yes | conditional_no
    confidence=0.72,
    explanation="...",
    conditions=["visibility remains good", ...],
    wh_chain={...},
    score=4.5
)
```

**Verdict rules:**
| Score | Risk | Verdict |
|---|---|---|
| ≥ 6, risk ≤ 0.2 | → yes | |
| ≥ 3, risk ≤ 0.5 | → conditional_yes | |
| ≥ 0, risk ≤ 0.7 | → conditional_no | |
| < 0 or risk > 0.7 | → no | |

---

## Cross-Session Pattern Consolidation

**File:** `prototype/memory/pattern_store.py`

The "dreaming layer" — runs after sessions, not within them.

```
Many sessions
    ↓
PatternStore.consolidate(experience_store)
    ↓
Extract: which constraint configurations predict success or failure
    ↓
Store patterns for future retrieval
    ↓
Future decisions informed by accumulated experience
```

Retrieval is **constraint-based**, not text-based — patterns are matched by constraint configuration similarity.

---

## Open Implementation Problems

1. **Constraint similarity metric:** Jaccard on name-value pairs (v0.1). Better: weighted by priority, or embedding-based.
2. **WHY composition quality:** Templates work but are rigid. LLM composition with component injection is the v1.0 target.
3. **Stopping depth for recursive WHY:** Currently hardcoded. Needs a programmatic usefulness threshold.
4. **Weight learning:** Importance weights are static in v0.1. Should be learned from outcome history.
5. **Cross-agent pattern sharing:** Can patterns from one agent instance safely inform another? Open question.


---

## Formal Runtime Principles

CDRS separates reasoning into machine-usable layers:

```text
Context
→ Objective extraction
→ Constraint weighting
→ Tradeoff analysis
→ Action generation
→ Risk evaluation
→ Decision
→ Feedback consolidation
```

The architecture intentionally avoids:
- unrestricted free-form reasoning
- unconstrained autonomous planning
- opaque hidden objective mutation

All reasoning should remain:
- inspectable
- structured
- reproducible
- constraint-bound

---

## Decision Arbitration

When multiple WHY paths conflict, the coordinator layer resolves decisions through weighted evaluation.

Example:

```json
{
  "speed_priority": 6,
  "safety_priority": 10,
  "cost_priority": 4
}
```

The final action is selected through:
- constraint weighting
- risk scoring
- confidence thresholds
- outcome prediction

