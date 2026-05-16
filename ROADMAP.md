# CDRS Roadmap

---

## v0.1 — Foundation ✅ (Current)
*Establish the concept, open the community, working prototype.*

- [x] Publish original concept paper
- [x] Open-source the repository (Apache 2.0)
- [x] Working Python prototype: all 7 layers implemented
- [x] Constraint extraction, WH-chain, WHY construction, evaluator
- [x] Experience store (JSON-backed cross-session memory)
- [x] Pattern store (consolidation layer)
- [x] Two example domains: driving, task scheduling
- [ ] First community implementation (any language)
- [ ] First external research evaluation

---

## v0.2 — Weighted Decisions + Confidence Refinement
*Improve decision quality. Make weights learnable.*

- [ ] Weighted similarity metric for constraint matching (respects priority)
- [ ] Confidence calibration against past accuracy
- [ ] Feedback-adjusted importance weights (learn from outcomes)
- [ ] WHY constructor improvements: richer language generation
- [ ] Add third example domain (medical triage or code review)
- [ ] Unit test suite for all engine components

---

## v0.3 — Similarity-Based Pattern Retrieval
*Reuse past decisions reliably.*

- [ ] Embedding-based constraint vectors (alternative to Jaccard)
- [ ] Pattern-informed decision bias: past success steers current choice
- [ ] Confidence decay: old patterns weighted less than recent ones
- [ ] PatternStore consolidation scheduling (time-based trigger)
- [ ] Pattern conflict detection: contradictory past outcomes flagged

---

## v0.4 — Adaptive Explanation Generation
*Generate WHY explanations that improve with data.*

- [ ] Template evolution: explanations adapt as patterns accumulate
- [ ] Probabilistic outcome estimation from historical data
- [ ] WH-chain refinement: domain-specific resolvers
- [ ] Multi-agent support: shared pattern stores across agent instances

---

## v1.0 — Modular Decision Engine
*Production-quality, domain-pluggable architecture.*

- [ ] Plugin system: domain-specific constraint extractors and action generators
- [ ] Full learning + refinement pipeline
- [ ] LLM integration layer (optional, non-critical)
- [ ] REST API wrapper for external agent integration
- [ ] Benchmark evaluation: CDRS vs ReAct vs CoT on standardized tasks
- [ ] Formal evaluation paper published

---

## Long-Term Research Track

CDRS hypothesizes that structured goal interrogation (WH-chaining), constraint-aware reasoning, and cross-session pattern consolidation are **necessary conditions** for general reasoning in agents.

The research track aims to:
- Define CDRS-specific evaluation metrics
- Test generalization across domains
- Publish findings — positive and negative — openly

---

*Last updated: May 2026*  
*Original concept: Sami Ahmed Yusuf Kolarkar*
