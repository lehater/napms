# Active execution

Current: `domain-erd-revalidation.md`

Goal: converge revalidated capabilities into coherent Strategic/Tactical DDD before affected Architecture or implementation proceeds.

Current task: select the next S2 slice after completing required-policy materialization ownership and Resource realization semantics.

Lifecycle stage: `S2`

Stage state: `NOT_STARTED`

Lifecycle basis: governance-chain S2 and required-policy materialization S2 have `G2 PASS`. ADR-019 establishes Business Connectivity / Access Governance boundaries. ADR-020 establishes Required Policy Materialization as a non-peer derived composition over Access Policy, ACC, Resource Catalogue and NEP. Resource Catalogue target realization now defines stable ResourceEndpoint identity plus separate current corporate-visible address/prefix realization. No G3/G4 or implementation authorization exists.

Implementation authorization: `none`

Authorized scope: `none`

Authorization basis: `none`

## Working set

Read first:
- `docs/domain/strategic-model.md`
- `docs/requirements/policy-realization-reconciliation-g1.md`
- `docs/process/domain-design-stage.md`

## Completed governance-chain S2

```text
Business Connectivity
    -- Process-backed Need --> Access Governance
Authority Management
    -- effective authority --> Access Governance
ACC
    -- deployed Interaction subject --> Access Governance / Access Policy
Access Governance
    -- AuthorizationGranted / AuthorizationWithdrawn --> Access Policy
```

Critical invariant: revocation changes current consent for the semantic AuthorizationSubject; old approved Requests cannot silently reauthorize it.

Gate: `G2 PASS`.

## Completed required-policy materialization S2

ADR-020 resolves the previously unnamed seam:

```text
Access Policy effective Rules
+ ACC Interaction traffic
+ Resource Catalogue current Endpoint/address realization
        -> normalized required technical predicates
        -> NEP candidate target/policy locators
        -> TargetRequiredPolicy
        -> APR
```

Ownership result: **derived non-peer composition**, not a new Bounded Context.

Resource Catalogue target realization:

```text
Resource
    -> ResourceEndpoint [0..N]
        -> current corporate-visible address/prefix [0..1]
```

Endpoint identity survives address changes. Missing address/placement/locator produces explicit `unresolved`; it is not empty required policy and not APR drift.

Predicate deduplication preserves all contributing Policy Rule provenance. Revocation recomputes aggregate required policy rather than deleting a historical firewall row.

Materialization may rely on the accepted public NEP result contract without declaring NEP's separate internal S2 revalidation complete.

Gate: `G2 PASS` for the materialization slice.

## Remaining dirty areas

- provider-specific configured-policy interpretation/normalization boundary;
- provider-specific rendering boundary between APR and execution adapters/NEO;
- NEP internal S2 revalidation against accepted G1 requirements when selected;
- migration of legacy Requirement/Decision/Proposal/UI/API/runtime artifacts;
- responsibility-scope change consequences for existing authorization;
- richer deferred governance semantics only when a concrete use case requires them.

## Blockers

No repository blocker for selecting the next S2 slice.

## Gate

Governance chain: `G2 PASS`.

Required Policy Materialization: `G2 PASS`.

Next selected slice: `S2 NOT_STARTED`.

No implementation lease exists.

## Next

Revalidate the provider boundary around configured effective-policy semantics and rendering:

```text
provider/device configuration evidence
    -> provider-specific effective-policy interpretation
    -> normalized configured effective policy
        -> APR comparison/change design/verification
    -> verified vendor-neutral change
    -> provider-specific rendering
    -> NEO execution
```

First question: whether effective-policy interpretation and target rendering are adapter/integration responsibilities around APR or require a separate semantic owner, while preserving APR's vendor-neutral effective-policy algebra.
