# Access Governance — G1 Requirements Passport

Status: `G1 MVP behavior accepted 2026-09-15; generalized overlapping-scope semantics deferred`.

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
19. For the MVP happy path, each governance side shall resolve to exactly one distinct applicable `ResponsibilityScopeRef` when approval obligations are determined.
20. If a source or destination side resolves to zero or more than one distinct applicable Responsibility Scope, approval obligations are unresolved for MVP and the deployment pair is not selectable/authorizable. AG shall fail closed rather than choose a scope by precedence or require all overlapping scopes without an accepted product rule.

The selection rule does not imply planned/future deployment inference, generalized cross-application compatibility rules or fallback guessing when current placement/scope information is unresolved.

The obligation-change rule does not require a separate `Suspended` product state for MVP. If placement/scope changes leave the approval obligations materially unchanged, the current authorization remains effective. Exact reuse or representation of still-valid individual consent facts is Tactical-open so long as no authorization remains effective without all current obligations being satisfied.

The single-scope-per-side rule is an Access Governance MVP boundary, not a Resource Catalogue invariant. RC may retain several distinct effective Resource Scope Affiliations; generalized overlap semantics are deferred until a concrete governance journey requires them.

## Current subject

```text
GovernedInteractionSubject {
    interactionContractRevisionRef
    sourceApplicationDeploymentRef
    destinationApplicationDeploymentRef
}
```

Technical Resource AddressSpace is not part of subject identity.

## G1 checkpoint result

The behavior required for the first Access Governance happy path is accepted:

- governed subject identity is stable;
- deployment-pair selection is fail-closed when obligations cannot be resolved;
- one source-side and one destination-side obligation are required for the MVP;
- grant requires both sides;
- either side may reject while pending or later withdraw current consent;
- material obligation change withdraws current authorization until current obligations are satisfied again;
- overlapping Responsibility Scopes are explicitly unsupported/fail-closed for the first happy path rather than implicitly resolved.

No implementation authorization is implied. Broader scope algebra, precedence and multi-scope approval behavior remain deferred product work.
