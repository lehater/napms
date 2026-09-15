# Access Governance requirements

## Purpose

Define the observable governance behavior for requesting, approving, withdrawing and re-establishing authorization for one governed Interaction between logical ApplicationDeployments.

## Governed subject

```text
GovernedInteractionSubject {
    interactionContractRevisionRef
    sourceApplicationDeploymentRef
    destinationApplicationDeploymentRef
}
```

Resource addresses and individual ComponentPlacements are not part of subject identity.

## Requirements

1. A deliberate Access Request requests permission for a Process-backed Connectivity Need applied to one concrete logical source/destination ApplicationDeployment pair.
2. The Request preserves business justification and the approval/authority provenance used for its decisions; later current-state changes do not rewrite those historical decisions.
3. Resource address changes, ordinary ComponentPlacement replacement and Resource replacement do not create a new governed subject while both ApplicationDeployment identities and the InteractionContractRevision remain unchanged.
4. Replacing the InteractionContractRevision or either logical ApplicationDeployment creates a different governed subject.
5. Request initiation authority is distinct from approval authority.
6. Authorization requires independent source-side and destination-side approval obligations; current grant requires both obligations to be satisfied.
7. Either required side may reject a pending Request.
8. Either authorized side may withdraw its current consent without approval from the other side.
9. Rejection and withdrawal are distinct and do not rewrite prior valid decisions.
10. Old approved Requests do not silently restore withdrawn consent.
11. Request, approval and withdrawal authority is evaluated through Authority Management and is not inferred from Resource owner, administrator, responsibility or contact metadata.
12. Rejected Requests create no semantic deny Policy Rule.
13. Access Policy consumes `AuthorizationGranted` and `AuthorizationWithdrawn`; it does not own bilateral governance.
14. A source/destination ApplicationDeployment pair is selectable for a declared Interaction only when each deployment can realize the corresponding Interaction endpoint Component and the current placement/scope facts required to determine approval obligations are resolvable.
15. A placement or Resource Scope Affiliation change does not automatically withdraw authorization. If the change materially changes the approval obligations for the same governed subject, AG withdraws current authorization with provenance for that obligation change.
16. Earlier approvals do not silently satisfy a materially changed set of current obligations.
17. The same governed subject may become authorized again only after its current approval obligations are satisfied and AG publishes a new `AuthorizationGranted`.
18. Each governance side currently resolves to exactly one distinct applicable `ResponsibilityScopeRef` when approval obligations are evaluated.
19. If either side resolves to zero or more than one distinct applicable Responsibility Scope, the obligations are unresolved and the pair is not selectable/authorizable. AG fails closed and does not choose a scope by precedence or require all overlapping scopes implicitly.

## Current scope boundary

The current Access Governance contract uses one applicable Responsibility Scope per side. Resource Catalogue may still contain several effective Resource Scope Affiliations; AG simply cannot authorize a subject whose required side resolves ambiguously under the current contract.

The model contains no separate `Suspended` product state. If placement/scope changes leave obligations materially unchanged, current authorization remains effective. If obligations change materially, current authorization is withdrawn until the new obligations are satisfied.

The current requirements do not define generalized overlapping-scope approval algebra, precedence rules, quorum approval, explicit deny policy or automatic inference from planned/future deployments.
