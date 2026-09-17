# Strategic DDD convergence

## Purpose

Use this protocol only when S2 Domain Design is routed to Strategic DDD. Converge on coherent semantic ownership, Bounded Context boundaries, relationships and public semantic contracts.

```text
candidate contexts
<-> responsibilities and decisions
<-> context relationships
<-> public semantic contracts
<-> boundary/coupling challenge
```

The current strategic model is authoritative project truth until an S2 change explicitly reopens it. It may be challenged by new accepted requirements/evidence, but existing code/package/database boundaries are not automatic semantic truth.

## Inputs

Load only the affected current scope:

- accepted requirements creating the semantic need;
- affected current domain/context artifacts;
- current context-map relationships;
- concrete consumer/provider semantic needs;
- code/persistence only as secondary evidence when needed to resolve a semantic claim.

Do not preload every context or invent a repository-wide capability inventory for a local boundary question.

## Canonical strategic artifacts

- `docs/domain/strategic-model.md` — current target participants, responsibilities and boundaries.
- `docs/domain/context-map.md` — material strategic relationships and public semantic contracts.
- `docs/domain/strategic-model.json` — machine-readable projection for validation/automation; it does not redefine the Markdown authorities.

Projection mismatch is a consistency finding to resolve against accepted current truth, not permission to choose whichever representation is convenient.

## Boundary discovery

Capabilities, journeys and use cases are evidence, not automatic Bounded Contexts. When ownership is unclear, derive only what the affected behavior needs and group candidate responsibilities by:

- ubiquitous language;
- authoritative decisions/facts;
- identity, lifecycle and invariants;
- authority/responsibility;
- change independence;
- stable public semantic inputs/outputs.

A class, table, API, package, service, screen or deployment unit is not by itself a Bounded Context argument.

## Context responsibility check

For each affected candidate/current context make explicit:

- purpose;
- authoritative semantic responsibility;
- decisions/facts owned;
- key identities;
- lifecycle/invariants;
- language boundary;
- authority boundary where material;
- required semantic inputs;
- public semantic outputs.

Boundary defects include duplicate authority, missing authority, peer-private model dependence, an invariant/lifecycle split across contexts, or a context justified only by technical packaging.

## Relationship contract

For each affected cross-context relationship state only the semantics required by the current change:

- provider/semantic owner and consumer;
- request/input and response/fact/output;
- crossing identities/references;
- temporal semantics when material;
- empty/unknown/failure semantics;
- provenance/authority expectations when material;
- consumer obligations and forbidden reinterpretation.

The contract is semantic before it is HTTP, Python, messaging or storage.

Prefer consumer-owned ports for dependency inversion unless a genuinely provider-published/shared language is intentionally accepted. Do not create a shared business-model package merely to avoid explicit context boundaries.

## Boundary and coupling challenge

For every affected edge ask:

1. Why does the consumer need this meaning?
2. Who has authority to decide/derive it?
3. Can the consumer work from the public contract alone?
4. Is it re-deriving provider decisions from private state?
5. Is the provider exporting more private model than necessary?
6. Are identity/time/unknown/provenance semantics sufficient?
7. Does one semantic operation require N+1 traversal or a distributed join because the published meaning is too fine-grained?
8. Does the consumer require provider availability even though it only needs already-established meaning?
9. Can provider-internal refactoring break consumers without public semantic change?
10. Is an Aggregate/BC being enlarged only to remove technical integration inconvenience?
11. Is a consumer-local projection beginning to make authoritative decisions?
12. Would plausible scale amplify the contract into mandatory per-object coordination or Cartesian work?

Prefer semantic remedies first: narrow or coarsen the published meaning, batch at the semantic contract, keep one authority owner, permit rebuildable consumer projections when they do not gain authority, and reject aggregate enlargement without a local invariant/lifecycle reason.

Do not choose brokers, HTTP, caches, replication, persistence technology or deployment topology in S2 merely to fix an otherwise sufficient semantic contract. Efficient delivery/computation after semantics are sufficient is S3 Architecture work.

## Convergence loop

Run only the affected steps:

1. restate the affected behavior/use cases when needed;
2. derive the smallest responsibility/capability set when boundaries are unclear;
3. form context candidates without accepting them prematurely;
4. state responsibilities and relationships;
5. define the public semantic contracts;
6. challenge boundaries and coupling;
7. classify findings P0-P3 and separate semantic defects from architecture concerns;
8. change ownership/boundaries/contracts where required;
9. repeat only when evidence/model/problem state changed.

Apply the lifecycle no-progress rule instead of re-running the same analysis.

## Strategic convergence gate

The affected strategic scope is converged when:

- every authoritative semantic fact/decision has one coherent owner;
- required context relationships are explicit;
- each affected edge has a sufficient public semantic contract;
- consumers do not require peer-private domain models;
- material identity/time/unknown/provenance semantics are explicit;
- no P0/P1 ownership, boundary, semantic-cycle or semantic-coupling contradiction remains;
- remaining efficiency/delivery concerns are clearly S3 rather than hidden semantic gaps;
- `strategic-model.json` remains consistent with the canonical Markdown strategic artifacts.

## Output

Update only current canonical owners:

- `strategic-model.md` for responsibility/boundary changes;
- `context-map.md` for accepted relationships/contracts;
- the smallest affected context/domain artifact for additional semantic detail;
- `strategic-model.json` to keep the machine projection consistent.

Do not keep rejected alternatives, discovery reports, capability clustering, supersession narratives or decision-history documents after current canonical truth absorbs the result. Git history preserves replaced repository state.

Return to `domain-design-stage.md` for required Tactical DDD and final G2 evaluation.
