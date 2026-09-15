# NAPMS Strategic DDD model

Status: `S2 affected-edge convergence: Application Deployment boundary accepted; AG behavior questions remain S1-open`.

Source baseline: DDD-BDM-010, 2026-09-14 G1 revalidation, ADR-019/020/021, global Strategic convergence pass, and the 2026-09-15 Application Deployment Boundary Challenge.

This document defines model/language/responsibility boundaries. It does not define services, databases, teams or deployment units. Canonical relationship map: `context-map.md`.

## Current target Bounded Contexts

| Bounded Context | Semantic center | Responsibility |
|---|---|---|
| **Business Connectivity** | why is application connectivity needed? | Business Process, Connectivity Need, attribution/justification |
| **Access Governance** | has a governed interaction received and retained required consent? | Request history, bilateral consent, grant/withdrawal provenance |
| **Access Policy** | what semantic network access is currently authorized? | authoritative Policy Rule truth and effective authorization projection |
| **Authority Management** | who may perform a domain action for scope/time? | effective actor/action/scope authority and assignment semantics |
| **Resource Catalogue** | what access-domain resources exist and how are they realized? | Resource identity/lifecycle, technical realization, scope affiliation and responsibility |
| **Application Communication Catalogue** | what applications/components exist and how may components communicate? | Application/Component/Interaction identity and immutable interaction traffic contract |
| **Application Deployment** | where are logical application deployments placed? | ApplicationDeployment identity/lifecycle and Component-to-Resource placement truth |
| **Network Enforcement Placement** | where may a technical pair be enforced? | candidate Firewall/policy-locator relevance |
| **Technical Access Evidence** | what source-qualified technical material was observed/imported? | immutable normalized evidence with source/time/provenance |
| **Access Policy Realization** | how does configured effective access compare with required effective access? | source-neutral realization assessment, semantic delta, vendor-neutral change design and proposed-result verification |
| **Network Environment Operations** | how is one verified target mutation executed and explained? | controlled mutation operation identity, authority admission, preconditions/concurrency, outcome and provenance |

`Connectivity Requirements` and `Connectivity Decision` remain legacy/current-state boundaries, not target BCs.

## Core semantic ladder

```text
Observed != Recognized != Needed != Authorized != Materialized != Realized
```

No level silently becomes another context's truth.

## Application / deployment / resource boundary

The 2026-09-15 Boundary Challenge separated three independently changing truths:

```text
Application Communication Catalogue
  Application
  Component
  Interaction / InteractionContractRevision
          |
          | ApplicationRef / ComponentRef
          v
Application Deployment
  ApplicationDeployment
  ComponentPlacement
          |
          | ResourceRef
          v
Resource Catalogue
  Resource
  technical realization
  ResourceScopeAffiliation
  ResourceResponsibility
```

`ApplicationDeployment` is an identifiable logical deployment of one Application. Its identity survives scaling, migration and ordinary Component placement replacement while continuity of that logical deployment is preserved.

`ComponentPlacement` is an access-domain placement fact relating a Component in the referenced Application to a Resource. It is not automatically a process, container, pod or provider runtime instance.

Application Deployment does not own Application/Component meaning or Resource technical truth. Resource Catalogue does not own which application Components are placed on a Resource. ACC no longer owns deployment or Resource binding truth.

The exact network-exposure contract between Application Deployment and Resource Catalogue remains Tactical-open. `ResourceEndpoint`, `DeploymentEndpointBinding`, `Environment`, listener/interface, VIP and provider-runtime concepts are not accepted merely to satisfy integration convenience.

## Governance chain

```text
Business Connectivity -- Process-backed Need --> Access Governance
ACC -- InteractionContractRevision --> Access Governance
Application Deployment -- ApplicationDeployment identity/placement facts --> Access Governance
Resource Catalogue -- effective Resource Scope Affiliation --> Access Governance
Authority Management -- effective authority --> Access Governance
Access Governance -- AuthorizationGranted / AuthorizationWithdrawn --> Access Policy
```

`Grant = source consent AND destination consent`.
`Revoke = source withdrawal OR destination withdrawal`.

The working governed-subject contract is:

```text
GovernedInteractionSubject {
    interactionContractRevisionRef
    sourceApplicationDeploymentRef
    destinationApplicationDeploymentRef
}
```

This replaces the former deployment-pair `DirectedInteractionIdentity`. Scaling, placement replacement, Resource replacement or address change does not by itself redefine this subject identity.

Subject identity and current authorization validity are distinct. A placement change can change the effective Resource Scope Affiliations and therefore the approval obligations without changing the governed subject. The required product behavior when that happens is an active S1 question and must not be invented in Tactical DDD.

Resource Catalogue owns which Responsibility Scope affiliations are effective for a Resource at a logical time. Access Governance owns how those facts establish source/destination approval obligations. Authority Management owns whether an Actor may perform the corresponding action for a selected scope/time.

## Required Policy Materialization

Required Policy Materialization remains a non-peer derived composition:

```text
Access Policy effective Policy Rules
+ ACC immutable Interaction traffic semantics
+ Application Deployment applicable Component placements / ResourceRefs
+ Resource Catalogue technical realization as-of selected time
+ NEP candidate target/policy locators
        -> normalized required technical predicates
        -> TargetRequiredPolicy
        -> APR
```

It owns no upstream source truth. Missing or unresolved deployment, realization, placement or locator input remains explicit and is not an empty required policy.

The materialization boundary must not require a Cartesian distributed join at scale. Computation-local derived projections may be introduced at Architecture when necessary without moving semantic ownership.

## Provider realization chain

Provider-specific interpretation and rendering remain integration capabilities, not BCs. APR consumes `TargetRequiredPolicy` and `ConfiguredEffectivePolicySnapshot`, owns `common = required ∩ configured`, `missing = required - configured`, `excess = configured - required`, change design and semantic verification. NEO owns controlled execution lifecycle; apply success is not convergence proof.

TAE owns immutable source-qualified technical evidence and does not assert universal currentness/completeness or authorization.

## Strategic invariants

- A Bounded Context is not a service/deployment unit.
- Business Need, consent, Policy Rule truth, technical materialization and realization are separate dimensions.
- ACC owns Application, Component and Interaction semantics; it does not own deployment placement.
- Application Deployment owns logical deployment identity and Component-to-Resource placement truth.
- Resource Catalogue owns Resource identity/lifecycle, Resource Scope Affiliation/responsibility and technical realization.
- `ApplicationDeployment` identity survives ordinary scaling/migration/placement replacement while logical deployment continuity is preserved.
- A technical realization change does not redefine semantic authorization identity.
- Authority Management owns effective action authority; consumers own decisions made using that authority.
- Required Policy Materialization is derived composition; unresolved is not empty required policy or APR drift.
- technical evidence is not authorization and is not automatically current/complete configured policy.
- NEP owns candidate enforcement-location relevance.
- provider interpretation/rendering are adapters around source-neutral contracts.
- APR core remains provider-neutral.
- NEO owns execution lifecycle, not policy reinterpretation or placement.
- no Shared Kernel is accepted between target BCs.

## Active strategic / S1 questions

The Application Deployment convergence pass promotes these behavior questions to active S1:

1. What product constraints determine which source/destination `ApplicationDeployment` pair may be selected for an Access Request?
2. When placement or Resource Scope Affiliation changes alter source/destination approval obligations, does existing authorization remain valid, require reapproval, warn, or withdraw? This is product behavior; stable subject identity alone does not answer it.
3. When several Responsibility Scopes are simultaneously applicable to one governance side, what approval obligations are required?

The exact network-exposure/public RC network concept remains Tactical-open and is not an S1 answer by itself.

## Strategic convergence disposition

The Application Deployment Boundary Challenge is `PASS`. The target model now contains eleven Bounded Contexts. Affected-edge ownership convergence is accepted for ACC -> AD, RC -> AD, ACC/AD/RC -> RPM and AM -> AD. The former RC -> ACC deployment binding and ACC-owned `DirectedInteractionIdentity` are superseded.

Global G2 is not implied. Context-local Tactical DDD must revalidate RC, AD and ACC in the new ownership order, while the active Access Governance behavior questions above route through S1 before their final semantic contract is frozen.
