# Decision and unknown protocol

## Two-axis classification

Every material statement used for design must be classified independently along two axes before it is promoted into current project truth.

### Axis 1 — semantic owner / lifecycle level

Determine what kind of statement it is and therefore which stage owns accepting it:

- **S0 Problem / Outcome** — need, trigger, evidence, desired outcome, problem boundary;
- **S1 Product Requirement** — externally meaningful behavior, constraint or quality expectation;
- **S2 Domain Semantics** — domain meaning, identity, lifecycle, invariant and ownership;
- **S3 Architecture / Design** — realization structure, contracts between technical components, data/acquisition strategy, persistence/API/service/adapter design;
- **S4 Implementation Readiness / Implementation Choice** — executable implementation detail, concrete code/task decomposition, framework/configuration choice when not already constrained by S3.

An explicit owner decision can make a statement accepted at its proper level. It does not promote an implementation/design statement into a product requirement merely because the user stated it decisively.

When a statement can be expressed at more than one level, preserve the highest-level observable constraint separately from any lower-level realization. Do not freeze a concrete representation into an earlier lifecycle layer unless that representation is itself part of the accepted contract.

### Axis 2 — decision status / obligation

Every material statement must also be distinguishable as:

- **accepted/known** — supported by current project truth or an explicit owner decision at the correct semantic level;
- **constraint** — mandatory limitation imposed by accepted external/project truth;
- **proposal** — candidate target choice not yet accepted;
- **hypothesis** — proposition being tested against evidence or consequences;
- **unknown** — evidence or decision is insufficient;
- **conflict** — authoritative current sources disagree.

`proposal` and `hypothesis` are non-authoritative and must not be written as accepted truth before the owning stage accepts them.

## Stakeholder evidence

Stakeholder statements about problems, goals, usage, examples, workarounds, constraints, risks and operating context are source evidence. They are not automatically accepted requirements or domain truth.

When consequential evidence must survive the conversation, preserve only the minimum evidence needed by the current owner to interpret or decide the active question. Do not create transcript archives or discovery-history documents.

## Discovery entity classification

The kind of thing discovered is separate from lifecycle ownership and decision status. A journey, use case, capability or Bounded Context candidate does not become accepted merely because it has been identified.

Preserve a discovery only when it is consequential to current work and in the smallest existing owner that needs it. Do not create permanent discovery catalogs by default.

## Classification rule

For every consequential statement ask:

1. What was actually observed or stated?
2. What semantic question does it answer: problem, required behavior, domain meaning, architecture/design, or implementation?
3. What kind of discovery entity is it, when that distinction matters?
4. Is it accepted, a constraint, proposal, hypothesis, unknown or conflict?
5. Which lifecycle stage owns acceptance?
6. What higher-level constraint, if any, is independent of the proposed realization?

## No-invention rule

Never represent a proposal, hypothesis or unknown as accepted product/domain truth because it makes implementation convenient.

For a material unknown:
1. inspect current canonical repository evidence first;
2. determine whether it is factual, semantic or a target choice;
3. resolve it with evidence or a focused owner decision;
4. keep the relevant gate closed while a blocking unknown remains.

If a question is intentionally outside the current scope, state the present boundary in the owning artifact rather than keeping a future-work history entry.

## Promotion rule

Acceptance is local to semantic ownership:

```text
accepted at S3 != product requirement at S1
accepted at S2 != evidence/problem statement at S0
implementation convenience != accepted architecture
```

When a later-stage choice creates a new externally observable constraint, explicitly `REOPEN` the owning earlier stage rather than silently backfilling the lower-level choice into that artifact.

## Recording accepted decisions

Record accepted normative consequences in the artifact owned by their semantic level:

- requirements for observable behavior and quality constraints;
- domain for meaning, identity, lifecycle, invariants and semantic ownership;
- architecture for realization structure and dependency/data boundaries;
- engineering for API, persistence, runtime and operational contracts.

Use an ADR under `docs/decisions/` when the **decision itself** is required project knowledge: a consequential choice among alternatives whose rationale, trade-offs, compatibility consequences or revisit conditions are needed to reconstruct or safely evolve the current as-built/target design. Such an ADR is current design documentation, not a decision-history archive.

An ADR may remain after implementation. Remove it only when it no longer constrains or explains any current as-built or target design and its still-required normative consequences are fully represented elsewhere.

Do not retain supersession chains or obsolete alternatives solely for history. Git history remains the archive for replaced decisions and repository state. Chat transcripts are not canonical project truth.
