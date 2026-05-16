# Contributing to CDRS

Thank you for your interest in contributing to the Constraint-Driven Reasoning System.

CDRS is an open research framework — not a finished product. Every contribution, whether a challenge to the theory, a new implementation, or a real-world example, moves the idea forward.

---

## What You Can Contribute

### 1. Architecture Extensions
Improve, challenge, or expand the five pillars.

- Found a gap in WH-question chaining? Propose a fix.
- Better mechanism for importance weighting? Submit it.
- Alternative to constraint-based retrieval? Open a discussion.

Use the **Idea Proposal** issue template.

### 2. Implementations
Build CDRS in any language or framework.

- Python, Java, TypeScript, Rust — all welcome
- LangChain, LlamaIndex, Spring AI, or raw API — all valid
- Partial implementations are accepted

Place implementations in `implementations/<your-name-or-handle>/`.  
Include a `README.md` explaining what you built and what works.

### 3. Research Findings
Evaluate CDRS against existing benchmarks or test it on real tasks.

- Does WH-chaining improve decision quality over direct prompting?
- Does constraint-based retrieval outperform text similarity?
- Where does CDRS fail?

Place findings in `research/`. Negative results are equally valuable.

### 4. Examples and Use Cases
Show CDRS applied to a specific domain.

- Autonomous vehicle decision-making
- Medical triage reasoning
- Financial risk assessment
- Code review agents
- Customer support agents

Place in `examples/<domain>/`.

### 5. Critiques
Open an issue identifying weaknesses, contradictions, or missing pieces in the architecture.  
Good critiques improve the system. They are credited in the changelog.

---

## Contribution Process

1. **Fork** the repository
2. **Create a branch**: `git checkout -b your-contribution-name`
3. **Add your contribution** to the appropriate folder
4. **Open a Pull Request** using the PR template
5. **Discuss** — maintainers and community will review and engage

---

## Standards

- Be specific. Vague contributions are hard to evaluate.
- Cite prior work if your idea builds on existing research.
- Credit the original CDRS concept in derivative works per the Apache 2.0 license.
- Treat all contributors with respect — see `CODE_OF_CONDUCT.md`.

---

## Attribution

All accepted contributions are credited in the repository.  
The original concept remains attributed to **Sami Ahmed Yusuf Kolarkar, 2026**.  
Contributors own their contributions under Apache 2.0.

---

## Questions

Open a GitHub Discussion or an issue labeled `question`.
