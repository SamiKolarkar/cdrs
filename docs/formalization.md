# CDRS Formalization Notes

## Purpose

This document defines the machine-usable structures required to move CDRS from conceptual architecture to reproducible implementation.

---

## WHY Representation

```json
{
  "objective": "complete task safely",
  "constraints": [
    {
      "name": "time",
      "priority": 7
    }
  ],
  "risk_score": 0.2,
  "confidence": 0.85
}
```

---

## Core Runtime Loop

```text
Context
→ WHY extraction
→ Constraint weighting
→ Planner
→ Action generation
→ Evaluation
→ Memory consolidation
```

---

## Memory Consolidation Goals

Store:
- objective
- constraints
- selected action
- outcome
- risk profile
- confidence score

Avoid storing:
- raw chat logs only
- unstructured reasoning dumps
- isolated actions without context

---

## Long-Term Goal

CDRS aims to become a reusable reasoning runtime for constraint-aware AI agents rather than a claim of unrestricted AGI.
