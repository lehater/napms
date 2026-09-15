# Active execution

Current: `mvp-vertical-architecture.md`
Goal: define the smallest feasible target architecture for the G2-accepted first MVP semantic vertical before any implementation readiness decision.
Current task: map current realization and fix dependency/port/consistency/migration architecture for ACC -> AD -> RC -> AG -> AP -> RPM -> APR -> renderer -> NEO.
Lifecycle stage: `S3`
Stage state: `IN_PROGRESS`
Lifecycle basis: `docs/plans/active/mvp-vertical-architecture.md`, G2 PASS in the completed MVP vertical consistency checkpoint, canonical `docs/domain/context-map.md`, `docs/domain/strategic-model.md`, ADR-020 and ADR-021.
Implementation authorization: `none`
Authorized scope: `none`
Authorization basis: `none`

## MVP execution rule

Build the smallest working end-to-end happy path, not a feature-complete platform. Preserve accepted context ownership and public contracts; defer richer lifecycle, generalized scope algebra, Prefix-aware NEP, managed-policy removal, optimization, migration machinery and edge-case semantics until concrete pressure appears.

Prefer local/in-process orchestration and explicit ports for MVP. Do not introduce messaging, new deployable services, distributed transactions or durable workflow engines unless S3 finds a concrete requirement.

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
- Prefix Resource realization is preserved upstream but unresolved for the current HostAddress-only NEP/RPM edge;
- APR may remediate `missing` only; `excess` is report/audit evidence, not automatic removal;
- provider rendering must prove semantic equivalence or fail closed;
- NEO `Verified` is immediate artifact/application verification, not final semantic convergence.

## Working set

Read first:

- `docs/plans/active/mvp-vertical-architecture.md`
- `docs/process/architecture-stage.md`
- `docs/domain/context-map.md`
- `docs/decisions/ADR-020-required-policy-materialization-is-derived-composition.md`
- `docs/decisions/ADR-021-provider-policy-interpretation-and-rendering-boundaries.md`
- `docs/requirements/access-policy-realization-mvp.md`
- `docs/requirements/provider-policy-renderer-mvp.md`
- `docs/requirements/network-environment-operations.md`
- only affected current code/packages required to map the realization gap.

## Gate

G2 PASS applies only to this first MVP vertical semantic slice.

G3 is open. No implementation authorization exists. Code changes remain forbidden until later S4/G4 creates a scoped implementation lease.

## Next

Map the current runtime against the accepted target and choose the smallest architecture that implementation can follow without inventing ownership, consistency or failure behavior.
