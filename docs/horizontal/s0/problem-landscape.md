# NAPMS problem landscape

Status: CANDIDATE / non-canonical / full-width S0 reconstruction from `docs/**`.

## Problem statement

Enterprise application connectivity is described across business intent, application communication meaning, concrete deployments, network-address realization, current technical evidence, access decisions, enforcement placement, configured policy and network mutation. These truths have different owners and different rates of change.

The system must make access explainable and controllable without collapsing those distinct truths into one inventory, one approval record or one provider-specific configuration model. Missing or ambiguous information must remain visible rather than being silently interpreted as absence, denial, empty required policy or successful convergence.

The documented problem therefore spans the complete path from understanding why connectivity is needed, through deciding what access should be effective, to understanding what is technically present and safely changing network environments when required.

## Desired outcomes

A competent operator/product consumer must be able to:

- identify applications, components, concrete deployments and resources without conflating their identities;
- describe reusable application communication semantics independently from deployment placement;
- record why connectivity is needed and preserve business attribution;
- propose, formally decide, withdraw and explain concrete access policy while preserving history;
- determine who may perform protected actions without turning authority into business ownership or approval workflow;
- resolve resources to current technical address space while preserving uncertainty and history;
- understand where access may be enforced without claiming unproven routing certainty;
- preserve normalized, source-qualified technical evidence independently from desired policy;
- recognize possible application access from technical evidence without manufacturing authorization;
- derive complete required policy from accepted business/policy/catalogue truth or explicitly report unresolved inputs;
- compare required access with trustworthy configured-effective policy;
- render verified source-neutral change intent into provider representation without semantic loss;
- execute controlled network mutations with authority, preconditions, outcome and provenance;
- verify convergence separately from execution success;
- inspect useful cross-context inventory/impact views without transferring semantic ownership into the view.

## Actors and external participants

The current documentation implies these actor classes without requiring them to be domain entities in every context:

- catalogue curators maintaining application/resource/deployment truth;
- business/application stakeholders describing processes and connectivity needs;
- authorized policy actors proposing, deciding or withdrawing access changes;
- security/network operators investigating technical access and policy state;
- network operators executing controlled mutations;
- product users consuming inventories, explanations, comparisons and exports;
- external authority/identity systems supplying actor and authority facts;
- network devices/providers and technical evidence sources;
- external customer-specific governance/workflow systems that may reach approval decisions outside baseline NAPMS semantics.

## Problem areas

### Business intent and attribution

Connectivity may be deliberately requested from a Process-backed Need, while brownfield technical traffic may be recognized before business attribution exists. Recognition must not fabricate the missing business justification or authorization.

### Application communication meaning

Applications contain Components whose reusable directed communication semantics must be expressible independently from concrete runtime placement. Traffic semantics evolve while historical revisions remain interpretable.

### Concrete deployment truth

The same Component may have several independently governed deployed instances. The system needs exact Component-on-Resource identity so policy can refer to concrete endpoints without treating deployment placement as part of application-definition ownership.

### Resource realization and responsibility

Resources require stable identity independent from changing address realization, scope affiliation and responsibility. For the current MVP a Resource has at most one effective AddressSpace at a logical time, exactly HostAddress or Prefix when resolved. Multiple simultaneous addresses/interfaces/VIPs are a documented future extension, not current MVP truth.

### Access policy lifecycle

Proposed changes, formal Accepted/Rejected outcomes, current effective access, withdrawal and history must remain coherent under one policy lifecycle. Pending or rejected proposals must not overwrite effective policy, and historical acceptance must not silently reactivate withdrawn access.

### Action authority versus approval procedure

The system must fail closed for protected actions when authority is denied or unknown. Authority admission is distinct from how an organization decides whether a policy change should be accepted. Bilateral approval, quorum, CAB/ticket stages and responsibility-derived approver routing are documented future/customer-specific extensions rather than baseline approval semantics.

### Technical evidence and recognition

Observed/imported technical material must preserve source, time, provenance, completeness and uncertainty. Evidence may be correlated to catalogue truth to recognize candidate access, but evidence alone cannot create resources, deployments, desired policy or authorization.

### Required policy materialization

Current effective policy must be resolvable through immutable communication semantics, concrete deployments, Resource AddressSpace and enforcement-placement relevance. Missing inputs are unresolved rather than an empty policy. Prefix support may remain unresolved at provider/placement edges that only support host-to-host semantics.

### Enforcement placement

The system needs candidate network enforcement locations/policy locators while preserving the distinction between relevance and proven routing. Multiple candidates may be valid and must not be collapsed without accepted evidence.

### Realization and reconciliation

Required policy and configured-effective policy must be compared in source-neutral semantics. Missing required access drives additive remediation in the MVP; excess configured access is report/audit evidence and is not automatically removed.

### Provider interpretation and rendering

Provider-native configuration must remain at integration boundaries. Configured-policy interpretation must publish trustworthy normalized semantics; rendering must preserve the verified change intent's meaning.

### Controlled network mutation

Execution requires explicit mutation identity, authority, preconditions, outcome and provenance. Successful apply does not itself prove semantic convergence; later observation/interpretation/comparison is required.

### Cross-context views and analysis

Resource-centric connectivity inventory and connectivity impact analysis are useful product capabilities but do not become semantic owners merely by composing data from authoritative contexts.

## Documented future/deferred problem space

The accepted documentation also preserves future problems that are not baseline MVP behavior:

- richer Business Process lifecycle, criticality and duplicate-Need semantics;
- several simultaneous pending policy changes and ordering/conflict semantics;
- customer-specific bilateral/quorum/staged approval workflow integrations;
- nested groups, role inheritance, deny/ABAC/quorum authority models;
- richer deployment/runtime/container history and possible restrictions on Resource sharing;
- richer ACC draft/publish/version presentation;
- multiple simultaneous Resource addresses/interfaces/VIPs and endpoint-purpose semantics;
- Prefix-aware enforcement placement/matching;
- richer technical evidence acquisition/provider source contracts;
- managed-policy narrowing/removal semantics rather than additive-only remediation;
- richer provider/device realization details and operational workflows;
- authoritative enterprise identity/source integrations.

These are retained as explicit problem-space extensions. They are not automatically current functional requirements or new Bounded Contexts.

## S0 guardrail

Solution structures found in legacy requirements, architecture, domain or engineering documents are evidence of the documented problem but do not become S0 constraints merely because the existing design uses them. Only explicitly externally imposed or non-negotiable constraints qualify as S0 constraints; none are inferred here without such documentation.
