# First MVP vertical — Architecture

Status: `active S3 Architecture`.

Date: 2026-09-15.

## Goal

Define the smallest feasible target realization for the G2-accepted first MVP vertical without changing domain meaning or adding speculative infrastructure.

## Accepted semantic scope

```text
ACC InteractionContractRevision
-> AD ApplicationDeployment / ComponentPlacement
-> RC Resource / HostAddress realization
-> AG bilateral authorization
-> AP current Policy Rule
-> RPM TargetRequiredPolicy
-> PPI ConfiguredEffectivePolicySnapshot
-> APR exact comparison
-> VerifiedChangeIntent(ENSURE-PERMIT)
-> Provider Policy Renderer
-> TargetPolicyArtifact
-> NEO controlled mutation
```

Current deliberate limitations remain authoritative:

- exactly one applicable ResponsibilityScope per AG side;
- HostAddress-to-HostAddress technical materialization only for the first NEP/RPM edge;
- Prefix input is unresolved, never host-expanded;
- APR remediation is additive-only on `missing`;
- no automatic removal of `excess`;
- provider rendering fails closed when semantic equivalence cannot be established;
- NEO executes one artifact with explicit mutation authority/preconditions;
- execution success is not final semantic convergence proof.

## S3 questions

Architecture must define only what implementation would otherwise have to invent:

1. where the thin vertical orchestration lives without creating a new semantic owner;
2. consumer-owned ports between existing contexts/capabilities;
3. dependency direction and package boundaries;
4. how current authoritative data is read without peer-private persistence access;
5. transaction/snapshot consistency needed for one end-to-end operation;
6. fail-closed propagation for unresolved/incomplete/unsupported states;
7. idempotency/correlation boundaries for rendering and NEO;
8. minimal migration/compatibility strategy from current runtime structures;
9. which existing code can be retained/adapted/replaced without treating it as target truth.

## Architecture rule

Prefer in-process application orchestration and explicit ports for the MVP. Do not introduce messaging, distributed workflows, new services, caches or durable orchestration state unless a demonstrated requirement makes them necessary.

## Working set

Start with:

- `docs/process/architecture-stage.md`
- `docs/domain/context-map.md`
- `docs/domain/strategic-model.md`
- `docs/decisions/ADR-020-required-policy-materialization-is-derived-composition.md`
- `docs/decisions/ADR-021-provider-policy-interpretation-and-rendering-boundaries.md`
- `docs/requirements/access-policy-realization-mvp.md`
- `docs/requirements/provider-policy-renderer-mvp.md`
- `docs/requirements/network-environment-operations.md`
- only the affected current code/packages needed to map realization gaps.

## Exit criteria / G3

- one clear technical owner for orchestration responsibilities;
- explicit ports/adapters and dependency direction;
- no peer-private model/database navigation;
- consistency/precondition strategy preserves accepted semantics;
- unresolved/incomplete/unsupported cases fail closed end to end;
- provider-specific code remains outside APR core and NEO does not render;
- migration from current runtime is bounded and removable;
- no unresolved P0/P1 architecture contradiction remains;
- implementation would not need to invent architecture or upstream semantics.

No implementation authorization is implied.
