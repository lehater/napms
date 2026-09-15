# Access Governance — G1 Requirements Passport

Status: `G1 bilateral behavior retained; deployment subject aligned 2026-09-15; pair selection and obligation-change behavior accepted; overlapping-scope behavior remains open`.

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
15. A source/destination ApplicationDeployment pair is selectable for an Access Request using a declared Interaction when each ApplicationDeployment can realize the corresponding Interaction endpoint Component and the current placements required to determine approval obligations are resolvable.
16. A placement or Resource Scope Affiliation change does not by itself withdraw current authorization. If the change materially changes the approval obligations for the governed subject, the current authorization shall cease to be effective and AG shall publish `AuthorizationWithdrawn` with provenance for the obligation change.
17. Historical Requests, approvals and provenance remain history after such withdrawal; they do not silently satisfy a materially changed set of current approval obligations.
18. The same governed subject may become authorized again only after the current approval obligations are satisfied and AG publishes a new `AuthorizationGranted`.

The selection rule does not imply planned/future deployment inference, generalized cross-application compatibility rules or fallback guessing when current placement/scope information is unresolved.

The obligation-change rule does not require a separate `Suspended` product state for MVP. If placement/scope changes leave the approval obligations materially unchanged, the current authorization remains effective. Exact reuse or representation of still-valid individual consent facts is Tactical-open so long as no authorization remains effective without all current obligations being satisfied.

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

One product question remains unresolved:

1. When several Responsibility Scopes simultaneously apply to one side, which approval obligations are required?

Tactical AG must not invent this answer.
