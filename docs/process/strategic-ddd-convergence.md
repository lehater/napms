# Strategic DDD convergence

## Purpose

Use this protocol only when S2 Domain Design has been routed to Strategic DDD.

Its purpose is to converge on coherent semantic ownership and context boundaries by iterating between:

```text
candidate contexts
<-> responsibilities/decisions
<-> context relationships
<-> semantic contracts
<-> boundary challenge
```

The current strategic model is a starting hypothesis to validate, not proof that existing Bounded Context boundaries are correct.

## Inputs

Load only the affected strategic scope:

- accepted requirements that create the semantic need;
- affected context/domain artifacts;
- current context-map/relationship statements when they exist;
- accepted ADRs constraining ownership/boundaries;
- concrete cross-context consumer/provider needs;
- consequential candidate journeys/use cases/capability clues already preserved by upstream work when they materially illuminate the boundary question;
- code/persistence only as secondary evidence when a semantic claim cannot otherwise be resolved.

Do not preload every bounded context, every known journey/use case, or a global capability inventory merely because Strategic DDD is active. Widen the working set only when the current boundary question demonstrates the need.

### Canonical strategic artifact authority

When the repository has a converged strategic baseline, treat its representations according to their declared authority rather than as competing sources:

- `docs/domain/strategic-model.md` is authoritative for current target participants, semantic responsibilities and context boundaries;
- `docs/domain/context-map.md` is authoritative for material strategic relationships and public semantic contracts;
- `docs/domain/strategic-model.json` is the machine-readable projection used for consistency checks and automation, not an independent source allowed to redefine the Markdown authorities.

The machine-readable projection should carry stable participant identifiers and every material relationship needed to compare it with the canonical Context Map. A mismatch is a consistency finding to resolve against accepted requirements/ADRs and the canonical owners; it is not permission to silently change domain truth.

Git history is the archive. Repository documentation is the current working knowledge base. Superseded specifications should not remain normal retrieval inputs unless they carry migration-relevant current-state information or durable decision rationale that is not represented by current canonical artifacts.

A repository/code-search hit is not current truth merely because the search backend returns it. Before using a found document as semantic evidence, verify that the path exists at the task's current target ref (normally current `main`) and classify it as canonical/current, migration/current-state, or superseded rationale. Search results tied only to an older commit SHA are historical evidence.

## Capability and boundary discovery

Capabilities are useful evidence for Strategic DDD, not automatic Bounded Contexts. When ownership/boundaries are genuinely unclear, derive only the capabilities needed by the affected use cases and look for semantic cohesion around:

- ubiquitous language;
- authoritative decisions/facts;
- invariants and lifecycle;
- authority/responsibility;
- change independence;
- stable semantic inputs/outputs that could form a boundary seam.

Treat a capability cluster as a **Bounded Context candidate** until boundary analysis establishes coherent semantic ownership. Do not infer a context from a screen, journey step, application use case, class, package, service, table or deployment unit alone.

A journey may cross several Bounded Contexts. One use case may require several capabilities. One capability may support several use cases. Preserve those relationships only as far as they materially explain the current boundary; do not create a permanent traceability graph by default.

## Context responsibility check

For every affected candidate context, make these explicit enough to challenge:

- purpose;
- authoritative semantic responsibility;
- decisions/facts it owns;
- key identities;
- lifecycle/invariants that justify autonomy;
- language boundary;
- authority/responsibility boundary where material;
- required inputs from other contexts;
- public outputs/semantic facts supplied to others.

Signals of a bad boundary:

- two contexts claim authoritative ownership of the same decision/fact;
- no context owns a required decision/fact;
- one context must understand peer-private entities/state transitions to perform its responsibility;
- contexts cannot change independently because one semantic lifecycle/invariant is artificially split;
- a context exists only because of a table/service/deployment/package boundary.

## Relationship and contract check

For every relationship material to the current change, state:

- purpose of the relationship;
- provider / semantic owner;
- consumer;
- semantic request/input when applicable;
- semantic response/fact/output;
- identity references crossing the boundary;
- temporal semantics (`current`, `asOf`, validity interval, snapshot) where material;
- unknown/absence/error semantics where material;
- provenance/authority expectations where material;
- consumer obligations and forbidden reinterpretation.

The contract is semantic before it is a Python/HTTP/message interface.

Prefer consumer-owned ports for local dependency inversion unless a genuinely shared/provider-published language has been intentionally accepted. Do not create a generic shared business-model package merely to avoid explicit boundaries.

## Boundary challenge

For each affected edge ask:

1. Why does the consumer need this fact?
2. Who has authority to decide/derive it?
3. Can the consumer fulfil its responsibility from the public semantic contract alone?
4. Is the consumer re-deriving an upstream decision from raw upstream internals?
5. Is the provider exporting more internal model than the consumer actually needs?
6. Would moving this responsibility change identity/lifecycle/invariant ownership more coherently?
7. Do time/unknown/provenance semantics make the apparent contract ambiguous?
8. Does a reusable semantic result serve materially different downstream goals, suggesting a stable seam, or is it only an internal intermediate with no independent semantic ownership?

If the smallest stable contract still requires peer-private model knowledge, challenge the context boundary before expanding the DTO/API.

### Cross-context coupling challenge

For every affected cross-context edge whose contract is created, changed or materially exercised by the current Tactical work, challenge coupling as a second lens. Do not run a repository-wide coupling audit merely because one edge changed.

Ask:

1. **Model leakage** — must the consumer understand provider-private entities, aggregates, lifecycle or storage shape to perform its responsibility?
2. **Interaction/chatiness** — does one semantic operation require object-by-object traversal, N+1 cross-context lookups or a large distributed join rather than one sufficiently complete published meaning?
3. **Temporal coupling** — must provider and consumer be simultaneously available even though the consumer only needs an already-established semantic fact?
4. **Change coupling** — can an internal provider-model refactor force consumer change without any change to the public semantic meaning?
5. **Consistency-boundary abuse** — are an Aggregate or Bounded Context being enlarged merely to remove integration inconvenience rather than to protect a local invariant/lifecycle?
6. **Semantic duplication** — does a consumer-owned copy/projection begin to make authoritative decisions that belong to the provider?
7. **Scale amplification** — under a plausible x100/x1000 object count, does the contract turn a normal use case into per-object coordination, Cartesian expansion or mandatory full hydration?

Prefer semantic remedies before architecture remedies:

- private-model leakage -> narrow the Published Language or consumer-owned semantic port;
- chatiness caused by an under-specified semantic contract -> publish a coarser complete semantic result or batch-shaped semantic contract;
- temporal coupling where the meaning is already established -> permit a derived/local consumer projection while preserving one semantic owner;
- change coupling -> stabilize the Published Language or use an anti-corruption translation boundary;
- large distributed joins -> allow derived/materialized consumer projections when they do not acquire independent authority;
- Aggregate enlargement -> reject unless a local invariant, lifecycle or atomic consistency requirement justifies it;
- duplicated authority -> retain one semantic owner and classify downstream copies as derived/rebuildable state.

Do not choose HTTP, messaging, brokers, caches, database replication, persistence technology or deployment topology in S2 merely to answer this challenge. A coupling finding is Strategic when it exposes insufficient public meaning, peer-private model dependence, duplicated authority or a wrong boundary. If the semantic contract is sufficient and only efficient delivery/computation remains unresolved, record an Architecture concern for S3 rather than blocking Strategic convergence.

Chatiness, temporal coupling or scale cost alone is therefore not automatically a P1 domain finding. Classify it P0/P1 only when the cause is a semantic boundary/contract defect that would force downstream invention or peer-private knowledge.

## Convergence loop

Run only the affected portion of this loop:

1. establish/restate the materially affected journeys/use cases only when needed to expose distinct goals;
2. derive the smallest capability set needed by those goals when the boundary is unclear;
3. cluster capabilities by semantic language/ownership/lifecycle and form context candidates without accepting them yet;
4. establish/restate candidate context responsibilities;
5. map affected relationships;
6. describe the semantic contract for each affected edge;
7. boundary-challenge and coupling-challenge each affected contract as applicable;
8. classify contradictions/gaps P0-P3 and separate semantic defects from S3 delivery/computation concerns;
9. change context boundary/ownership/relationship when required;
10. rebuild only contracts/capability grouping affected by that change;
11. repeat until no P0/P1 finding requires another boundary/ownership/contract change.

Skip steps 1-3 when accepted context boundaries are already clear for the current semantic question. A later iteration must change evidence, model, problem state or decision state. Otherwise apply the lifecycle no-progress rule and block/escalate rather than looping.

## Strategic convergence gate

Strategic work is converged for the affected scope when:

- authoritative semantic responsibilities have one coherent owner;
- capability grouping used as boundary evidence is consistent with language/ownership/lifecycle, where capability discovery was needed;
- all relationships needed by the current change are explicit;
- each such relationship has a sufficient semantic contract;
- consumers do not require peer-private domain models to perform their responsibility;
- no unresolved P0/P1 ownership/boundary/semantic-cycle or semantic-coupling contradiction remains;
- relevant identity/time/unknown/provenance semantics are explicit where omission would force downstream invention;
- material coupling findings have either a semantic remedy in S2 or are explicitly classified as S3 delivery/computation concerns;
- one full boundary/coupling challenge pass over the affected edges produces no new P0/P1 requiring a strategic-model change.

P2/P3 findings may remain when they do not undermine these guarantees.

For a repository-wide strategic baseline that also maintains a machine-readable projection, convergence hardening additionally requires that participant identities and material relationship edges can be reconciled between the projection and the canonical Markdown artifacts. Projection drift is documentation/tooling debt unless it exposes a real semantic contradiction; it does not by itself reopen Strategic DDD.

## Output

Promote accepted results to the smallest canonical owners:

- strategic model/context documentation for responsibility/boundary changes;
- context-map/relationship documentation for accepted edges;
- semantic contract documentation near the owner/consumer as appropriate;
- ADR only for consequential decisions that need durable rationale;
- context problem register for unresolved parked context-local issues.

Do not create a permanent capability-clustering analysis, journey map, discovery report or preserve rejected alternatives unless they carry durable decision rationale. Once accepted boundaries/contracts absorb the useful result, discard the exploratory grouping.

After strategic convergence, return to `domain-design-stage.md` for any required Tactical DDD and final G2 evaluation.
