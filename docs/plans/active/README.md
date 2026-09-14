# Active execution

Current: `domain-erd-revalidation.md`

Goal: converge revalidated capabilities into coherent Strategic/Tactical DDD before affected Architecture or implementation proceeds.

Current task: select and start the next S2 slice: semantic-to-technical required-policy materialization between Access Policy, catalogue/resource truth, NEP and APR.

Lifecycle stage: `S2`

Stage state: `NOT_STARTED`

Lifecycle basis: governance-chain S2 has `G2 PASS` on branch `docs/s2-strategic-capability-recomposition`. ADR-019 establishes separate Business Connectivity and Access Governance contexts; target Tactical models now define Need, Request/bilateral current consent, Policy Rule grant/withdrawal consumption and exactly-one-Resource ComponentDeployment semantics. No G3/G4 or implementation authorization exists.

Implementation authorization: `none`

Authorized scope: `none`

Authorization basis: `none`

## Working set

Read first:
- `docs/requirements/policy-realization-reconciliation-g1.md`
- `docs/requirements/access-policy-core.md`
- `docs/process/domain-design-stage.md`

## Expand when needed

Load ACC/Resource Catalogue/NEP requirements and target models only when the materialization contract needs their owned facts. Load APR context problems/problem statement only when assigning the downstream reconciliation seam. Do not preload legacy CR/CD artifacts.

## Completed governance-chain S2

Strategic ownership:

```text
Business Connectivity
    -- Process-backed Need --> Access Governance

Authority Management
    -- effective actor/action/scope authority --> Access Governance

ACC
    -- deployed Interaction subject --> Access Governance / Access Policy

Access Governance
    -- AuthorizationGranted / AuthorizationWithdrawn --> Access Policy
```

Accepted Tactical owners:
- `docs/domain/business-connectivity/target-tactical-model.md`;
- `docs/domain/access-governance/target-tactical-model.md`;
- `docs/domain/access-policy/tactical-model.md`;
- `docs/domain/application-communication-catalogue/target-model.md`.

Critical invariant: revocation changes current consent for the semantic AuthorizationSubject; it is not cancellation of one historical Request. Old approved Requests cannot silently reauthorize a withdrawn subject.

Governance-chain gate: `G2 PASS`.

## Remaining dirty areas

- ownership/contract for semantic Policy Rule -> technical required-policy materialization;
- provider-specific effective-policy normalization/rendering boundary around TAE/APR/operations;
- NEP S2 revalidation against its accepted G1 requirements when selected;
- Resource Catalogue target details needed by materialization;
- migration of legacy Requirement/Decision/Proposal/UI/API/runtime artifacts;
- richer deferred governance semantics only when a concrete use case requires them.

## Blockers

No repository blocker for starting the next S2 slice.

## Gate

Governance-chain S2: `G2 PASS`.

Current next slice: `S2 NOT_STARTED`.

No implementation lease exists.

## Next

Determine the semantic owner and public contract for:

```text
Effective semantic Policy Rules
    -> current Resource/Endpoint realization
    -> Interaction traffic semantics
    -> normalized technical predicates
    -> NEP candidate locations/locators
    -> target-specific required effective policy
    -> APR reconciliation
```

First question: is this chain one independent domain responsibility, a non-peer application projection/composition, or several contracts whose ownership already belongs to existing contexts?
