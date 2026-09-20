# Blind backend MVP product requirements

Status: ACCEPTED for downstream design

## Goal

Support the narrow end-to-end backend journey from describing Resources and application communication, through business-backed connectivity request/decision and current desired access, to a complete explainable vendor-neutral normalized access-policy result.

## Observable behavior

### PR-RESOURCE

1. The product can create and identify a human-recognizable logical Resource independently of its current network address.
2. A Resource can expose logical network presence/endpoints whose current address realization can change without changing Resource identity.
3. Address realization can represent a host or prefix when that is the meaningful corporate-network access unit.
4. Logical Resource/endpoint creation and address assignment are separate; missing current realization is explicit.
5. Resource-level Site, Owner and Administrator information is representable; Owner/Administrator are organizational groups and do not imply security authority.
6. Basic history of changing Resource/network-realization facts remains explainable.

### PR-APPLICATION

7. The product can define reusable Applications containing Components that represent communication participants/roles.
8. It can define directed Interactions between Components. An Interaction represents one independently meaningful communication reason and carries the complete minimal traffic semantics for that reason.
9. Traffic that must be independently applicable/authorized/managed is represented by a distinct Interaction rather than merged solely because endpoints match.
10. A concrete Component deployment is identifiable separately from reusable application meaning and is associated with a Resource, not with a current IP address.

### PR-BUSINESS

11. The product can identify/describe a Business Process and associate descriptive organizational responsibility with it.
12. The product can represent a Connectivity Need stating that the Process requires an application-level Interaction.
13. Connectivity Need is independent from concrete Access Request and from IP/current deployment realization.
14. One Process can have multiple Needs; the same Interaction can support Needs from multiple Processes.
15. One Need can lead to multiple concrete Access Requests over time or for different deployments.
16. A deliberate Access Request requires a current Process-backed Connectivity Need at submission time.
17. Process/Need is business justification, not proof that connectivity is permitted.

### PR-ACCESS

18. A deliberate request for connectivity is expressed using semantic application/deployment references rather than raw firewall/vendor syntax.
19. Authority to submit/request connectivity is distinct from the permission decision whether connectivity is allowed.
20. A denied permission decision creates no current effective desired access.
21. Technical realization/address changes alone do not silently rewrite the business permission/intention they realize.
22. The backend preserves enough provenance to explain how request/business intent and permission decision contribute to current desired access.

### PR-POLICY-OUTPUT

23. Current effective desired access can be materialized for one logical evaluation time into a vendor-neutral normalized technical policy result.
24. The result preserves source/destination technical realization, interaction traffic meaning and provenance sufficient to explain each materialized access effect.
25. One semantic access may expand into several technical effects where realization requires it; expansion must not broaden/narrow accepted traffic meaning.
26. Independently meaningful access intent must not be merged when doing so would erase business/decision provenance.
27. If any included effective access lacks required trustworthy current realization/communication data, the backend must not present the result as a complete successful policy output.
28. Diagnostic partial information may be exposed only with explicit unresolved/non-success semantics.
29. Access that is not currently effective contributes no output and does not create an output-completeness failure solely because its technical realization is absent.

## Deferred accepted problem-space input

Stakeholder evidence says business importance/criticality information may be useful for downstream impact analysis, while its attributes, scale and propagation semantics are explicitly unresolved. The selected first policy-export MVP does not consume criticality. Therefore no criticality field/enum/score is part of this MVP contract; reopen Product Requirements when impact-analysis scope is selected.

## Current non-goals

- provider/device-specific configuration rendering;
- direct firewall/provider mutation and execution;
- configured-state comparison/reconciliation/remediation;
- brownfield traffic recognition/reverse attribution as an MVP prerequisite;
- BPMN/workflow engine for Business Process modeling;
- speculative Process hierarchy/monetary valuation or automatic criticality propagation;
- business-impact/criticality analysis in the selected MVP;
- frontend layout/component/visual design.

## Acceptance semantics

- Creating a Resource before it has an address succeeds while current realization remains explicitly unresolved.
- Changing a Resource address preserves Resource identity/history.
- An Interaction is invalid when it does not have a meaningful directed source Component, destination Component and non-empty traffic meaning.
- A deliberate Access Request without a current Process-backed Need is rejected.
- Possessing request authority does not make the permission outcome allowed.
- A denied decision does not appear in current desired-policy materialization.
- A successful policy materialization is complete for all included effective access at the same logical evaluation time.
- Missing required realization for one included effective access makes the overall materialization unresolved/non-success, not silently partial success.
- Equivalent technical effects retain independent provenance when they originate from independently meaningful access intent.

## Deliberately downstream

Product Requirements does not decide Bounded Contexts, aggregates, API transport, database technology, module layout, authentication mechanism, or test framework.
