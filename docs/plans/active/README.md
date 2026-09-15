# Active execution

Current: `application-deployment-boundary.md`
Goal: converge the smallest ACC + RC -> AD foundation needed for the MVP happy path without speculative extensions.
Current task: checkpoint the minimal ACC model and hand off to minimal Resource Catalogue Tactical modelling.
Lifecycle stage: `S2`
Stage state: `IN_PROGRESS`
Lifecycle basis: `docs/plans/active/application-deployment-boundary.md` and the accepted 2026-09-15 MVP happy-path decision.
Implementation authorization: `none`
Authorized scope: `none`
Authorization basis: `none`

## MVP execution rule

Build the smallest working end-to-end happy path, not a feature-complete domain model. Define only semantics required by that path; preserve stable context boundaries, identities and public contracts; defer revisions, richer lifecycle/state machines, migration machinery, optimization and edge-case semantics until concrete pressure appears. Prefer a thin vertical path across contexts over completing each context in depth first.

Current progression: minimal `ACC + RC -> AD`, then the smallest downstream governance/network/policy path needed to produce a working rule.

## Working set

Read first:

- `docs/domain/application-communication-catalogue/target-model.md`
- `docs/plans/active/application-deployment-boundary.md`
- `docs/domain/context-map.md`

Expand only if a concrete contradiction or missing requirement requires it.

## Current baseline

```text
ACC Application / Component / Interaction
        |
        v
AD ApplicationDeployment / ComponentPlacement -> ResourceRef
        |
        v
RC Resource -> effective AddressSpace [0..1] = HostAddress | Prefix
```

ACC MVP checkpoint: Interaction is a stable directed communication template between Components of one Application Definition; self-interaction is allowed; one directed Component pair has at most one Interaction; reverse direction is distinct; endpoints are immutable; traffic is current Interaction state; dedicated InteractionContractRevision is deferred beyond MVP. ACC owns neither placements nor Resources nor concrete deployment pairs.

## Blockers

None for the foundational ACC checkpoint or the next minimal RC Tactical step.

Access Governance retains S1 questions around selectable ApplicationDeployment pairs, authorization behavior after placement/scope changes, and overlapping Responsibility Scopes. Do not solve them speculatively; reopen them when the vertical slice reaches that behavior.

## Gate

This checkpoint may merge when the hosted Harness gate passes for the PR head. Passing this gate records documentation/process consistency only; it does not grant implementation authorization.

## Next

Start a fresh session from this capsule. Define the **minimal Resource Catalogue Tactical model**, then immediately revalidate minimal Application Deployment against ACC + RC. Avoid deeper ACC refinement unless the end-to-end slice exposes a blocking semantic gap.
