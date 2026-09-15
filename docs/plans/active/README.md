# Active execution

Current: `mvp-vertical-consistency.md`
Goal: verify the first accepted end-to-end MVP semantic path is internally coherent before any implementation authorization.
Current task: run a bounded cross-contract consistency pass over ACC -> AD -> RC -> AG -> AP -> RPM -> APR -> renderer -> NEO.
Lifecycle stage: `S2`
Stage state: `IN_PROGRESS`
Lifecycle basis: accepted 2026-09-15 AG Q1/Q2/Q3 decisions, APR exact-comparison checkpoint, additive-only remediation decision, ADR-020 and ADR-021.
Implementation authorization: `none`
Authorized scope: `none`
Authorization basis: `none`

## MVP execution rule

Build the smallest working end-to-end happy path, not a feature-complete domain model. Define only semantics required by that path; preserve stable context boundaries, identities and public contracts; defer richer lifecycle, generalized scope algebra, Prefix-aware NEP, managed-policy removal, optimization, migration machinery and edge-case semantics until concrete pressure appears.

## Current vertical baseline

```text
ACC InteractionContractRevision
        -> AD ApplicationDeployment / ComponentPlacement
        -> RC Resource / HostAddress realization
        -> AG bilateral authorization
        -> AP current Policy Rule
        -> RPM TargetRequiredPolicy
        -> APR common/missing/excess
        -> VerifiedChangeIntent(ENSURE-PERMIT)
        -> Provider Policy Renderer
        -> TargetPolicyArtifact
        -> NEO controlled mutation
```

Current deliberate limitations:

- AG first path requires exactly one applicable ResponsibilityScope per side;
- Prefix Resource realization is preserved upstream but RPM is unresolved for the current HostAddress-only NEP edge;
- APR may remediate `missing` only; `excess` is report/audit evidence, not automatic removal;
- provider rendering must prove semantic equivalence or fail closed;
- NEO `Verified` is immediate artifact/application verification, not final semantic convergence.

## Working set

Read first:

- `docs/plans/active/mvp-vertical-consistency.md`
- `docs/domain/context-map.md`
- `docs/domain/strategic-model.md`
- `docs/domain/strategic-model.json`
- `docs/requirements/access-governance-g1.md`
- `docs/domain/access-governance/target-tactical-model.md`
- `docs/domain/access-policy/tactical-model.md`
- `docs/decisions/ADR-020-required-policy-materialization-is-derived-composition.md`
- `docs/requirements/access-policy-realization-mvp.md`
- `docs/domain/access-policy-realization/README.md`
- `docs/requirements/provider-policy-renderer-mvp.md`
- `docs/requirements/network-environment-operations.md`
- `docs/domain/network-environment-operations/tactical-model.md`

Expand only when a concrete contradiction points to another owner document.

## Gate

No implementation authorization exists. This pass may align documentation/contracts only.

## Next

Finish the bounded consistency pass. If no blocking semantic contradiction remains, record the vertical design checkpoint as ready for an explicit implementation-authorization decision rather than silently starting implementation.
