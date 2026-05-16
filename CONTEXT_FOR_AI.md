# CONTEXT FOR AI CONTRIBUTORS

**Read this file before making any contribution to CDRS.**

If you are an AI assistant (Claude, GPT, Gemini, or any other) helping a contributor extend, implement, or evaluate CDRS — this document gives you the complete project context needed to contribute correctly.

---

## What CDRS Is

CDRS (Constraint-Driven Reasoning System) is an experimental open-source AI decision framework built around **practical operational intelligence** — not AGI, not consciousness, not philosophical reasoning.

The single governing philosophy:

> "Good intelligence is reliable decision-making under constraints."

---

## What CDRS Is Not

Do not frame contributions around:
- AGI capability claims
- Consciousness simulation
- Universal truth generation
- Infinite recursive reasoning
- Philosophical completeness

These are explicitly rejected by the project. Any contribution that drifts toward these should be redirected toward practical decision quality.

---

## The Architecture in One Paragraph

CDRS structures agent decision-making through seven layers: (1) constraint extraction before any reasoning begins, (2) WH-question chaining (WHY → WHAT → WHO → WHEN → WHERE → HOW, with HOW always last), (3) action candidate generation, (4) outcome prediction, (5) risk evaluation with importance weighting, (6) dynamic WHY composition from multiple factors, and (7) decision output + experience storage + cross-session pattern consolidation. WHY is never stored as a fixed answer — it is always constructed from components specific to the current situation.

---

## The Ten Design Principles

1. Decision quality matters more than explanation depth
2. Constraints define reasoning validity — extract before anything else
3. WHY is dynamically constructed, never stored as a fixed answer
4. Multiple WHY chains must be balanced (benefit, risk, condition, failure)
5. Risks must be explicitly modeled and weighted
6. Learning requires feedback — close every decision loop
7. Context must persist across sessions via pattern consolidation
8. Operational usefulness is preferred over philosophical completeness
9. Explanations are context-dependent — never universal
10. HOW is always the output of reasoning, never the starting point

---

## The WH-Chain (Critical)

This is the primary architectural differentiator of CDRS from standard agent frameworks.

```
WHY   → What is the underlying intent?
WHAT  → What is needed to fulfill it?
WHO   → What entities or resources are involved?
WHEN  → Under what conditions does this apply?
WHERE → In what environment?
HOW   → Execution strategy — derived from all above, always last
```

When extending CDRS, always ensure HOW is derived, not assumed.

---

## WHY Construction Formula

```
WHY = f(outcomes, constraints, risks, goals, timing)
```

WHY has four components that must all be evaluated:
- `benefit_why` — why this action produces value
- `risk_why` — why this action could fail
- `condition_why` — when this action is valid
- `failure_why` — when this action becomes dangerous

A response that only evaluates one WHY type is incomplete.

---

## Stopping Conditions

Recursive WHY decomposition must halt. Stop when:
- Explanation is sufficient for reliable action
- Deeper explanation adds no practical value

*Do not generate infinitely deep explanations. Useful understanding > infinite understanding.*

---

## Decision Output Format

All decisions must include:
- Verdict: `yes` / `no` / `conditional_yes` / `conditional_no`
- Confidence: 0.0–1.0
- Explanation: dynamic WHY summary
- Conditions: what must hold for the verdict to remain valid

Binary yes/no without confidence or conditions is insufficient.

---

## What Is an Open Problem (Good Contribution Targets)

1. **Constraint similarity metric** — Jaccard (v0.1) is a placeholder; weighted or embedding-based similarity is needed
2. **WHY composition quality** — template-based (v0.1) is rigid; LLM composition with component injection is the target
3. **Stopping depth for recursive WHY** — currently implicit; needs a programmatic usefulness threshold
4. **Weight learning** — importance weights are static; they should be learned from outcome history
5. **Cross-agent pattern sharing** — can patterns from one agent instance safely inform another?

---

## What Makes a Good Contribution

- Targets one of the five open problems above
- Improves decision quality measurably (provide before/after comparison)
- Keeps implementations modular and testable
- Does not add philosophical abstraction without implementation
- Credits original concept: Sami Ahmed Yusuf Kolarkar, 2026

---

## What Makes a Bad Contribution

- Claims AGI or consciousness properties
- Adds explanation depth without improving decision quality
- Breaks the constraint-first ordering
- Makes HOW a starting point instead of a derived output
- Stores WHY as a fixed answer

---

## Project Files to Read First

Before contributing to any specific component:

1. `docs/origin.md` — why every design decision exists
2. `docs/architecture.md` — 7-layer technical deep-dive
3. `docs/philosophy.md` — the reasoning behind design choices
4. `prototype/engine/decision_engine.py` — the orchestration layer
5. `prototype/engine/wh_chain.py` — the differentiating component

---

## Attribution

Every contribution must include:

> "Original CDRS concept: Sami Ahmed Yusuf Kolarkar, 2026. Apache License 2.0."

Your contribution is your own — but the foundation it builds on must be credited.

---

*This file exists because AI tools are legitimate contributors to open-source projects.  
Read it. Follow it. Build something useful.*
