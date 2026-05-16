# CDRS Benchmark

Compares CDRS decision quality against a naive baseline across structured scenarios.

---

## Run

```bash
PYTHONPATH=. python benchmark/compare_baseline.py
```

---

## What It Measures

| Metric | Description |
|---|---|
| Risk awareness | Does CDRS correctly avoid high-risk actions under safety constraints? |
| Constraint respect | Does CDRS change its decision when constraints change? |
| Conditional output | Does CDRS produce nuanced verdicts instead of binary yes/no? |
| Confidence calibration | Does confidence reflect actual decision quality? |

---

## Baseline

The baseline is intentionally naive: it picks the action with the highest `outcome_score` and always returns `verdict=yes, confidence=0.5`. It has no constraint awareness, no risk weighting, and no WH-chain reasoning.

This is the simplest plausible alternative — not a sophisticated comparison point. More rigorous comparisons against ReAct, Chain-of-Thought, and standard agent frameworks are open research tasks.

---

## Current Results (v0.1)

| Scenario | CDRS | Baseline |
|---|---|---|
| Dangerous overtake (safety critical) | ✓ wait_for_gap | ✗ aggressive_overtake |
| Safe highway (low risk) | ✓ overtake | ✓ overtake |
| Time-critical scheduling (memory critical) | ✓ defer_low_priority | ✗ process_immediately |
| Equal scores, different risk | ✓ option_safe | ✗ option_risky |

CDRS: 4/4 correct | Baseline: 2/4 correct (fails on safety-critical scenarios)

---

## Contributing Benchmarks

Add a new scenario to `benchmark/compare_baseline.py` following the existing pattern:

```python
{
    "name": "Your scenario name",
    "description": "What this tests and why.",
    "constraints": {"key": "value", ...},
    "actions": [Action(...), ...],
    "expected_cdrs_action": "action_name",
    "expected_baseline_action": "action_name",
}
```

Good domains: medical triage, network routing, financial risk, code deployment, emergency response.

---

## Open Research Questions

See `research/README.md` for the full list. The key benchmark question:

> Does CDRS generalize its constraint-aware improvements to unseen domains, or only to scenarios it was designed around?


---

## Proposed Evaluation Metrics

CDRS benchmarks should measure:

- unsafe action reduction
- reasoning consistency
- constraint adherence
- conflict-resolution quality
- reusable learning retrieval accuracy
- hallucination reduction during planning

Example benchmark scenarios:
- task scheduling
- delivery routing
- coding assistant planning
- multi-constraint prioritization

