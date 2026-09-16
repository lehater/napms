# NAPMS full-width capability requirements

Status: CANDIDATE / non-canonical / S1 reconstruction from accepted `docs/**`.

Requirements are grouped by observable product capability rather than by Bounded Context. Strategic ownership is assigned separately in S2.

Disposition markers:
- `CURRENT` — accepted current target/as-built behavior required to reconstruct the designed system;
- `EXTENSION` — documented future/deferred behavior/problem that is retained but is not baseline MVP behavior.

## Business intent and connectivity need

- **REQ-BC-001 CURRENT** — users can represent business processes and connectivity needs so deliberate access changes have an explicit business basis.
- **REQ-BC-002 CURRENT** — a connectivity need can remain stable across concrete deployment or communication-revision changes and does not itself grant access.
- **REQ-BC-003 CURRENT** — evidence-derived connectivity may be recognized before Process/Need attribution, but deliberate policy submission requires the documented business basis.
- **REQ-BC-101 EXTENSION** — richer process lifecycle/criticality and duplicate-need behavior may be introduced without redefining current policy ownership.

## Application communication catalogue

- **REQ-ACC-001 CURRENT** — users can maintain Application and Component identities and reusable directed Component-to-Component communication definitions.
- **REQ-ACC-002 CURRENT** — an Interaction is intra-Application; cross-Application Interaction is rejected.
- **REQ-ACC-003 CURRENT** — traffic semantics are preserved as immutable InteractionContractRevision values; changing traffic creates a new revision while stable Interaction identity and old revisions remain resolvable.
- **REQ-ACC-004 CURRENT** — an exact revision determines its owning Interaction, endpoint Components and complete traffic alternatives without requiring duplicate semantic references.
- **REQ-ACC-005 CURRENT** — ACC communication semantics are defined at Component level; concrete ComponentDeployment selection is not part of ACC Interaction ownership.
- **REQ-ACC-101 EXTENSION** — richer draft/publish/version presentation may be added without changing immutable revision semantics.

## Concrete application deployment

- **REQ-AD-001 CURRENT** — users can represent one concrete deployed Component instance as an identity referencing exactly one Component and one Resource.
- **REQ-AD-002 CURRENT** — deploying the same Component on another Resource creates another independently governed deployment identity.
- **REQ-AD-003 CURRENT** — Resource address changes do not change deployment identity; Resource replacement creates a different deployment instance.
- **REQ-AD-004 CURRENT** — deployment truth supplies the ComponentRef/ResourceRef facts used to validate whether a concrete deployment pair is compatible with an ACC Interaction revision; AD does not decide whether that pair is authorized for access.
- **REQ-AD-101 EXTENSION** — richer runtime/container/deployment history and product restrictions on Resource sharing may be introduced when use cases require them.

## Resource catalogue

- **REQ-RC-001 CURRENT** — users can maintain stable Resource identity independently from realization, scope affiliation, responsibility and retirement.
- **REQ-RC-002 CURRENT** — at a logical time a Resource resolves to at most one effective AddressSpace; when present it is exactly HostAddress or Prefix.
- **REQ-RC-003 CURRENT** — missing Resource realization remains explicitly unresolved rather than being treated as empty access.
- **REQ-RC-004 CURRENT** — address realization, scope affiliation and responsibility preserve temporal history/provenance.
- **REQ-RC-005 CURRENT** — scope affiliation and responsibility do not themselves grant actor authority.
- **REQ-RC-101 EXTENSION** — multiple simultaneous addresses/interfaces/VIPs, endpoint purpose and richer exposure semantics may be introduced when a use case requires them.

## Access policy lifecycle

- **REQ-AP-001 CURRENT** — users can maintain a stable concrete access rule for one directed source/destination ComponentDeployment pair.
- **REQ-AP-002 CURRENT** — a PolicyRule/RuleChange identifies one exact ACC InteractionContractRevision plus one concrete source/destination ComponentDeployment pair; AP validates that each deployment's ComponentRef matches the corresponding endpoint ComponentRef of the revision's Interaction.
- **REQ-AP-003 CURRENT** — users can propose changes to the rule's exact communication revision and record one formal Pending, Accepted or Rejected outcome with actor/time/provenance.
- **REQ-AP-004 CURRENT** — pending/rejected changes never overwrite current effective policy; an applicable accepted change may advance the effective revision.
- **REQ-AP-005 CURRENT** — users can explicitly withdraw effective access without deleting decision/change history; historical acceptance does not silently reactivate withdrawn access.
- **REQ-AP-006 CURRENT** — deliberate change submission preserves its Process-backed Need/business basis; evidence-derived candidates cannot bypass the business-basis requirement for formal submission.
- **REQ-AP-007 CURRENT** — exact InteractionContractRevision is sufficient to resolve the owning Interaction; PolicyRule does not need a duplicate InteractionRef merely to restate that identity.
- **REQ-AP-101 EXTENSION** — multiple simultaneous pending changes and ordering/conflict semantics may be introduced later.
- **REQ-AP-102 EXTENSION** — customer-specific bilateral/quorum/CAB/ticket approval procedures may integrate while preserving the core formal outcome model.

## Protected-action authority

- **REQ-AM-001 CURRENT** — protected actions are admitted against authenticated actor, action, scope and effective time.
- **REQ-AM-002 CURRENT** — denied or unknown authority fails closed.
- **REQ-AM-003 CURRENT** — authority admission does not imply business ownership, resource responsibility or a particular policy approval procedure.
- **REQ-AM-101 EXTENSION** — nested groups, role inheritance, deny/ABAC/quorum and richer authority models may be introduced later.

## Technical access evidence and recognition

- **REQ-TAE-001 CURRENT** — technical observations/imports are preserved as normalized immutable source-qualified evidence with time/provenance/completeness semantics.
- **REQ-TAE-002 CURRENT** — acquisition scheduling, credentials, retry and source transport do not redefine evidence meaning.
- **REQ-EAR-001 CURRENT** — technical evidence can be correlated with Resource, deployment and application communication truth to produce a recognized access candidate or an explicit unresolved/ambiguous result.
- **REQ-EAR-002 CURRENT** — recognition cannot manufacture catalogue identities, business need, desired policy or authorization.
- **REQ-TAE-101 EXTENSION** — additional collectors/import sources and richer source contracts may be added while preserving normalized evidence ownership.

## Required policy materialization

- **REQ-RPM-001 CURRENT** — current effective access can be materialized by combining exact accepted policy, immutable communication semantics, concrete source/destination deployments, Resource realization and applicable enforcement-placement relevance.
- **REQ-RPM-002 CURRENT** — each effective rule already identifies one concrete deployment pair; materialization does not perform replica/placement Cartesian expansion.
- **REQ-RPM-003 CURRENT** — missing/incomplete deployment, address, target or locator information produces an explicit unresolved result, never empty required policy.
- **REQ-RPM-004 CURRENT** — Prefix remains first-class upstream truth even when a downstream enforcement edge supports HostAddress only.

## Network enforcement placement

- **REQ-NEP-001 CURRENT** — users/system can determine zero, one or many candidate enforcement locations/policy locators relevant to a technical traffic pair.
- **REQ-NEP-002 CURRENT** — candidate relevance is not presented as proven routing certainty and multiple candidates remain visible.
- **REQ-NEP-003 CURRENT** — unsupported Prefix matching produces unresolved placement rather than expansion/fabrication.
- **REQ-NEP-101 EXTENSION** — Prefix-aware placement semantics may be introduced when accepted.

## Policy realization/reconciliation

- **REQ-APR-001 CURRENT** — required and configured-effective policy are compared in source-neutral semantics as common, missing and excess access.
- **REQ-APR-002 CURRENT** — incomplete/untrustworthy configured or required inputs do not silently become an empty comparison.
- **REQ-APR-003 CURRENT** — MVP remediation intent is additive for missing required access; excess configured access remains report/audit evidence rather than automatic removal authority.
- **REQ-APR-004 CURRENT** — verification/convergence is distinguishable from mutation execution success.
- **REQ-APR-101 EXTENSION** — managed narrowing/removal semantics may be introduced under an explicit future safety/ownership contract.

## Provider interpretation and rendering

- **REQ-PPI-001 CURRENT** — provider-native configured material is interpreted into a trustworthy normalized configured-effective policy snapshot with explicit scope/completeness/freshness/unsupported semantics.
- **REQ-PPR-001 CURRENT** — verified source-neutral change intent can be rendered into provider-specific representation without semantic loss.
- **REQ-PROVIDER-101 EXTENSION** — additional provider/device realization details may be added behind these integration boundaries.

## Controlled network operations

- **REQ-NEO-001 CURRENT** — network mutations are executed as controlled operations with explicit identity, authority, preconditions, outcome and provenance.
- **REQ-NEO-002 CURRENT** — failed/unknown execution remains distinguishable from success.
- **REQ-NEO-003 CURRENT** — execution success is not reported as final semantic convergence without later verification evidence.

## Cross-context views and analysis

- **REQ-VIEW-001 CURRENT** — users can consume resource-centric scoped connectivity inventory/read compositions without the view becoming an authoritative owner of underlying facts.
- **REQ-VIEW-002 CURRENT** — connectivity impact analysis may compose authoritative facts across contexts while preserving source ownership and uncertainty.

## Enterprise authoritative-source integration

- **REQ-ID-001 CURRENT** — where enterprise identities/authoritative facts are integrated, their source authority and correlation boundary remain explicit rather than silently becoming locally authored truth.
- **REQ-ID-101 EXTENSION** — additional authoritative enterprise source integrations may be introduced under explicit source contracts.

## Cross-cutting quality requirements

- **QREQ-001 CURRENT** — fail closed on missing/ambiguous authority, identity correlation or required semantic inputs where proceeding would fabricate access truth.
- **QREQ-002 CURRENT** — preserve provenance, temporal meaning and historical identities required for explanation/reconstruction.
- **QREQ-003 CURRENT** — preserve semantic ownership across compositions; a view/orchestrator/integration does not become authoritative merely by consuming data.
- **QREQ-004 CURRENT** — provider-specific semantics remain isolated at integration boundaries and do not leak into core source-neutral policy meaning.
- **QREQ-005 CURRENT** — current effective truth remains distinguishable from proposed, historical, observed and executed truth.
- **QREQ-006 CURRENT** — designed current as-built and target behavior remains reconstructible from documentation without requiring implementation inspection.
