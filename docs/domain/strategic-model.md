# NAPMS Strategic DDD model

Status: `S2 affected strategic boundaries converged 2026-09-16; dependent Tactical DDD pending revalidation`.

Canonical relationship map: `context-map.md`.
Machine projection: `strategic-model.json`.
DDD convergence checkpoint: `mvp-ddd-convergence-checkpoint.md`.

## Current target Bounded Contexts

| Bounded Context | Semantic center | Responsibility |
|---|---|---|
| **Business Connectivity** | why is application connectivity needed? | Business Process, Connectivity Need, attribution/current justification |
| **Access Policy** | what concrete access is proposed, governed and currently effective? | Policy Rule identity/lifecycle, rule-change proposals/decisions/provenance, bilateral approval obligations, current effective revision/withdrawal |
| **Authority Management** | who may perform a domain action for scope/time? | effective actor/action/scope authority and membership/role/scope assignment semantics |
| **Resource Catalogue** | what access-domain resources exist and how are they realized? | Resource identity/lifecycle, effective HostAddress-or-Prefix realization, scope affiliation/responsibility |
| **Application Communication Catalogue** | what applications/components exist and how may components communicate? | Application/Component/Interaction identity and immutable InteractionContractRevision traffic meaning |
| **Application Deployment** | which concrete Component instances are deployed on which Resources? | ComponentDeployment identity/lifecycle and exact ComponentRef -> ResourceRef deployment truth |
| **Network Enforcement Placement** | where may a technical pair be enforced? | candidate Firewall/policy-locator relevance |
| **Technical Access Evidence** | what source-qualified technical material was reported/observed/imported? | canonical normalized immutable evidence language plus source/time/provenance |
| **Access Policy Realization** | how does configured effective access compare with required effective access? | source-neutral assessment, semantic delta, accepted additive change design and verification |
| **Network Environment Operations** | how is one verified target mutation executed and explained? | controlled mutation identity, authority, preconditions/concurrency, outcome/provenance |

`Access Governance` is no longer a separate target Bounded Context. Its still-required bilateral proposal/approval/withdrawal semantics belong to the Access Policy lifecycle. This removes duplicate ownership of current authorization while preserving governance history and authority checks.

`Connectivity Requirements`, `Connectivity Decision` and the implemented ACC compatibility deployment model remain legacy/as-built boundaries where documented; they are not target semantic owners.

Provider Policy Interpreter, Provider Policy Renderer and Technical Evidence Acquisition/Collectors are integration/application capabilities. Required Policy Materialization and Evidence Access Recognition are non-peer derived/application compositions, not Bounded Contexts.

## Core semantic distinctions

```text
Observed != Recognized != Needed != Proposed != Authorized != Materialized != Realized != Executed
```

These are meanings, not a mandatory single linear workflow. In particular, brownfield traffic may be Recognized and Proposed before a Business Connectivity Need is known, but deliberate governance submission requires accepted business justification.

Execution success does not imply semantic convergence; convergence is established only by later normalized observation/interpretation and comparison.

## Application communication definition

ACC owns reusable application communication meaning:

```text
Application
  -> Components
  -> directed Interactions between Components of that same Application
       -> immutable InteractionContractRevision[]
```

An Interaction never crosses Application boundaries.

A material traffic change creates a new immutable `InteractionContractRevision` while preserving Interaction identity. Old revisions remain resolvable. A revision reference identifies the exact traffic semantics and, through its owning Interaction, the source/destination Component definitions.

Consumers therefore do not require a duplicate `InteractionRef` merely to interpret an exact revision.

## Concrete Component deployment boundary

Application Deployment owns concrete deployed Component instances:

```text
ComponentDeployment
    ComponentDeploymentId
    ComponentRef
    ResourceRef
```

For the first MVP:

- one Component Deployment represents one Component deployed on exactly one Resource;
- deploying the same Component on a second Resource creates a different Component Deployment;
- several Component Deployments of the same Component may coexist and are independently governed;
- replacing the Resource with a different deployed instance creates a different Component Deployment;
- no whole-Application `ApplicationDeployment` identity is required by target access governance or policy export;
- provider/container/pod/runtime identity remains outside the target unless a later requirement needs it.

Whether several different Component Deployments may share one Resource is deliberately not constrained by the current MVP because current accepted behavior does not depend on that choice.

ACC owns Component meaning. Application Deployment consumes opaque `ComponentRef`. RC owns Resource meaning. Application Deployment consumes opaque `ResourceRef`. No context imports another context's persistence model.

## Resource Catalogue boundary

RC owns:

```text
Resource identity/lifecycle
Resource -> effective AddressSpace [0..1] = HostAddress | Prefix
ResourceScopeAffiliation
ResourceResponsibility
```

AddressSpace is technical realization, not Resource or ComponentDeployment identity. Address changes therefore do not replace either identity.

Multiple simultaneous addresses/interfaces, endpoint purpose, VIPs and deployment-specific exposure remain future extensions; `ResourceEndpoint` is not current target truth.

## Business need versus concrete access lifecycle

Business Connectivity Need remains application-semantic:

```text
ConnectivityNeed
    -> stable ACC InteractionRef
```

It does not identify concrete deployments or authorize access and may survive deployment or traffic-revision changes.

Access Policy operates on one concrete directed deployment pair:

```text
PolicyRule subject
    sourceComponentDeploymentRef
    destinationComponentDeploymentRef

PolicyRule current traffic
    revisionRef
```

The pair identifies the concrete connection. The exact immutable revision is current/proposed traffic semantics for that connection and is not by itself the identity of the connection.

A deliberate governance submission requires a Process-backed Connectivity Need. Evidence-derived recognition may create a candidate/proposal before Process/Need attribution, but cannot make a Rule effective without the normal governance requirements.

## Access Policy lifecycle ownership

Access Policy owns the complete semantic lifecycle of one concrete rule:

- stable Policy Rule identity;
- concrete directed source/destination Component Deployment subject;
- proposed traffic revision changes and their provenance;
- source/destination approval obligations;
- approval/rejection/withdrawal history;
- current effective revision, if any;
- current effective/withdrawn state;
- publication of current effective Policy Rule truth to downstream consumers.

This is one lifecycle owner because an accepted proposal is exactly what changes the current Rule, while a pending/rejected proposal must coexist with and not overwrite the current effective revision.

The former AG -> AP `AuthorizationGranted / AuthorizationWithdrawn` semantic handoff is removed from the target model. It duplicated one authoritative current-access fact across two Bounded Contexts without an independent AP decision.

Historical governance state remains distinct from current effective state **inside** the Access Policy boundary; merging the Bounded Contexts does not permit old approvals to reactivate access or pending changes to replace current policy.

## Approval obligations and authority

Responsibility and authority remain separate truths:

```text
Application Deployment: ComponentDeploymentRef -> ResourceRef
RC: ResourceRef -> ResponsibilityScopeRef affiliation
AM: ActorRef + ActionRef + ResponsibilityScopeRef + effectiveTime -> EffectiveAuthority
Access Policy: correlates those truths into rule-change approval obligations
```

For the first MVP, source and destination obligations are independent and each side must resolve to exactly one distinct applicable Responsibility Scope. Zero or several distinct scopes on either side fail closed.

AM owns actor/action/scope/time authority. Resource owner/admin/contact metadata never grants authority by itself.

Historical decisions preserve the authority evidence/basis valid at decision time. Later role/scope changes do not rewrite history.

A material change of current approval obligations may make current authorization cease to be effective according to Access Policy lifecycle rules; historical approvals alone cannot silently restore it.

## Evidence recognition boundary

TAE owns evidence only. Recording evidence never creates desired policy or authorization.

`TrafficDerived` or other applicable evidence may feed a non-peer **Evidence Access Recognition** composition:

```text
TAE technical predicate
+ RC AddressSpace -> Resource correlation
+ Application Deployment Resource -> ComponentDeployment correlation
+ ACC Component/Interaction/revision semantics
    -> RecognizedAccessCandidate | unresolved
```

When correlation is exact enough, that candidate may initiate the same Access Policy proposal/change lifecycle used by manual creation. Recognition does not gain authority and does not bypass Business Connectivity/approval requirements.

TAE remains unaware of Policy Rule lifecycle and does not own candidate acceptance.

## Required Policy Materialization

Required Policy Materialization remains a derived composition:

```text
Access Policy current effective Policy Rules
+ ACC exact immutable InteractionContractRevision semantics
+ Application Deployment concrete ComponentDeployment -> ResourceRef truth
+ RC ResourceRef -> effective HostAddress | Prefix
+ NEP candidate Firewall / AccessListLocator results
        -> normalized required permit predicates
        -> TargetRequiredPolicy[] | unresolved
        -> APR
```

For one effective Rule there is one source Component Deployment and one destination Component Deployment. Materialization verifies both against the exact revision's endpoint Components, resolves each to its Resource, then resolves each Resource AddressSpace.

The target no longer expands one logical Application deployment into a source-placement × destination-placement Cartesian product. Replicas are independent Component Deployments and require their own effective policy relationships.

Missing/unresolved deployment, Resource realization, candidate target or policy locator is explicit unresolved state and is not an empty required policy.

The first target-specific NEP edge supports only HostAddress-to-HostAddress TrafficPairs. Prefix remains first-class RC truth and fails closed at that edge rather than being expanded into hosts.

## Technical evidence acquisition and configured interpretation

TAE owns canonical normalized immutable source-qualified evidence, not acquisition scheduling or provider interpretation.

```text
device/config acquisition capability ----\
NetFlow/IPFIX/flow collector -------------+--> normalized evidence --> TAE
file/import adapter ----------------------/
```

Provider Policy Interpreter separately interprets provider-native configured semantics into `ConfiguredEffectivePolicySnapshot` for APR. Configured evidence stored by TAE may be one selected input under an explicit source contract.

APR does not parse raw provider syntax.

## Access Policy Realization / execution

APR remains the owner of source-neutral required-vs-configured comparison and accepted additive remediation intent. Provider Policy Renderer owns provider rendering. NEO owns controlled target mutation.

For complete comparable inputs:

```text
common  = required ∩ configured
missing = required - configured
excess  = configured - required
```

MVP remediation remains additive-only on `missing`; `excess` is report/audit evidence without automatic removal authority.

NEO execution success is not final convergence proof; later observation and APR comparison establish convergence.

## Strategic invariants

- each authoritative semantic fact/decision has one explicit owner;
- Access Policy is the single owner of proposal/approval history and current effective Policy Rule truth for a concrete connection;
- current effective policy and pending/rejected change history remain distinct meanings within that lifecycle owner;
- ACC owns reusable Application/Component/Interaction/revision semantics and not deployment placement;
- Application Deployment owns concrete ComponentDeployment identity and ComponentRef -> ResourceRef deployment truth;
- RC owns Resource identity, AddressSpace and responsibility/scope affiliation;
- cross-context references are opaque semantic references, not persistence foreign keys;
- no Shared Kernel is accepted between target Bounded Contexts;
- unknown/incomplete evidence does not silently become absence, denial, empty policy or success;
- evidence alone never manufactures authorization, desired policy or remediation intent;
- workflows/compositions derive values but acquire no business authority merely by orchestrating owners;
- provider-native semantics remain at integration boundaries.

## Explicit non-blocking future extensions

- richer BusinessProcess retirement/criticality/duplicate-Need behavior;
- whether several different Component Deployments may share one Resource;
- ComponentDeployment runtime/container/pod identity and richer lifecycle/history;
- ACC draft/publish/version-presentation workflow beyond immutable revisions;
- generalized approval semantics for several Responsibility Scopes on one side;
- nested groups, role inheritance, explicit deny/ABAC/quorum authority rules;
- Prefix-aware NEP query/matching semantics;
- several simultaneous Resource addresses/interfaces, endpoint purpose, VIP and deployment-specific exposure;
- managed-policy ownership/removal semantics for APR excess;
- richer APR change vocabulary or durable remediation-plan lifecycle;
- concrete acquisition scheduling/polling and provider transport/rollback mechanisms.

These are revisit-triggered extensions, not blockers for the selected first-MVP policy/export behavior.

## S2 strategic disposition

The affected Strategic boundary review converges on:

1. keep ACC, Application Deployment and RC as separate owners, but replace logical whole-Application deployment/placement-set semantics with concrete ComponentDeployment semantics in Application Deployment;
2. absorb Access Governance responsibility into Access Policy because proposal/approval/current-rule semantics form one rule lifecycle and the old split duplicated current authorization truth;
3. keep Business Connectivity and Authority Management separate because their facts/lifecycles remain independently meaningful;
4. keep TAE as evidence-only and introduce evidence recognition only as a non-peer composition feeding the normal Access Policy proposal lifecycle;
5. keep downstream materialization/realization/execution ownership unchanged except for consuming concrete ComponentDeployment references.

Dependent Tactical DDD must now be revalidated before G2 can PASS. No implementation authorization is implied.
