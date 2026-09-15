# Active execution

Current: `access-governance-mvp.md`
Goal: resolve the smallest Access Governance behavior needed to continue the MVP happy path from ACC/RC/AD into bilateral authorization and Access Policy handoff.
Current task: resolve S1 Q1 — the minimal rule for selectable source/destination ApplicationDeployment pairs for an Access Request.
Lifecycle stage: `S1`
Stage state: `IN_PROGRESS`
Lifecycle basis: `docs/requirements/access-governance-g1.md`, `docs/plans/active/access-governance-mvp.md`, and the completed 2026-09-15 ACC/RC/AD MVP foundation checkpoint.
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

The ACC/RC/AD foundation is coherent for the MVP: RC now uses Resource-level `AddressSpace = HostAddress | Prefix` with historical `ResourceAddressFact`; AD references only `ResourceRef`; no endpoint/interface/VIP binding is introduced.

Preserved AG behavior: source and destination approval obligations are independent; grant requires both required sides; either side may later withdraw its consent; Authority Management owns actor/action/scope authority; Access Policy consumes grant/withdrawal.

## Blockers

S1 still requires owner decisions for:

1. selectable source/destination ApplicationDeployment pairs;
2. authorization consequence when placement/scope changes alter approval obligations;
3. overlapping Responsibility Scopes on one side.

Q1 is current. A minimal candidate is recorded in the active plan but is non-authoritative until accepted.

## Gate

G1 remains open for the affected Access Governance behavior. Tactical AG revalidation must not freeze obligation cardinality or state transitions before the S1 questions are accepted or explicitly deferred as non-blocking.

No implementation authorization exists.

## Next

Resolve Q1 with the smallest accepted selection rule sufficient for the MVP happy path, then resolve Q2. Treat Q3 only to the extent the first happy path actually encounters overlapping Responsibility Scopes.
