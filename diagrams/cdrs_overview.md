# CDRS — Full System Overview (Mermaid)

GitHub-native diagrams. Renders inline on any Markdown viewer.

---

## Complete Decision Cycle

```mermaid
flowchart TD
    INPUT([INPUT SITUATION]) --> L1

    subgraph L1["① Constraint Layer"]
        CE[Extract constraints\nenvironment · limits · priorities · risk]
    end

    L1 --> L2

    subgraph L2["② WH-Chain Layer"]
        WH["WHY → WHAT → WHO → WHEN → WHERE → HOW\nHOW is always last"]
    end

    L2 --> L3

    subgraph L3["③ Pattern Retrieval"]
        PM[Match past constraint configurations\nconstraint-based similarity · not text]
    end

    L3 --> L4

    subgraph L4["④⑤ Action · Outcome · Risk Layers"]
        A[Generate candidate actions]
        B[Predict outcomes per action]
        C[Evaluate risks + failure conditions\nweighted by constraint priority]
        A --> B --> C
    end

    L4 --> L6

    subgraph L6["⑥ WHY Construction Layer"]
        W["WHY = f(outcomes, constraints, risks, goals, timing)\n\nbenefit_why · risk_why · condition_why · failure_why\n→ dynamic summary"]
    end

    L6 --> L7

    subgraph L7["⑦ Decision + Learning Layer"]
        D["Score = outcome_score − risk × safety_weight\n\nVerdict: YES · NO · CONDITIONAL + confidence"]
        E[Execute action]
        F[Observe actual result]
        G[Store experience record]
        H[Consolidate patterns across sessions\nDreaming Layer]
        D --> E --> F --> G --> H
    end

    H -.->|informs future decisions| L3

    style INPUT fill:#1f4e79,color:#fff
    style L1 fill:#0e3d5c,color:#cdd9e5
    style L2 fill:#1a3a5c,color:#cdd9e5
    style L3 fill:#1c2128,color:#cdd9e5
    style L4 fill:#0e3d5c,color:#cdd9e5
    style L6 fill:#1a3a5c,color:#cdd9e5
    style L7 fill:#0e3d5c,color:#cdd9e5
```

---

## WH-Chain Detail

```mermaid
flowchart LR
    G([GOAL]) --> WHY
    WHY["WHY\nUnderlying intent"] --> WHAT
    WHAT["WHAT\nRequired outcomes"] --> WHO
    WHO["WHO\nEntities involved"] --> WHEN
    WHEN["WHEN\nConditions that apply"] --> WHERE
    WHERE["WHERE\nEnvironment context"] --> HOW
    HOW(["HOW\nExecution strategy\nDerived — never assumed"])

    style G fill:#1f4e79,color:#fff
    style HOW fill:#1a6090,color:#fff
```

---

## WHY Composition

```mermaid
flowchart TD
    OUT[Outcomes] --> COMP
    CON[Constraints] --> COMP
    RISK[Risks] --> COMP
    GOAL[Goals] --> COMP
    TIME[Timing] --> COMP

    COMP{WHY\nComposer}

    COMP --> BW[benefit_why\nWhy this action produces value]
    COMP --> RW[risk_why\nWhy this action could fail]
    COMP --> CW[condition_why\nWhen this action is valid]
    COMP --> FW[failure_why\nWhen this action is dangerous]

    BW --> SUM([Dynamic WHY Summary])
    RW --> SUM
    CW --> SUM
    FW --> SUM

    style COMP fill:#1f4e79,color:#fff
    style SUM fill:#1a6090,color:#fff
```

---

## Memory and Learning

```mermaid
flowchart TD
    D[Decision Made] --> ES[ExperienceStore\nSave full record\nconstraints · action · expected outcome\nconfidence · explanation]
    EX[Execution Result] --> ES
    ES --> PS

    PS[PatternStore\nconsolidate — scheduled process\nreview all sessions\nextract recurring patterns]

    PS --> RET[Constraint-Based Retrieval\nfuture decisions informed\nby pattern similarity]

    RET -.->|informs| NEXT([Next Decision Cycle])

    style D fill:#1f4e79,color:#fff
    style PS fill:#1a6090,color:#fff
    style NEXT fill:#1f4e79,color:#fff
```

---

## Verdict Matrix

```mermaid
quadrantChart
    title Decision Verdict by Score and Risk
    x-axis Low Risk --> High Risk
    y-axis Low Score --> High Score
    quadrant-1 YES
    quadrant-2 CONDITIONAL YES
    quadrant-3 NO
    quadrant-4 CONDITIONAL NO
    YES: [0.1, 0.85]
    CONDITIONAL YES: [0.4, 0.65]
    CONDITIONAL NO: [0.6, 0.35]
    NO: [0.85, 0.15]
```
