# MVP vertical consistency checkpoint

Status: `active cross-contract consistency pass`.

Date: 2026-09-15.

## Goal

Check only the first accepted end-to-end MVP semantic path for contradictions or stale blockers before considering implementation authorization.

```text
ACC InteractionContractRevision
    -> AD ApplicationDeployment / ComponentPlacement
    -> RC Resource / AddressSpace
    -> AG bilateral authorization
    -> AP current Policy Rule
    -> RPM TargetRequiredPolicy
    -> PPI ConfiguredEffectivePolicySnapshot
    -> APR comparison + additive VerifiedChangeIntent
    -> Provider Policy Renderer
    -> TargetPolicyArtifact
    -> NEO controlled mutation
```

## Accepted MVP boundaries to preserve

- MVP means minimal happy path; extensions stay deferred until concrete pressure.
- Governed subject = InteractionContractRevisionRef + source/destination ApplicationDeploymentRef.
- AG requires exactly one applicable ResponsibilityScope per side for the first path.
- Material approval-obligation change withdraws current authorization.
- AP consumes only AuthorizationGranted / AuthorizationWithdrawn.
- RPM is derived composition, not a Bounded Context.
- current RPM -> NEP first path is HostAddress-to-HostAddress; Prefix remains unresolved, not expanded.
- comparison scope = firewallId + accessListName.
- APR comparison = exact common/missing/excess over complete comparable effective permit spaces.
- MVP remediation is additive-only: ENSURE-PERMIT on missing; excess is report/audit only.
- provider rendering must preserve verified semantics or fail closed.
- NEO owns execution authority/preconditions/outcome and does not reinterpret policy.
- apply/operation success is not final semantic convergence proof.

## Check scope

Inspect canonical strategic/domain/requirements documents touched by these edges only.

Fix:

- stale statements that an already accepted question is still open;
- identity/ownership contradictions;
- inconsistent comparison/target keys;
- accidental promotion of deferred behavior into the MVP;
- missing fail-closed distinction that could turn unresolved into empty/success.

Do not:

- expand APR deeper Tactical backlog;
- design production provider adapters;
- solve Prefix-aware NEP;
- add managed-policy removal semantics;
- authorize implementation.

## Exit criteria

- no known P0/P1 semantic contradiction on the first vertical path;
- active plan names the next actual step;
- implementation remains unauthorized unless explicitly granted later.
