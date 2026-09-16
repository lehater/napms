# NAPMS strategic DDD — full-width candidate

Status: CANDIDATE / non-canonical / strategic S2 reconstruction from accepted `docs/**`.

## Strategic principle

A capability is not automatically a Bounded Context, service or deployment unit. Peer Bounded Contexts exist where the documentation establishes independent semantic ownership and lifecycle. Cross-context derivations, read models, acquisition and provider adapters remain compositions/integration capabilities unless a distinct authoritative model is accepted.

## Peer Bounded Contexts

| Bounded Context | Core question | Authoritative semantic ownership |
|---|---|---|
| Business Connectivity | Why is application connectivity needed? | Business Process, Connectivity Need, business attribution/current justification |
| Access Policy | What concrete access is proposed, formally decided and currently effective? | PolicyRule identity/lifecycle, RuleChange history/outcome, effective revision, withdrawal |
| Authority Management | Who may perform a protected action for scope/time? | effective actor/action/scope authority |
| Resource Catalogue | What access-domain Resources exist and how are they realized/responsible? | Resource identity/lifecycle, effective AddressSpace, scope affiliation, responsibility |
| Application Communication Catalogue | What applications/components exist and how may Components communicate? | Application, Component, Interaction, immutable InteractionContractRevision traffic meaning |
| Application Deployment | Which concrete Component instances are deployed on which Resources? | ComponentDeployment identity/lifecycle and ComponentRef -> ResourceRef truth |
| Network Enforcement Placement | Where may a technical pair be enforced? | candidate enforcement target/policy-locator relevance |
| Technical Access Evidence | What source-qualified technical material was observed/reported/imported? | normalized immutable technical evidence and provenance |
| Access Policy Realization | How does configured effective access compare with required effective access? | source-neutral assessment/delta, verified additive change intent and verification meaning |
| Network Environment Operations | How is a verified target mutation executed and explained? | controlled mutation identity, authority, preconditions, outcome/provenance |

## Non-peer compositions and integration capabilities

### Required Policy Materialization

Composition over Access Policy + ACC + Application Deployment + Resource Catalogue + Network Enforcement Placement. It derives complete `TargetRequiredPolicy` or unresolved. It owns no upstream policy/catalogue truth.

### Evidence Access Recognition

Composition over Technical Access Evidence + Resource Catalogue + Application Deployment + ACC. It derives `RecognizedAccessCandidate | unresolved/ambiguous`; Access Policy remains the owner of formal submission/decision/current access.

### Provider Policy Interpreter

Integration capability that translates trustworthy provider/configured material into a source-neutral configured-effective policy snapshot. It is not a peer domain owner.

### Provider Policy Renderer

Integration capability that translates verified source-neutral change intent into provider-specific representation while preserving semantics.

### Technical Evidence Acquisition / Collectors

Application/integration capabilities that acquire device/config/flow/import material and faithfully translate it into the TAE contract. Scheduling/credentials/retries/transport are not TAE domain semantics.

### Scoped Connectivity Inventory

Owner-preserving read composition. It does not become a peer BC merely because it provides a product workspace/view.

### Connectivity Impact Analysis

Cross-context analysis capability. It derives impact from authoritative facts without owning those facts.

## Core semantic distinctions

```text
Observed != Recognized != Needed != Proposed != Accepted != Materialized != Realized != Executed != Verified
```

These are distinct states of knowledge/intent/outcome, not one mandatory linear workflow.

Brownfield evidence may be Recognized before business attribution. Deliberate policy submission requires its accepted business basis. Accepted policy is not the same as materialized technical policy. Successful execution is not final convergence verification.

## Context relationships

```text
ACC --ComponentRef--> Application Deployment
RC  --ResourceRef----> Application Deployment
ACC --InteractionRef-> Business Connectivity

Business Connectivity --Need/business basis-----------------> Access Policy
ACC ------------------InteractionContractRevisionRef--------> Access Policy
Application Deployment --ComponentDeploymentRef-------------> Access Policy
Authority Management --protected-action admission-----------> Access Policy

Access Policy --------current effective PolicyRule----------> Required Policy Materialization
ACC ---------------------------------------------------------> Required Policy Materialization
Application Deployment -------------------------------------> Required Policy Materialization
Resource Catalogue -----------------------------------------> Required Policy Materialization
Network Enforcement Placement ------------------------------> Required Policy Materialization
Required Policy Materialization --TargetRequiredPolicy------> Access Policy Realization

Technical Access Evidence --> Evidence Access Recognition
Resource Catalogue --------> Evidence Access Recognition
Application Deployment ----> Evidence Access Recognition
ACC -----------------------> Evidence Access Recognition
Evidence Access Recognition --RecognizedAccessCandidate-----> Access Policy

Provider/network environment --> Provider Policy Interpreter --> Access Policy Realization
Access Policy Realization --> Provider Policy Renderer --> Network Environment Operations
Authority Management --mutation authority-------------------> Network Environment Operations
Network Environment Operations --> provider/network environment
provider/external technical sources --> acquisition --> Technical Access Evidence
```

Arrows denote semantic contracts/data flow, not deployment topology. No Shared Kernel is accepted between target peer BCs.

## Strategic ownership decisions

### Business Connectivity

Owns the application-semantic reason for connectivity. `ConnectivityNeed` may survive deployment/revision changes and never implies authorization. Evidence recognition may precede Need attribution but cannot bypass the deliberate-submission business basis.

### Application Communication Catalogue

Owns reusable application communication meaning. An Interaction is a stable directed Component pair within one Application; traffic changes create immutable revisions. ACC owns neither concrete deployment nor Resource realization.

### Application Deployment

Owns one concrete deployed Component instance:

```text
ComponentDeployment
  ComponentDeploymentId
  ComponentRef
  ResourceRef
```

A deployment references exactly one Component and one Resource. Replicas are independent deployments. Address changes do not change deployment identity.

### Resource Catalogue

Owns stable Resource identity and temporal realization/responsibility facts. Current MVP realization is:

```text
Resource -> effective AddressSpace [0..1]
AddressSpace = HostAddress | Prefix
```

Multiple simultaneous addresses/interfaces/VIPs are an extension, not current target truth. Scope affiliation/responsibility do not themselves grant actor authority.

### Access Policy

Owns one coherent concrete rule lifecycle. The directed source/destination ComponentDeployment pair is the Rule subject; exact revision is proposed/current traffic semantics rather than Rule identity. RuleChange formal outcome is Pending/Accepted/Rejected; accepted changes may advance current semantics; withdrawal clears effectiveness without deleting history.

`Access Governance` is not a target peer BC. Customer-specific approval workflow can integrate around the formal outcome without duplicating current policy ownership.

### Authority Management

Owns effective action admission, not policy approval workflow, business need, catalogue responsibility or policy lifecycle. Denied/Unknown is fail-closed where an action is protected.

### Technical Access Evidence

Owns normalized immutable source-qualified evidence. It does not own acquisition transport, catalogue correlation, desired policy or network mutation.

### Network Enforcement Placement

Owns relevance of enforcement targets/policy locators for a technical pair, not proven end-to-end routing. Multiple candidates remain possible. Prefix-aware matching is an extension.

### Access Policy Realization

Owns source-neutral required-vs-configured comparison and verified additive remediation semantics. `common`, `missing`, `excess` remain explicit. Excess does not create automatic removal authority in the current MVP.

### Network Environment Operations

Owns controlled mutation lifecycle and outcome/provenance. It does not own desired policy, rendering semantics or final convergence truth.

## Strategic invariants

- each authoritative semantic fact/decision has one owner;
- cross-context references are opaque semantic references, not persistence foreign keys;
- compositions derive values but do not acquire authoritative ownership merely by orchestration;
- current effective truth is distinct from proposals, rejected history, observations, rendered artifacts, execution and later verification;
- evidence cannot manufacture desired policy or authorization;
- missing/ambiguous input never silently becomes absence, denial, empty required policy or success;
- provider-native semantics stay at integration boundaries;
- Application communication meaning, concrete deployment and Resource realization are three separate ownership concerns;
- Resource responsibility/scope and actor authority are separate concerns;
- Access Policy is the single owner of proposed changes, formal decisions and current concrete policy lifecycle;
- no Shared Kernel is accepted among target peer contexts.

## Full-width extension map

The following documented extensions remain within the project problem landscape but do not create new peer BCs by default:

- richer Business Process/Need lifecycle;
- concurrent pending policy-change conflict/ordering;
- external/customer-specific approval workflows and responsibility-derived routing;
- richer authority models (nested groups, inheritance, deny/ABAC/quorum);
- richer deployment/runtime identity/history and Resource-sharing restrictions;
- richer ACC publication/version UX;
- multiple simultaneous Resource addresses/interfaces/VIPs and endpoint-purpose semantics;
- Prefix-aware enforcement placement;
- additional evidence collectors/source contracts;
- managed-policy narrowing/removal;
- additional provider interpreters/renderers and operational realization;
- authoritative enterprise identity/source integrations.

If a future use case gives one of these extensions an independent authoritative model/lifecycle, strategic DDD must be reopened rather than pre-creating a Bounded Context now.

## Strategic S2 result

The accepted `docs/**` material can be reconstructed into the ten peer Bounded Contexts plus the listed non-peer compositions/integration capabilities without assigning duplicate semantic ownership. Future/deferred material is preserved explicitly as extension scope rather than silently discarded or promoted to MVP behavior.
