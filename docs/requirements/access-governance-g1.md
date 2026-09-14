# Access Governance — G1 Requirements Passport

Status: `G1 revalidation candidate accepted at observable-behavior level; BC boundary not decided`.

Date/source: stakeholder revalidation, 2026-09-14.

## Problem / outcome

A user responsible for a source Resource must be able to request concrete network access to another Resource. Authorization must be distributed between the responsible source and destination sides, not decided by one centralized approver.

## Request semantics

1. A deliberate Access Request shall request permission for a concrete deployed realization of a Process-backed Connectivity Need.
2. The concrete authorization subject shall distinguish source Deployment, destination Deployment and stable Interaction meaning.
3. The Request shall preserve the business justification used at submission/decision time; later changes shall not rewrite history.
4. Address changes and Endpoint changes on the same Resource shall not by themselves require a new Request.
5. Replacement of source/destination Deployment or material expansion/change of Interaction shall require renewed authorization.
6. Request initiation authority is distinct from approval authority.

## Bilateral approval

7. Every ordinary Access Request shall require independent source-side and destination-side approval obligations.
8. Overall approval shall be granted only after both required sides approve.
9. Either required side may reject the Request.
10. Side decisions may occur in either order; one positive side decision shall not make the Request authorized while the other obligation remains unresolved.
11. There is no mandatory centralized approver that substitutes for both responsible sides.
12. The same actor may satisfy both side obligations only when that actor independently has effective approval authority for both corresponding scopes; two different humans are not inherently required.

## Authority integration

13. Approval authority shall not be inferred from Resource Owner or Administrator facts.
14. An approving actor shall have effective authority for the corresponding side/scope at decision time, derived through the authority model (for example membership in a Group with a Role assigned in a Scope).
15. Request initiation, source approval, destination approval, revocation and network execution shall be independently authorizable actions even when a role later groups some of them.
16. Access Governance shall consume effective authority results rather than depend on the internal mechanics/names of roles and group assignments.
17. Approval provenance shall preserve actor, side, decision/outcome, decision time, reason when supplied, scope and sufficient authority basis/provenance to explain why the actor could decide at that time.
18. Later removal of an actor's role shall not rewrite a historically valid decision.
19. Ambiguous/unresolved approval authority shall not be treated as successful approval.

## Revocation

20. Grant requires consent from both required sides.
21. Either authorized side shall be able to withdraw its consent for current access without approval from the other side.
22. Rejecting a pending Request and revoking/withdrawing consent from existing authorized access are different actions.
23. Revocation shall not rewrite the original approved Request as rejected.
24. Revocation shall not delete an underlying Connectivity Need that remains a valid business requirement.
25. Access shall not automatically become authorized again merely because the cause of revocation disappears. A new explicit authorization action is required.
26. An authorized side must be able to withdraw consent for the current semantic authorization subject, not merely cancel one arbitrary historical approval record while equivalent current authorization silently continues.

## Governance history and Policy handoff

27. Rejected Requests shall remain governance history and shall not create a semantic deny Policy Rule.
28. Multiple approved Requests/Needs may support the same semantic authorization subject without requiring duplicate current Policy Rules.
29. Access Governance shall preserve the history of requests, side decisions, grants and withdrawals sufficiently to explain current and past authorization.
30. Access Policy shall receive the resulting authorization grant/withdrawal semantics; Access Policy is not responsible for running the bilateral approval workflow.

## Important negative requirements

- `ownerGroup` and `administratorGroup` are not implicit approver lists.
- `requester == approver` is not assumed and is not forbidden when authority legitimately permits both actions.
- Approval does not imply immediate firewall realization.
- Revocation does not imply that the network has already removed technical access.
- A single global `Allowed/NotAllowed` Decision is insufficient to represent the required bilateral governance history.

## Capability clues, not BC decisions

- Access Request Submission
- Approval Obligation Determination
- Side Approval
- Bilateral/Composite Approval Evaluation
- Authorization Grant
- Authorization Revocation
- Governance History

## G1 status

The bilateral behavior and authority separation are sufficiently clear for G1. Exact entity identities, state machine, consent/grant representation, time-bounded authorization and BC grouping remain S2/later work.
