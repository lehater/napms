# Domain Revalidation Plan

Status: `active domain revalidation`.

Date: 2026-09-14.

## Goal

Revalidate only the domain scopes whose accepted S1 semantics or upstream contracts changed, lock coherent Strategic/Tactical DDD before Architecture/implementation, and keep unrelated completed contexts parked.

Current runtime/code/schema remain migration evidence, not automatic target truth.

## Current accepted baseline

Breadth-first capability G1 is accepted.

Current target strategic owners include:

- **Business Connectivity** — Business Process, Connectivity Need, business attribution/justification;
- **Access Governance** — Access Request, bilateral consent, grant/withdrawal and governance history;
- **Authority Management** — effective actor/action/scope authority;
- **Access Policy** — current authoritative Policy Rule truth;
- **Application Communication Catalogue** — concrete ComponentDeployment + immutable Interaction subject;
- **Resource Catalogue** — Resource/Endpoint/current realization;
- **Network Enforcement Placement** — candidate enforcement locations/policy locators;
- **Technical Access Evidence** — normalized source-qualified technical evidence;
- **Access Policy Realization** — required-vs-configured semantic reconciliation/change reasoning, with some downstream ownership still dirty.

ADR-019 supersedes the target-boundary assumptions that preserved/excluded the old `Connectivity Requirements` / `Connectivity Decision` model. Those names remain legacy/current-state evidence, not current target Bounded Contexts.

ADR-015 is amended: in MVP each ComponentDeployment belongs to exactly one Resource for its lifetime; moving the Component to another Resource creates another ComponentDeployment.

## Completed S2 slice — governance chain

Strategic DDD accepted:

```text
Business Connectivity
    -- Process-backed Need --> Access Governance

Authority Management
    -- effective action authority --> Access Governance

ACC
    -- concrete deployed Interaction subject --> Access Governance / Access Policy

Access Governance
    -- AuthorizationGranted / AuthorizationWithdrawn --> Access Policy
```

Tactical DDD accepted for the current slice:

- `docs/domain/business-connectivity/target-tactical-model.md`;
- `docs/domain/access-governance/target-tactical-model.md`;
- `docs/domain/access-policy/tactical-model.md` revalidated against grant/withdrawal semantics;
- `docs/domain/application-communication-catalogue/target-model.md` revalidated for exactly-one-Resource deployment semantics.

Core invariants:

- Need is application-semantic business truth, not permission;
- Access Request is one explicit authorization attempt and historical evidence;
- current bilateral consent is subject-level state, not one historical Request;
- grant requires source AND destination consent;
- withdrawal by either side removes current authorization and old approved Requests do not silently restore it;
- Access Policy consumes grant/withdrawal facts and owns one authoritative Rule meaning per semantic subject;
- address/Endpoint changes on the same Resource do not change authorization identity;
- Resource movement creates a different ComponentDeployment and requires renewed authorization.

Governance-chain S2 result: `G2 PASS` for this affected scope.

## Parked/deferred questions from this slice

These are not blockers for the accepted core invariants:

- Process criticality scale and richer Process lifecycle;
- exact Need applicability/time representation and duplicate declaration policy;
- Access Request cancellation/expiry;
- time-bounded authorization representation;
- overlapping-scope selection rules;
- responsibility-scope-change consequences for existing authorization;
- exact Rule revision/reactivation representation;
- endpoint-specific ComponentDeployment binding.

Reopen the smallest owning stage when a concrete use case requires one of them.

## Remaining dirty domain areas

### Semantic-to-technical required-policy materialization

Still unresolved:

```text
Effective semantic Policy Rules
    -> Deployment / Resource / Endpoint realization
    -> Interaction traffic contract
    -> normalized technical predicates
    -> NEP candidate enforcement locations / locators
    -> target-specific required effective policy
```

The final semantic owner/boundary for this materialization/projection must be established before downstream Architecture guesses it.

### Access Policy Realization / provider boundary

APR's stable responsibility is normalized required-vs-configured reconciliation and semantic change reasoning for a supplied comparable target.

Provider-specific normalization/rendering ownership remains dirty and must be revalidated separately from APR's semantic core.

### Legacy runtime/domain artifacts

Old Connectivity Requirements/Decision, Proposal and related UI/API/persistence are migration/current-state evidence. Their removal/transformation is S4/implementation work only after affected target design and architecture are accepted.

### Other independent slices

NEP remains separately checkpointed after G1 and can resume S2 against its accepted requirements when selected. Resource Catalogue/APR context-problem registers remain available for independent workstreams.

## Review method

For each selected slice:

1. identify the smallest semantic question and accepted G1 pressure;
2. route to Strategic or Tactical DDD;
3. update the highest affected semantic owner first;
4. make cross-context contracts explicit before peer internals;
5. revalidate only dependent Tactical semantics;
6. record P0/P1 blockers explicitly;
7. pass G2 only when Architecture no longer has to invent ownership/identity/lifecycle/invariants;
8. do not authorize implementation without later G3/G4.

## Current next slice

Revalidate ownership and contract for **semantic-to-technical required-policy materialization** between Access Policy/ACC/Resource Catalogue/NEP and APR.

Do not reopen the governance-chain Tactical models unless this materialization analysis exposes an actual contradiction in their accepted guarantees.
