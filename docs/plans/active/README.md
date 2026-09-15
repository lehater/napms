# Active execution

Current: `mvp-ddd-convergence.md`
Goal: keep the first MVP target DDD baseline as the current accepted design boundary and do not proceed downstream without a new explicit request.
Current task: parked after full MVP DDD convergence; no active Architecture/Implementation task.
Lifecycle stage: `S2`
Stage state: `ACCEPTED`
Lifecycle basis: `docs/domain/mvp-ddd-convergence-checkpoint.md`, `docs/plans/active/mvp-ddd-convergence.md`, canonical `docs/domain/strategic-model.md`, `docs/domain/context-map.md`, and the accepted target Tactical models for all 11 target Bounded Contexts.
Implementation authorization: `none`
Authorized scope: `none`
Authorization basis: `none`

## Current gate

```text
G2: PASS — first MVP target DDD baseline
```

This means the accepted happy path has sufficient Strategic/Tactical domain meaning for later architecture work without implementation inventing owners, identities, lifecycle/invariants or cross-context semantic contracts.

It does **not** mean all future extensions have been modelled.

## Execution rule

Remain parked at design.

Do not modify production code, tests, schemas, migrations, bootstrap, adapters, HTTP or UI unless the project owner explicitly starts a later downstream phase.

The previous G4 Slice 1 lease remains revoked. The current branch diff against `main` contains documentation only; no backend implementation change is part of the accepted S2 result.

Any later code work requires a new explicit progression through the applicable downstream lifecycle from this accepted G2 baseline.

## Canonical DDD baseline

Read first when resuming domain/design work:

- `docs/domain/mvp-ddd-convergence-checkpoint.md`
- `docs/domain/strategic-model.md`
- `docs/domain/context-map.md`
- the specific owning Tactical model for the affected context.

Target Tactical owners now exist for:

- Business Connectivity;
- Access Governance;
- Access Policy;
- Authority Management;
- Resource Catalogue;
- Application Communication Catalogue;
- Application Deployment;
- Network Enforcement Placement;
- Technical Access Evidence;
- Access Policy Realization;
- Network Environment Operations.

Required Policy Materialization remains a derived composition. Provider Policy Interpreter/Renderer remain integration capabilities rather than Bounded Contexts.

## Explicit future reopen triggers

Reopen only the affected domain edge when a concrete requirement needs, for example:

- several simultaneous Responsibility Scopes on one governance side;
- richer authority rules such as nested groups/explicit deny/ABAC/quorum;
- Prefix-aware NEP;
- multiple simultaneous Resource addresses/interfaces/VIPs/exposure;
- managed-policy removal/narrowing;
- richer ApplicationDeployment or BusinessProcess lifecycle/history;
- ACC revision workflow beyond immutable snapshots;
- richer APR remediation semantics/durable plans.

Do not model these speculatively.

## Next

No automatic next phase. Await an explicit project-owner request before entering S3 Architecture or any later stage.
