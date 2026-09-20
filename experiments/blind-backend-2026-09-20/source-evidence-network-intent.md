# Sanitized stakeholder network-intent evidence

Source class: SOURCE_INPUT / discovery evidence  
Original provenance: `docs-legacy/engineering/context-problems/stakeholder-network-intent-evidence.md`, stakeholder discussions recorded 2026-09-13/14.  
Original status: non-authoritative stakeholder evidence.

This copy intentionally removes prior solution/context names and preserves only source-level observations, revalidation evidence, candidate journeys and unresolved questions.

## Problem observations

- Working directly with raw firewall access lists is a forced low-level task rather than the desired primary user abstraction.
- A more useful abstraction is the network interaction required between described resources and application components deployed on them.
- Organizational processes are a plausible higher-level source of connectivity need: a process may require software, software may require component interactions, and those interactions may require network access.
- Desired value is causal/business traceability in both directions: from organizational need toward technical enforcement, and from observed traffic/enforcement back toward the application/process that justifies it.
- Business attributes such as criticality, importance, periodicity and lifecycle may help explain impact; exact attributes and propagation rules are unresolved.
- Rule cleanup based only on configuration syntax cannot establish whether semantically valid access is still needed.
- If a business/process need disappears, associated software/interactions/access may cease to be justified even when technical configuration remains valid.
- Business-driven rationalization is distinct from technical policy optimization that preserves effective access.
- A desired end-to-end capability is to explain why network access exists and connect technical enforcement back to the need that caused it.

## Application communication evidence

- An Application is intended as a reusable description of application communication structure and may be deployed more than once.
- A Component describes a participant/role in an application's network data exchange rather than a network device.
- A Deployment is a concrete deployment of a concrete Component of a concrete Application; the deployment unit is the Component.
- An Interaction describes directed communication between source and destination Components and carries required network semantics such as protocol and ports.
- The same Component pair may have several distinct Interactions for independently meaningful communication reasons.
- Interaction granularity is semantic rather than inferred from addresses/ports. One Interaction represents one independently meaningful reason and contains the complete minimal traffic set for that reason.
- Traffic subsets requiring independent applicability/authorization/lifecycle should be separate Interactions rather than bundled solely by technical endpoints.
- Interaction purpose/description is useful; no classification taxonomy is required without a concrete use case.
- Application communication meaning and technical network realization are separate; current IP address realization must not define Deployment identity.
- For the then-current MVP evidence, a Deployment is associated with a Resource rather than an individual Resource endpoint.
- For the then-current MVP evidence, authorized interaction realization considers all current endpoints of the Resource associated with each Deployment; later network-placement scoping may reduce irrelevant technical combinations.

## Resource evidence

- Resource is a human-recognizable logical unit connecting network addressing to a real-world object relevant to access management; detailed physical inventory is not required.
- A Resource may represent one logical network object or a homogeneous address/device group managed as one access unit.
- Resource identity must not depend on current IP address.
- A logical Resource endpoint/presence retains identity when its current address changes.
- Resource and endpoint may exist before any address is known; logical creation and address assignment are separate operations.
- The then-current MVP evidence required at most one current address realization per endpoint; simultaneous active addresses were deferred.
- Address realization may be one host or a subnet/prefix when individual devices are intentionally indistinguishable for access management.
- One Resource may have several endpoints only while they remain one logical access-management unit sharing significant Resource-level attributes; otherwise separate Resources are expected.
- The minimum then-current responsibility/location evidence included Site, Owner and Administrator; speculative unused classifiers were rejected.
- Site is reusable and stably identifiable across Resources.
- Owner is the organizational group owning the Resource; Administrator is the group technically operating it. They are distinct.
- Owner and Administrator are groups/teams rather than direct person references.
- Asset ownership/technical administration does not imply security/governance authority.
- Basic history is required for changing Resource/network-realization facts; no particular temporal storage mechanism is implied.
- Resource addressing represents the corporate address space relevant to access management; hidden local addresses behind translation are not necessarily the catalogue truth.
- Translation calculation/rules are outside the Resource description responsibility; the product receives the already meaningful corporate address/prefix.

## Realization/evidence observations

- Users may want an access audit, source-destination/service accessibility check, semantic required-versus-realized difference, or proposed correction.
- Semantic difference is independently useful without remediation.
- Semantic correctness of effective access differs from structural/configuration optimality.
- Raw rule comparison is insufficient when ordering, deny behavior, groups/objects, defaults or similar constructs affect effective behavior.
- Real network path is not assumed known; candidate relevant enforcement locations may be inferred from available evidence.
- Device/evidence acquisition may have per-source polling/timeout characteristics and administratively controlled active/inactive state.

## Candidate journeys — evidence only, not accepted requirements

- Describe an application, its resources/components and the network interactions those components require.
- Start from a required source-destination/service interaction, identify candidate enforcement locations, and inspect realization.
- Audit configured access and obtain missing/excess effective access.
- Obtain a semantic difference for analysis/reporting without remediation.
- Prepare and hand off a recommended correction after a discrepancy.
- Design, verify, render and operationally apply a correction.
- Start from observed traffic/access and trace upward to application/component interaction and organizational purpose.
- Start from a retired/changed organizational need and trace downward to access/enforcement that may no longer be justified.

## Explicit non-inferences

- Evidence terms are not automatically accepted entities, aggregates or bounded contexts.
- process -> software -> interaction -> access is not automatically the final mandatory hierarchy.
- Candidate capabilities do not imply domain ownership boundaries.
- Exact propagation of business criticality is unresolved.
- Traffic attribution is not assumed exact.
- Recommendation handoff does not imply an approval workflow.
- Resource Owner/Administrator does not imply person identity or security authorization.
- No particular persistence/computation boundary follows from user-facing scope.

## Source-level unknowns

- authoritative source/lifecycle for organizational process/need descriptions;
- whether process/application/component relationships are entered, imported, inferred or combined;
- how semantic authorized access is translated into current technical traffic pairs;
- whether application/component interaction is the stable user abstraction or an intermediate one;
- representation of ambiguous reverse attribution;
- which business attributes materially affect impact/cleanup decisions;
- exact history semantics beyond the accepted need for basic history;
- whether future scenarios need finer deployment-to-endpoint association.
