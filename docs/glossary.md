# CDRS Glossary

---

**Constraint**  
An environmental condition, limit, or priority that bounds the decision space. Constraints are always extracted before any reasoning begins. Examples: `traffic=high`, `visibility=good`, `time_critical=yes`.

**Constraint Configuration**  
The full set of constraints active for a given decision cycle. Two decisions with similar constraint configurations are candidates for pattern matching.

**WHY (dynamic)**  
An explanation constructed from outcomes, constraints, risks, goals, and timing — for a specific situation. WHY is never stored as a fixed answer.

**WH-Chain**  
The structured interrogation sequence: WHY → WHAT → WHO → WHEN → WHERE → HOW. HOW is always last.

**Benefit WHY**  
The component of WHY that explains why an action produces value under current constraints.

**Risk WHY**  
The component of WHY that explains why an action could fail or cause harm.

**Condition WHY**  
The component of WHY that identifies when an action is valid to execute.

**Failure WHY**  
The component of WHY that identifies when an action becomes invalid or dangerous.

**Importance Weight**  
A numeric value that scales the influence of a constraint priority on scoring. High-priority constraints amplify risk penalties.

**Decision Verdict**  
The output classification: `yes`, `no`, `conditional_yes`, or `conditional_no`. Always accompanied by a confidence score.

**Experience Record**  
A stored decision cycle: constraint configuration + action + expected outcome + actual outcome + explanation + confidence. The raw material for pattern consolidation.

**Pattern**  
A consolidated insight extracted from multiple experience records with similar constraint configurations. Represents: which actions succeed under which constraints.

**Pattern Consolidation (Dreaming Layer)**  
The scheduled process that reviews experience records across sessions, extracts recurring patterns, and stores them for future retrieval. Analogous to sleep-based memory consolidation in humans.

**Constraint-Based Retrieval**  
Matching past experiences or patterns by constraint configuration similarity — not by text similarity. A key architectural distinction of CDRS.

**Stopping Condition**  
The rule that halts recursive WHY decomposition when further depth produces no actionable value.

**Confidence Score**  
A value in [0.0, 1.0] estimating the reliability of a decision given current evidence, risk level, and historical pattern support.
