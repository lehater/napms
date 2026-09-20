# Blind backend MVP product requirements

Status: ACCEPTED after Source Corpus amendment 01

## Goal

Support the narrow end-to-end backend journey from describing Resources and application communication, through business-backed connectivity request/decision and current desired access, to a complete explainable vendor-neutral normalized access-policy result.

## Observable behavior

### PR-RESOURCE

1. The product can create and identify a human-recognizable logical Resource independently of its current network address.
2. A Resource can expose logical network presence/endpoints whose current address realization can change without changing Resource identity.
3. Address realization can represent a host or prefix when that is the meaningful corporate-network access unit.
4. Logical Resource/endpoint creation and address assignment are separate; missing current realization is explicit.
5. Resource-level Site, Owner and Administrator information is representable; Owner and Administrator are organizational groups, are distinct responsibilities and do not imply security authority.
6. At one current time a Resource has at most one current Owner group and at most one current Administrator group.
7. Basic history of changing Resource Site/responsibility/network-realization facts remains explainable.

### PR-APPLICATION

8. The product can define reusable Applications containing Components that represent communication participants/roles.
9. It can define directed Interactions between Components. Structural validity follows explicit source/destination Component references and described communication semantics; source and destination Components may belong to different Applications. An Interaction represents one independently meaningful communication reason and carries the complete minimal traffic semantics for that reason.
10. Traffic that must be independently applicable/authorized/managed is represented by a distinct Interaction rather than merged solely because endpoints match.
11. A concrete Component deployment is identifiable separately from reusable application meaning and is associated with a Resource, not with a current IP address.

### PR-BUSINESS

12. The product can identify/describe a Business Process and associate descriptive organizational responsibility with it.
13. The product can represent a Connectivity Need stating that the Process requires an application-level Interaction.
14. Connectivity Need is independent from concrete Access Request and from IP/current deployment realization.
15. One Process can have multiple Needs; the same Interaction can support Needs from multiple Processes.
16. One Need can lead to multiple concrete Access Requests over time or for different deployments.
17. A deliberate Access Request requires a current Process-backed Connectivity Need at submission time.
18. Process/Need is business justification, not proof that connectivity is permitted.
19. An already authorized/current access may acquire additional Process/Need justification later without creating a duplicate current access solely for that new justification.
20. Retiring/loss of a Need does not rewrite historical requests, decisions or prior justification provenance.
21. If an authorization has no currently known Need, that condition remains distinguishable for reconciliation, but the product does not automatically revoke/deactivate the authorization solely for that reason.

### PR-ACCESS

22. A deliberate request for connectivity is expressed using semantic application/deployment references rather than raw firewall/vendor syntax.
23. Authority to submit/request connectivity is distinct from the permission decision whether connectivity is allowed.
24. A denied permission decision creates no new authoritative current desired access.
25. A permission decision remains correlated to the exact semantic access that was requested; identity-defining semantic change must not silently inherit/rewrite a historical decision.
26. Reprocessing or separately allowing the same semantic access must resolve the same authoritative current access rather than create a duplicate.
27. First allowed materialization of a semantic access creates/resolves one authoritative current access and starts it operationally ACTIVE.
28. An authorized actor can change the current access ACTIVE <-> INACTIVE without a new permission decision. The stable access identity, permission provenance and audit/history remain.
29. A current access may carry supported declarative effective conditions. These conditions determine whether an ACTIVE access contributes desired effect at the evaluation time without periodically rewriting its stored ACTIVE/INACTIVE state.
30. Technical realization/address changes alone do not silently rewrite current-access identity or historical permission provenance.
31. The backend preserves enough provenance to explain the semantic request, permission evidence, business justifications, operational state/effective condition and current technical realization contributing to desired access.

### PR-POLICY-OUTPUT

32. Current desired access may be selected for export as a domain-policy subset. Selection is expressed in domain-policy identity, not vendor/device syntax.
33. At one logical evaluation time, a selected current access contributes desired effect only when it is backed by accepted permission evidence, is ACTIVE and its supported declarative effective conditions are satisfied.
34. Selected access that is INACTIVE or conditionally non-effective contributes no rows; missing technical realization for that non-effective access does not make the export incomplete.
35. Effective selected access can be materialized into a vendor-neutral normalized technical policy result.
36. The result preserves source/destination technical realization, interaction traffic meaning and provenance sufficient to explain each materialized access effect.
37. One semantic access may expand into several technical effects where realization requires it; expansion must not broaden/narrow accepted traffic meaning.
38. Independently meaningful current accesses must not be merged when doing so would erase business/permission provenance.
39. If any selected effective access lacks required trustworthy current realization/communication data, the backend must not present the result as a complete successful policy output.
40. Diagnostic partial information may be exposed only with explicit unresolved/non-success semantics.
41. An access with no currently known Need may still be selected/effective when otherwise authorized/ACTIVE/effective; its missing current business justification must remain explicitly visible as a reconciliation condition rather than silently revoking it.

## Minimal supported declarative effectiveness for this MVP

The source requires support for declarative time/effective conditions but does not establish a recurring-calendar language. The MVP therefore requires at least one implementation-independent **absolute effective window**:

- optional inclusive lower bound `effectiveFrom`;
- optional exclusive upper bound `effectiveUntil`;
- when both exist, `effectiveFrom < effectiveUntil`;
- ACTIVE access contributes only when evaluation time is inside the window.

Recurring/periodic schedule syntax is deferred until a concrete accepted use case defines its semantics. This preserves the accepted time-condition behavior without inventing a speculative recurrence DSL.

## Deferred accepted problem-space input

Stakeholder evidence says business importance/criticality may be useful for downstream impact analysis, while its attributes, scale and propagation semantics are explicitly unresolved. The selected policy-export MVP does not consume criticality. No criticality field/enum/score belongs to this MVP contract.

## Current non-goals

- provider/device-specific configuration rendering;
- direct firewall/provider mutation and execution;
- configured-state comparison/reconciliation/remediation;
- automatic revocation solely because all known Needs disappeared;
- recurring/periodic schedule DSL beyond the absolute effective window;
- brownfield traffic recognition/reverse attribution as an MVP prerequisite;
- BPMN/workflow engine for Business Process modeling;
- speculative Process hierarchy/monetary valuation or automatic criticality propagation;
- business-impact/criticality analysis in the selected MVP;
- frontend layout/component/visual design.

## Acceptance semantics

- Creating a Resource before it has an address succeeds while current realization remains explicitly unresolved.
- Changing a Resource address preserves Resource identity/history.
- Replacing current Owner/Administrator closes the prior role assignment and leaves at most one current assignment for that role.
- An Interaction is invalid when it lacks a meaningful directed source Component, destination Component or non-empty supported traffic meaning; it is not invalid merely because the Components belong to different Applications.
- A deliberate Access Request without a current Process-backed Need is rejected.
- Possessing request authority does not make the permission outcome allowed.
- DENIED creates no new current access.
- Two independently allowed requests for the same semantic access resolve one current access identity and preserve both authorization/request provenance items.
- A later additional current Need for the same access attaches justification without duplicating that access.
- Retiring an attached Need preserves historical justification; zero current Needs produces an explicit reconciliation condition and no automatic state transition.
- First allowed materialization is ACTIVE.
- ACTIVE -> INACTIVE -> ACTIVE preserves current-access identity and does not require a new permission decision.
- An ACTIVE access outside its absolute effective window is non-effective without changing stored ACTIVE state.
- Policy selection may include all current accesses or an explicit subset.
- A successful materialization is complete for every selected access that is effective at the same logical evaluation time.
- Missing required realization for one selected effective access makes the overall materialization unresolved/non-success, not silently partial success.
- Equivalent technical effects retain independent current-access provenance when their semantic access identities differ.

## Deliberately downstream

Product Requirements does not decide:
- the exact field tuple used to encode semantic current-access identity;
- Bounded Contexts/aggregates/value-object representation;
- API transport/DTO shape;
- database technology/schema;
- module layout;
- authentication technology;
- test framework.
