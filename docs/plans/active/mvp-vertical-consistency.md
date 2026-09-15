# MVP vertical consistency checkpoint

Status: `completed — G2 PASS for first MVP semantic vertical`.

Date: 2026-09-15.

## Scope

The evaluated semantic path is:

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

## Preserved MVP boundaries

- governed subject = InteractionContractRevisionRef + source/destination ApplicationDeploymentRef;
- AG first path requires exactly one applicable ResponsibilityScope per side;
- material approval-obligation change withdraws current authorization;
- AP consumes only AuthorizationGranted / AuthorizationWithdrawn;
- RPM is derived composition, not a Bounded Context;
- current RPM -> NEP first path is HostAddress-to-HostAddress; Prefix remains unresolved, not expanded;
- comparison scope = firewallId + accessListName;
- APR comparison = exact common/missing/excess over complete comparable effective permit spaces;
- MVP remediation is additive-only: ENSURE-PERMIT on missing; excess is report/audit only;
- provider rendering must preserve verified semantics or fail closed;
- NEO owns execution authority/preconditions/outcome and does not reinterpret policy;
- apply/operation success is not final semantic convergence proof.

## Findings resolved during pass

- removed stale statements that accepted AG questions were still open;
- aligned canonical strategic status through APR / Provider Renderer / NEO rather than stopping at RPM;
- aligned APR additive-remediation requirements and minimal VerifiedChangeIntent;
- aligned Provider Policy Renderer boundary and TargetPolicyArtifact shape;
- aligned NEO requirements/Tactical model to consume TargetPolicyArtifact while keeping mutation authority and convergence separate;
- kept unresolved/empty/failure distinctions explicit across RPM/APR/renderer/NEO.

## G2 result

`G2 PASS` for the first MVP semantic vertical.

Architecture may rely on the accepted semantic ownership, identities, cross-context contracts, fail-closed boundaries and current MVP limitations above.

This does not imply global G2 for unrelated scopes and does not authorize implementation.

## Next

Proceed to S3 Architecture for this exact vertical slice. Define the smallest feasible realization, dependency direction, ports/adapters, consistency/failure behavior and migration from current runtime without reopening accepted semantics unless Architecture exposes a genuine contradiction.
