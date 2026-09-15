# Active execution

Current: `access-governance-mvp.md`
Goal: resolve the smallest Access Governance behavior needed to continue the MVP happy path from ACC/RC/AD into bilateral authorization and Access Policy handoff.
Current task: resolve S1 Q2 — the consequence for an existing authorization when placement/scope changes alter approval obligations.
Lifecycle stage: `S1`
Stage state: `IN_PROGRESS`
Lifecycle basis: `docs/requirements/access-governance-g1.md`, `docs/plans/active/access-governance-mvp.md`, and the accepted 2026-09-15 Q1 deployment-pair selection decision.
Implementation authorization: `none`
Authorized scope: `none`
Authorization basis: `none`

## MVP execution rule

Build the smallest working end-to-end happy path, not a feature-complete domain model. Define only semantics required by that path; preserve stable context boundaries, identities and public contracts; defer revisions, richer lifecycle/state machines, migration machinery, optimization and edge-case semantics until concrete pressure appears. Prefer a thin vertical path across contexts over completing each context in depth first.

Current progression: accepted `ACC + RC -> AD` foundation, then minimal Access Governance behavior, then only the downstream network/policy semantics required to produce one working rule.

## Working set

Read first:

- `docs/requirements/access-governance-g1.md`
- `docs/plans/active/access-governance-mvp.md`
- `docs/domain/access-governance/target-tactical-model.md`
- `docs/domain/application-deployment/boundary.md`
- `docs/domain/resource-catalogue/tactical-model.md`

Expand only if a concrete contradiction or missing requirement requires it.

## Current baseline

```text
ACC Interaction / Component
        |
        v
AD ApplicationDeployment / ComponentPlacement -> ResourceRef
        |
        v
RC Resource / ResourceScopeAffiliation / CurrentResourceRealization
        |
        v
AG governed deployment pair + bilateral approval obligations
```

The ACC/RC/AD foundation is coherent for the MVP: RC uses Resource-level `AddressSpace = HostAddress | Prefix` with historical `ResourceAddressFact`; AD references only `ResourceRef`; no endpoint/interface/VIP binding is introduced.

Accepted AG Q1: a source/destination ApplicationDeployment pair is selectable for a declared Interaction when each deployment can realize the corresponding endpoint Component and the current placements needed to determine approval obligations are resolvable.

Preserved AG behavior: source and destination approval obligations are independent; grant requires both required sides; either side may later withdraw its consent; Authority Management owns actor/action/scope authority; Access Policy consumes grant/withdrawal.

## Blockers

S1 still requires owner decisions for:

1. authorization consequence when placement/scope changes alter approval obligations;
2. overlapping Responsibility Scopes on one side.

Q2 is current. Q3 should be resolved only if overlap is required by the first happy path; otherwise it may be explicitly deferred as non-blocking.

## Gate

G1 remains open for the affected Access Governance behavior. Tactical AG revalidation must not freeze obligation cardinality or state transitions before Q2 is accepted and Q3 is accepted or explicitly deferred.

No implementation authorization exists.

## Next

Resolve Q2 with the smallest behavior that prevents an authorization from remaining silently effective under materially changed approval obligations. Then resolve or explicitly defer Q3 for the MVP happy path.
