# CDRS Prototype — Module Map

How all Python files in the prototype relate to each other.

```mermaid
graph TD
    subgraph Input
        A[Raw Constraints / Actions / Goal]
    end

    subgraph Layer1["Layer 1 — Constraint Layer"]
        CE[constraint_extractor.py]
    end

    subgraph Layer2["Layer 2 — WH-Chain Layer"]
        WH[wh_chain.py]
    end

    subgraph Layer3to5["Layers 3-5 — Action / Outcome / Risk"]
        ACT[models/action.py]
        OUT[models/outcome.py]
        RISK[models/risk.py]
        EVAL[evaluator.py]
    end

    subgraph Layer6["Layer 6 — WHY Construction"]
        WHY[why_constructor.py]
    end

    subgraph Layer7["Layer 7 — Decision + Learning"]
        DE[decision_engine.py]
        DEC[models/decision.py]
        CM[constraint_matcher.py]
        ES[memory/experience_store.py]
        PS[memory/pattern_store.py]
    end

    subgraph Models["Shared Models"]
        CON[models/constraint.py]
    end

    A --> CE
    CE --> CON
    CON --> WH
    CON --> EVAL
    CON --> WHY
    CON --> CM

    WH --> DE
    EVAL --> DE
    WHY --> DE
    CM --> DE
    ES --> DE

    ACT --> EVAL
    RISK --> EVAL
    OUT --> EVAL

    DE --> DEC
    DE --> ES
    ES --> PS

    subgraph Examples
        OE[examples/overtake_example.py]
        SE[examples/scheduling_example.py]
        MAIN[main.py]
    end

    DE --> OE
    DE --> SE
    OE --> MAIN
    SE --> MAIN
```

---

## Dependency Rules

- `models/` has no internal dependencies — pure data classes
- `engine/` depends on `models/` only
- `memory/` depends on `models/` only
- `engine/decision_engine.py` depends on all other engine modules + memory
- Examples depend only on `engine/decision_engine.py` and `models/`
- No circular dependencies

## Entry Points

| File | Purpose |
|---|---|
| `prototype/main.py` | Run both example scenarios |
| `prototype/examples/overtake_example.py` | Driving decision demo |
| `prototype/examples/scheduling_example.py` | Task scheduling demo |
| `prototype/memory/pattern_store.py` | Trigger pattern consolidation manually |
