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

## Stakeholder evidence

Stakeholder/user statements about problems, goals, usage, examples, workarounds, constraints, risks and operating context are **source evidence**. They are valuable even when the speaker has not formulated a requirement correctly and even when the current interpretation later changes.

Source evidence is not itself canonical product/domain truth:

```text
stakeholder statement != accepted requirement
stakeholder example != accepted use case
repeated evidence != automatic acceptance
proposed realization != underlying need
```

When consequential evidence must survive the conversation, preserve a compact evidence atom with enough provenance to reinterpret it later. Prefer:

- source/date or equivalent provenance;
- affected topic/problem area;
- the observed problem/usage statement normalized without changing its meaning;
- a short verbatim fragment only when exact wording is materially useful;
- contradiction/supersession note when known.

Keep interpretation separate. A later analysis may derive journey/use-case candidates, requirement candidates, capability clues or boundary hypotheses from the same evidence without rewriting the original observation.

Do not persist full chat transcripts merely as evidence. Conversation history is disposable execution context; consequential stakeholder evidence extracted from it may be durable.

## Discovery entity classification

The kind of thing discovered in a discussion is separate from both lifecycle ownership and decision status. A material statement may describe, for example, a problem/goal, journey, use case, requirement, capability, Bounded Context candidate or architecture choice.

Do not infer acceptance or ownership from the entity label:

```text
identified use case != accepted requirement
identified capability != separate Bounded Context
Bounded Context candidate != accepted Bounded Context
```

Journeys, use cases and capabilities may be useful evidence for later requirements/domain work while remaining proposals or hypotheses. Preserve them only when consequential enough to survive the conversation, in the smallest existing durable owner appropriate to the active work.

## Classification rule

For every consequential statement ask, in order:

1. **What was actually observed/stated?** Preserve source evidence separately when later reinterpretation may matter.
2. **What semantic question does this statement answer?** Problem, required behavior, domain meaning, architecture/design, or implementation?
3. **What kind of discovery entity is it, when that distinction matters?** For example journey/use case/capability/boundary candidate; do not invent an entity taxonomy when the statement does not need one.
4. **How obligatory is it?** Accepted/known, constraint, proposal, hypothesis, unknown or conflict?
5. **Who can accept it?** Identify the stage/owner whose gate may promote it to canonical truth.
6. **What higher-level constraint, if any, is independent of this realization?** Preserve that separately.

User wording such as "давайте сделаем X", "будем читать вместе" or "можно хранить так" does not by itself establish S1 requirement ownership. First preserve any independent need/evidence, then classify the semantic level and determine whether the suggested choice is accepted, proposed or hypothetical at that level.

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

Discovery entities are not promoted into one another as a lifecycle shortcut. A journey/use case may motivate requirements; a use case may require capabilities; capability clustering may provide evidence for Bounded Context boundaries. Each remains its own concept, and each accepted truth is decided by its owning stage.

When a later-stage accepted choice creates a new externally observable constraint, explicitly `REOPEN` the owning earlier stage rather than silently backfilling the lower-level choice into that earlier artifact.

## Decision record

Consequential target choices belong in the canonical artifact owned by their semantic level or in an ADR when appropriate. Chat transcripts are not canonical decisions.

When recording a mixed discussion, split accepted statements by owner instead of copying the conversation verbatim into one requirements/domain/architecture document. Preserve consequential unresolved discoveries and stakeholder evidence only in the smallest correct durable owner; do not retain conversation dumps or create permanent discovery reports merely for memory.
