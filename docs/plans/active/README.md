# Active execution

Current: `access-governance-mvp.md`
Goal: resolve the smallest Access Governance behavior needed to continue the MVP happy path from ACC/RC/AD into bilateral authorization and Access Policy handoff.
Current task: resolve S1 Q3 — overlapping Responsibility Scopes on one governance side.
Lifecycle stage: `S1`
Stage state: `IN_PROGRESS`
Lifecycle basis: `docs/requirements/access-governance-g1.md`, `docs/plans/active/access-governance-mvp.md`, and the accepted 2026-09-15 Q1/Q2 Access Governance decisions.
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
- `docs/domain/resource-catalogue/tactical-model.md`
- `docs/domain/resource-role-model.md`

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

Accepted AG Q1: a source/destination ApplicationDeployment pair is selectable for a declared Interaction when each deployment can realize the corresponding endpoint Component and the current placements needed to determine approval obligations are resolvable.

Accepted AG Q2: placement/scope changes that leave obligations materially unchanged preserve current authorization; a material obligation change makes current authorization cease to be effective, produces `AuthorizationWithdrawn`, and requires the current obligations to be satisfied before a new `AuthorizationGranted`.

RC allows different Responsibility Scope affiliations to be simultaneously effective for one Resource, but no accepted hierarchy or precedence exists between such scopes.

## Blockers

Only Q3 remains for this S1 checkpoint: what to do when more than one distinct Responsibility Scope is simultaneously applicable to one source or destination governance side.

The current MVP candidate is fail-closed: support exactly one distinct applicable Responsibility Scope per side; if several are applicable, treat approval obligations as unresolved and the pair as not selectable/authorizable. This candidate is non-authoritative until accepted.

## Gate

G1 remains open only on Q3 for the affected Access Governance MVP scope. Tactical AG must not invent overlap cardinality or precedence before Q3 is accepted or explicitly deferred.

No implementation authorization exists.

## Next

Resolve Q3. If the fail-closed single-scope MVP boundary is accepted, close the affected G1 checkpoint and revalidate the minimal Access Governance Tactical model against Q1/Q2/Q3.
