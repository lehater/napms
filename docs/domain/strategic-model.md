# NAPMS Strategic DDD model

Status: `S2 revalidated target baseline accepted; G2 PASS 2026-09-16`.

Canonical relationship map: `context-map.md`.
Machine projection: `strategic-model.json`.
DDD convergence checkpoint: `mvp-ddd-convergence-checkpoint.md`.

## Current target Bounded Contexts

| Bounded Context | Semantic center | Responsibility |
|---|---|---|
| **Business Connectivity** | why is application connectivity needed? | Business Process, Connectivity Need, attribution/current justification |
| **Access Policy** | what concrete access is proposed, governed and currently effective? | Policy Rule identity/lifecycle, RuleChange governance history, current effective revision/withdrawal |
| **Authority Management** | who may perform a protected action for scope/time? | effective actor/action/scope authority |
| **Resource Catalogue** | what access-domain resources exist and how are they realized/responsible? | Resource identity/lifecycle, AddressSpace, scope affiliation/responsibility |
| **Application Communication Catalogue** | what applications/components exist and how may their components communicate? | Application/Component/Interaction identity and immutable InteractionContractRevision traffic meaning |
| **Application Deployment** | which concrete Component instances are deployed on which Resources? | ComponentDeployment identity/lifecycle and exact ComponentRef -> ResourceRef deployment truth |
| **Network Enforcement Placement** | where may a technical pair be enforced? | candidate Firewall/policy-locator relevance |
| **Technical Access Evidence** | what source-qualified technical material was reported/observed/imported? | canonical normalized immutable evidence plus source/time/provenance |
| **Access Policy Realization** | how does configured effective access compare with required effective access? | assessment, semantic delta, accepted additive change design/verification |
| **Network Environment Operations** | how is a verified target mutation executed/explained? | controlled mutation identity, authority, preconditions, outcome/provenance |

`Access Governance` is no longer a separate target Bounded Context. Its bilateral proposal/approval/rejection/withdrawal semantics are part of the Access Policy Rule lifecycle.

`Connectivity Requirements`, `Connectivity Decision`, implemented ACC `ApplicationDeployment`/`DeploymentInteraction` and compatibility `ComponentDeployment` remain as-built/legacy terms only where current reconstruction documentation requires them.

Provider Policy Interpreter, Provider Policy Renderer and Technical Evidence Acquisition/Collectors are integration/application capabilities. Required Policy Materialization and Evidence Access Recognition are non-peer compositions.

## Core distinctions

```text
Observed != Recognized != Needed != Proposed != Authorized != Materialized != Realized != Executed
```

These are semantic distinctions, not one mandatory linear workflow. Brownfield traffic may be Recognized before Process/Need attribution. Deliberate policy-change submission requires accepted business justification.

Execution success is not final convergence proof; later observation/interpretation/comparison establishes convergence.

## ACC — reusable communication definition

```text
Application
  -> Components
  -> Interaction(source Component, destination Component)
      -> immutable InteractionContractRevision[]
```

Strategic invariants:

- both Interaction endpoints belong to the same Application;
- cross-Application Interaction is invalid;
- Interaction is the stable directed Component-pair template;
- traffic changes create a new immutable revision without replacing Interaction identity;
- old revisions remain resolvable;
- an exact revision identifies its owning Interaction, endpoint Components and complete traffic alternatives;
- consumers need no duplicate `InteractionRef` merely to interpret an exact revision.

Changing ACC-current revision does not silently change an existing Policy Rule.

## Application Deployment — concrete deployed Components

```text
ComponentDeployment
    ComponentDeploymentId
    ComponentRef
    ResourceRef
```

For the first MVP:

- one ComponentDeployment is one concrete deployed Component instance;
- it references exactly one Component and one Resource;
- deploying the same Component on another Resource creates another ComponentDeployment;
- several deployments of the same Component may coexist and are independently governed;
- Resource replacement creates a different deployment instance rather than mutating a placement set;
- Resource AddressSpace change does not change ComponentDeployment identity;
- target policy semantics require no whole-Application `ApplicationDeployment` aggregate;
- provider pod/container/process identity is outside current scope.

Whether several different ComponentDeployments may share one Resource is intentionally not constrained by the current MVP.

ACC owns Component meaning; AD consumes opaque `ComponentRef`. RC owns Resource meaning; AD consumes opaque `ResourceRef`.

## Resource Catalogue

RC owns:

```text
Resource identity/lifecycle
Resource -> effective AddressSpace [0..1] = HostAddress | Prefix
ResourceScopeAffiliation
ResourceResponsibility
```

AddressSpace is realization, not Resource or ComponentDeployment identity. Multiple simultaneous interfaces/addresses, endpoint purpose, VIPs and deployment-specific exposure are deferred; `ResourceEndpoint` is not current target truth.

## Business Connectivity versus concrete policy

Business Connectivity Need remains application-semantic:

```text
ConnectivityNeed -> stable InteractionRef
```

A Need may survive one deployment or revision and never implies authorization.

Access Policy operates on one concrete directed pair:

```text
PolicyRule
    PolicyRuleId
    sourceComponentDeploymentRef
    destinationComponentDeploymentRef
    effectiveRevisionRef?
```

The directed deployment pair is the concrete Rule subject/business uniqueness. `revisionRef` is proposed/current traffic semantics rather than Rule identity.

A deliberate RuleChange submission requires a Process-backed Need/business basis. Evidence-derived recognition may produce a candidate before attribution, but cannot make access effective or bypass governance.

## Access Policy — one rule lifecycle owner

Access Policy owns:

- stable PolicyRule identity;
- immutable source/destination ComponentDeployment subject;
- RuleChange attempts and their business/evidence provenance;
- source/destination approval obligations;
- approval/rejection history;
- current effective revision, if any;
- withdrawal/regrant history;
- current effective PolicyRule publication.

This is one lifecycle because an accepted RuleChange is exactly what changes the Rule's current semantics. The former AG `GovernedAuthorization.effectiveGrant` + AP `PolicyRule` split duplicated current authorization truth without an independent AP decision.

Historical and current truth remain distinct inside the BC: pending/rejected changes never overwrite current effective policy, and old approvals never silently reactivate withdrawn access.

`PolicyRuleId` is AP-internal identity; downstream uses opaque `PolicyRuleRef`.

## Approval obligations and authority

```text
AD: ComponentDeploymentRef -> ResourceRef
RC: ResourceRef -> ResponsibilityScopeRef affiliation
AM: ActorRef + ActionRef + ResponsibilityScopeRef + effectiveTime -> EffectiveAuthority
AP: derives RuleChange approval obligations from those public facts
```

The first MVP requires exactly one distinct applicable Responsibility Scope per side. Zero or several on either side fail closed. Source and destination approvals are independent and both are required.

AM owns actor/action/scope/time authority. Resource responsibility/contact metadata never grants authority.

Historical decisions preserve the authority/obligation basis valid when decided. Materially changed obligations may withdraw current effectiveness; historical approvals alone cannot restore it.

## Evidence Access Recognition

TAE owns evidence only. A non-peer recognition composition may correlate:

```text
TAE technical predicate
+ RC AddressSpace -> Resource correlation
+ AD Resource -> ComponentDeployment correlation
+ ACC Component/Interaction/revision semantics
-> RecognizedAccessCandidate | unresolved
```

A candidate may carry:

```text
sourceComponentDeploymentRef
destinationComponentDeploymentRef
revisionRef
evidenceProvenance
```

into the same Access Policy proposal path as manual creation.

Ambiguous/missing correlation fails closed. Recognition owns no Resource, deployment, application, business Need or policy truth.

## Required Policy Materialization

```text
AP current effective PolicyRule
+ ACC exact immutable revision semantics
+ AD source/destination ComponentDeployment -> ResourceRef
+ RC Resource -> AddressSpace
+ NEP candidate target/policy locators
-> TargetRequiredPolicy[] | unresolved
-> APR
```

Each effective Rule already identifies one concrete source and destination deployment. RPM verifies those deployment Components against the revision endpoints and resolves exactly one Resource per endpoint. It does not perform replica/placement Cartesian expansion.

Independent replicas require independent effective Policy Rules.

Missing deployment, address, target or locator is `unresolved`, never empty policy.

The first target-specific NEP edge supports HostAddress-to-HostAddress only; Prefix remains first-class upstream truth and yields unresolved at that edge.

## Evidence acquisition / configured interpretation

TAE owns normalized immutable source-qualified evidence, not collection scheduling or configured-policy interpretation.

```text
device/config/flow acquisition -> TAE
file/import acquisition        -> TAE
```

Provider Policy Interpreter separately derives trustworthy `ConfiguredEffectivePolicySnapshot` semantics for APR. Configured TAE evidence may be an input only under an explicit source contract.

## APR / renderer / NEO

APR owns source-neutral required-vs-configured assessment and accepted additive change intent:

```text
common  = required ∩ configured
missing = required - configured
excess  = configured - required
```

MVP remediation is additive-only on `missing`; `excess` is report/audit evidence without automatic removal authority.

Provider Policy Renderer owns provider representation and must preserve semantic equivalence. NEO owns controlled mutation. Immediate apply/verification is not final semantic convergence.

## Strategic invariants

- each authoritative semantic fact/decision has one owner;
- Access Policy is the single owner of proposal/approval/current PolicyRule lifecycle;
- current effective policy and pending/rejected history remain distinct;
- ACC owns reusable application communication meaning, not deployment;
- AD owns concrete ComponentDeployment identity/Resource relation, not Resource realization;
- RC owns Resource/address/scope/responsibility truth, not policy;
- cross-context references are opaque semantic references, not persistence foreign keys;
- no Shared Kernel is accepted between target BCs;
- unknown/incomplete evidence never silently becomes absence, denial, empty policy or success;
- evidence alone never manufactures authorization, desired policy or remediation intent;
- compositions derive values but gain no authoritative ownership merely by orchestrating contexts;
- provider-native semantics remain at integration boundaries.

## Explicit non-blocking extensions

- richer BusinessProcess lifecycle/criticality/duplicate-Need behavior;
- several simultaneous Pending RuleChanges and conflict ordering;
- generalized multi-scope approval algebra;
- nested groups, role inheritance, deny/ABAC/quorum authority;
- whether several ComponentDeployments may share one Resource as a product restriction;
- provider runtime identity and richer ComponentDeployment history;
- ACC draft/publish/version presentation;
- Prefix-aware NEP matching;
- several simultaneous Resource addresses/interfaces/VIPs;
- managed-policy removal/narrowing semantics;
- concrete persistence/API/transport/package realization.

## S2 disposition

Strategic and dependent Tactical DDD are mutually coherent for the selected first-MVP slice. Formal result: `G2 PASS` in `mvp-ddd-convergence-checkpoint.md`.

No implementation authorization is implied. S3 Architecture may now rely on this target baseline.
