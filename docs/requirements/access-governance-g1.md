# Access Governance — G1 Requirements Passport

Status: `G1 bilateral behavior retained; deployment subject aligned 2026-09-15; three behavior questions reopened`.

## Observable requirements

1. A deliberate Access Request shall request permission for a Process-backed Connectivity Need applied to a concrete logical source/destination ApplicationDeployment pair.
2. The semantic subject shall distinguish `InteractionContractRevisionRef`, source `ApplicationDeploymentRef` and destination `ApplicationDeploymentRef`.
3. The Request shall preserve the business justification and approval basis used at submission/decision time; later changes shall not rewrite history.
4. Resource address changes, ordinary ComponentPlacement replacement and Resource replacement shall not by themselves create a different governed subject while ApplicationDeployment continuity is preserved.
5. Material change of InteractionContractRevision or replacement of either logical ApplicationDeployment creates a different subject.
6. Request initiation authority is distinct from approval authority.
7. Ordinary authorization requires independent source-side and destination-side approval obligations; overall grant requires both.
8. Either required side may reject a pending Request.
9. Either authorized side may later withdraw its current consent without approval from the other side.
10. Rejection and withdrawal are distinct; neither rewrites historical valid decisions.
11. Old approved Requests cannot silently restore withdrawn consent.
12. Approval/revoke authority is evaluated through Authority Management and is not inferred from Resource Owner/Administrator/Responsibility metadata.
13. Rejected Requests remain history and create no semantic deny Policy Rule.
14. Access Policy consumes `AuthorizationGranted` / `AuthorizationWithdrawn`; it does not run bilateral governance.

## Current subject

```text
GovernedInteractionSubject {
    interactionContractRevisionRef
    sourceApplicationDeploymentRef
    destinationApplicationDeploymentRef
}
```

Technical Resource AddressSpace is not part of subject identity.

## Reopened S1 behavior

The AD boundary makes these product questions operationally material and they remain unresolved:

1. What constraints determine selectable source/destination ApplicationDeployment pairs?
2. When placement or Resource Scope Affiliation changes alter approval obligations, does current authorization remain valid, require reapproval, warn, suspend or withdraw?
3. When several Responsibility Scopes simultaneously apply to one side, which approval obligations are required?

Tactical AG must not invent these answers.
