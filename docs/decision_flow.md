# CDRS Decision Flow

---

## Full Cycle

```
INPUT SITUATION
      │
      ▼
┌─────────────────────────┐
│  1. Extract Constraints │  ← ConstraintExtractor
│     environment         │
│     limits / priorities │
│     risk conditions     │
└──────────┬──────────────┘
           │
           ▼
┌─────────────────────────┐
│  2. WH-Chain            │  ← WHChain
│     WHY  → intent       │
│     WHAT → requirements │
│     WHO  → entities     │
│     WHEN → conditions   │
│     WHERE→ context      │
│     HOW  → strategy     │
└──────────┬──────────────┘
           │
           ▼
┌─────────────────────────┐
│  3. Retrieve Patterns   │  ← ConstraintMatcher + PatternStore
│     similar past cases  │
│     constraint-based    │
└──────────┬──────────────┘
           │
           ▼
┌─────────────────────────┐
│  4. Generate Actions    │  ← Action definitions
│     candidate options   │
│     with outcome scores │
│     and risk values     │
└──────────┬──────────────┘
           │
           ▼
┌─────────────────────────┐
│  5. Predict Outcomes    │  ← Evaluator (outcome scoring)
│     expected benefit    │
│     per action          │
└──────────┬──────────────┘
           │
           ▼
┌─────────────────────────┐
│  6. Evaluate Risks      │  ← Evaluator (risk weighting)
│     failure probability │
│     severity            │
│     importance weights  │
└──────────┬──────────────┘
           │
           ▼
┌─────────────────────────┐
│  7. Construct WHY       │  ← WHYConstructor
│     benefit_why         │
│     risk_why            │
│     condition_why       │
│     failure_why         │
│     summary             │
└──────────┬──────────────┘
           │
           ▼
┌─────────────────────────┐
│  8. Assign Weights      │  ← Evaluator (priority-based)
│     high priority → 10  │
│     medium → 5          │
│     low → 2             │
└──────────┬──────────────┘
           │
           ▼
┌─────────────────────────┐
│  9. Compare + Score     │  ← Evaluator.score_all()
│     benefit vs risk     │
│     vs feasibility      │
└──────────┬──────────────┘
           │
           ▼
┌─────────────────────────────────────────┐
│  10. Produce Decision                   │
│      verdict: YES/NO/CONDITIONAL        │
│      confidence: 0.0-1.0                │
│      explanation: dynamic WHY           │
│      conditions: what must hold         │
└──────────┬──────────────────────────────┘
           │
           ▼
┌─────────────────────────┐
│  11. Execute Action     │  ← External system
└──────────┬──────────────┘
           │
           ▼
┌─────────────────────────┐
│  12. Observe Result     │  ← record_result("success"|"failure")
└──────────┬──────────────┘
           │
           ▼
┌─────────────────────────┐
│  13. Store Experience   │  ← ExperienceStore
│     full context saved  │
└──────────┬──────────────┘
           │
           ▼
┌─────────────────────────┐
│  14. Consolidate        │  ← PatternStore.consolidate()
│     (scheduled process) │
│     extract patterns    │
│     from many sessions  │
└─────────────────────────┘
```

---

## Key Rules

- Steps 1-2 are mandatory before any scoring begins
- Step 3 is advisory — patterns inform but do not override current reasoning
- Step 7 WHY is always constructed dynamically — never retrieved as a fixed answer
- Step 14 runs on a schedule, not inline with every decision
- Confidence degrades when risk is high or constraint similarity is low
