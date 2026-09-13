# Decision and unknown protocol

## Two-axis classification

Every material statement used for design must be classified independently along two axes before it is promoted into canonical truth.

### Axis 1 — semantic owner / lifecycle level

Determine what kind of statement it is and therefore which stage owns accepting it:

- **S0 Problem / Outcome** — need, trigger, evidence, desired outcome, problem boundary;
- **S1 Product Requirement** — externally meaningful behavior, constraint or quality expectation;
- **S2 Domain Semantics** — domain meaning, identity, lifecycle, invariant and ownership;
- **S3 Architecture / Design** — realization structure, contracts between technical components, data/acquisition strategy, persistence/API/service/adaptor design;
- **S4 Implementation Readiness / Implementation Choice** — executable implementation detail, concrete code/task decomposition, framework/configuration choice when not already constrained by S3.

An explicit owner decision can make a statement accepted at its proper level. It does not promote an implementation/design statement into a product requirement merely because the user stated it decisively.

When a statement could be expressed at more than one level, preserve the highest-level observable constraint separately from any proposed lower-level realization. Example:

```text
S1 FIXED: downstream consumers must be able to determine freshness of data used in the result.
S3 PROPOSED/FIXED: expose this as metadata.snapshotCollectedAt from one logical acquisition snapshot.
```

Do not collapse those into one S1 requirement unless the concrete representation itself is part of the accepted external product contract.

### Axis 2 — decision status / obligation

Every material statement must also be distinguishable as:

- **accepted/known** — supported by canonical project truth or an explicit owner decision at the correct semantic level;
- **constraint** — mandatory limitation imposed by accepted external/project truth; downstream work must satisfy it but it may not itself be the feature goal;
- **proposal** — a candidate choice suggested for consideration but not yet accepted;
- **hypothesis** — plausible proposition being tested against evidence or consequences;
- **unknown** — evidence/decision is insufficient;
- **conflict** — authoritative sources disagree.

`proposal` and `hypothesis` are both non-authoritative. A proposal is primarily a candidate To-Be choice; a hypothesis is primarily a belief to validate. Neither may be written as accepted truth before the owning stage accepts it.

## Classification rule

For every consequential statement ask, in order:

1. **What semantic question does this statement answer?** Problem, required behavior, domain meaning, architecture/design, or implementation?
2. **How obligatory is it?** Accepted/known, constraint, proposal, hypothesis, unknown or conflict?
3. **Who can accept it?** Identify the stage/owner whose gate may promote it to canonical truth.
4. **What higher-level constraint, if any, is independent of this realization?** Preserve that separately.

User wording such as "давайте сделаем X", "будем читать вместе" or "можно хранить так" does not by itself establish S1 requirement ownership. First classify the semantic level; then determine whether the wording is an accepted choice, proposal or hypothesis at that level.

## No-invention rule

Never represent a proposal, hypothesis or unknown as accepted product/domain truth because it makes implementation convenient.

Never represent a lower-level realization choice as a higher-level requirement merely because it is concrete, easy to test, or explicitly suggested during requirements discovery.

For a material unknown:
1. inspect canonical repository evidence first;
2. determine whether it is factual, semantic or a To-Be choice;
3. resolve it with evidence, focused owner decision or an accepted explicit deferral;
4. keep the relevant gate closed if the unknown is blocking.

A deferral is valid only when it states why the unknown is non-blocking now and what event requires revisiting it.

## Promotion rule

Acceptance is local to semantic ownership:

```text
accepted at S3 != product requirement at S1
accepted at S2 != evidence/problem statement at S0
implementation convenience != accepted architecture
```

When a later-stage accepted choice creates a new externally observable constraint, explicitly `REOPEN` the owning earlier stage rather than silently backfilling the lower-level choice into that earlier artifact.

## Decision record

Consequential target choices belong in the canonical artifact owned by their semantic level or in an ADR when appropriate. Chat transcripts are not canonical decisions.

When recording a mixed discussion, split accepted statements by owner instead of copying the conversation verbatim into one requirements/domain/architecture document.
