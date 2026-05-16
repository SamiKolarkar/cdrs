
# CDRS — Constraint-Driven Reasoning System

CDRS is a local-first constraint-aware reasoning runtime for AI agents.

It combines:
- structured WHY reasoning
- constraint-first decision orchestration
- arbitration-based planning
- reusable memory consolidation
- lightweight retrieval
- local LLM execution

to improve decision reliability using lightweight models such as Phi running through Ollama.

---

## Philosophy

CDRS does not attempt to simulate consciousness or unrestricted AGI.

Instead, it focuses on:

- reliable decision-making
- constraint-aware reasoning
- reusable structured experiences
- operational intelligence for local AI agents

The core idea is:

> Good intelligence is not infinite intelligence.
> Good intelligence is reliable decision-making under constraints.

---

## Current Status

Current implementation status:

- local runtime prototype
- structured WHY engine
- arbitration layer
- memory consolidation
- lightweight retrieval system
- Phi + Ollama compatible
- experimental architecture
- not production-ready

---

## Runtime Flow

```text
Context
→ WHY generation
→ Constraint weighting
→ Arbitration
→ Decision
→ Action
→ Evaluation
→ Memory storage
→ Pattern consolidation
→ Retrieval reuse
```

---

## Key Features

- Constraint-first reasoning
- Structured WHY representation
- Multi-domain reasoning runtime
- Local-first architecture
- Lightweight memory system
- Experience consolidation
- Retrieval-driven reuse
- Runtime-oriented agent orchestration

---

## Structured WHY Representation

CDRS treats WHY as machine-usable runtime structure rather than free-form explanation.

Example:

```json
{
  "objective": "meet the deadline safely",
  "constraints": [
    {
      "name": "time_critical",
      "priority": 10
    }
  ],
  "risk_score": 0.28,
  "confidence": 0.81
}
```

This structure allows:
- arbitration
- retrieval
- reusable memory
- deterministic reasoning
- confidence scoring

---

## Example Runtime Output

### Driving Decision Example

```text
Decision: CONDITIONAL YES
Action: overtake
Confidence: 0.72

WHY:
Overtaking advances progress toward the goal while visibility and safety remain acceptable.

Risk Conditions:
- blind turns
- high traffic
- low visibility
```

### Task Scheduling Example

```text
Decision: YES
Action: defer_low_priority
Confidence: 0.75

WHY:
Deferring non-critical tasks preserves system stability while meeting time-critical objectives.
```

---

## Current Limitations

CDRS currently does NOT provide:

- unrestricted AGI
- autonomous scientific reasoning
- full causal world modeling
- true self-directed intelligence
- advanced semantic retrieval
- distributed multi-agent coordination

The current system should be understood as:

- an experimental reasoning runtime
- a structured decision architecture
- a local-first intelligent agent framework

rather than a complete general intelligence system.

---

## Running Locally

### Create virtual environment

```bash
python3 -m venv .venv
source .venv/bin/activate
```

### Install dependencies

```bash
pip install -r requirements.txt
```

### Start Ollama

```bash
ollama serve
```

### Pull Phi model

```bash
ollama pull phi3
```

### Run prototype

```bash
python3 -m prototype.main
```

---

## License

MIT License
