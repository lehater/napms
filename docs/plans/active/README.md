# Active execution

Current: `mvp-ddd-convergence.md`
Goal: finish the DDD required by the first MVP semantic vertical before any further architecture/readiness/implementation work.
Current task: close the remaining MVP Tactical DDD gaps, beginning with Application Deployment and then Access Policy Realization, followed by one bounded cross-context DDD consistency pass.
Lifecycle stage: `S2`
Stage state: `IN_PROGRESS`
Lifecycle basis: `docs/plans/active/mvp-ddd-convergence.md`, accepted strategic context map/model, existing ACC/RC/AG/AP/NEP/NEO Tactical models, and the explicit stakeholder instruction on 2026-09-15 to finish DDD before returning to code.
Implementation authorization: `none`
Authorized scope: `none`
Authorization basis: `none`

## Execution rule

Remain within domain design. Do not modify production code, tests, schemas, migrations, bootstrap, adapters, HTTP or UI while this S2 plan is active.

The existing experimental target APR code already committed on this branch is intentionally left in place but frozen. It is implementation evidence only and must not be used as authoritative domain truth.

The previous G4 Slice 1 lease is revoked. Any later implementation requires a new explicit S3/S4/G4 cycle after DDD closure and only when requested.

## MVP design rule

Complete only the DDD needed for the minimal happy path. Preserve clear ownership, identities, invariants and public semantic contracts, but defer future generalization.

Do not expand into:

- generalized overlapping Responsibility Scope algebra;
- Prefix-aware NEP;
- multiple simultaneous Resource addresses/interfaces;
- managed-policy removal/narrowing;
- richer provider-specific semantics;
- generalized workflow/state-machine infrastructure;
- persistence/transport/package design.

## Current vertical baseline

```text
ACC InteractionContractRevision
        -> AD ApplicationDeployment / ComponentPlacement
        -> RC Resource / AddressSpace
        -> AG bilateral authorization
        -> AP current Policy Rule
        -> RPM TargetRequiredPolicy
        -> APR realization assessment / VerifiedChangeIntent
        -> Provider Policy Renderer boundary
        -> NEO controlled mutation semantics
```

## Current DDD gaps

1. `Application Deployment` — strategic boundary accepted, MVP Tactical model still missing.
2. `Access Policy Realization` — comparison/additive semantics accepted, but MVP Tactical classification/identity/lifecycle/invariant model still needs closure.
3. After those two, run one bounded DDD consistency pass and remove stale open-status statements only where the question is actually resolved.

## Working set

Read first:

- `docs/plans/active/mvp-ddd-convergence.md`
- `docs/process/domain-design-stage.md`
- `docs/process/tactical-ddd-stage.md`
- `docs/domain/application-deployment/boundary.md`
- `docs/domain/access-policy-realization/README.md`
- neighboring canonical domain contracts only when needed for the active semantic question.

## Gate

G2 is open for the complete first MVP vertical. Previous partial/edge G2 conclusions remain useful evidence but do not authorize moving past DDD while material Tactical gaps remain.

Even after G2 PASS, stop at design. Do not proceed to S3/S4/implementation unless explicitly requested later.

## Next

Close Application Deployment Tactical DDD with the smallest model that supports placement multiplicity, deployment continuity and downstream governance/materialization without inventing runtime-instance or endpoint semantics.
