# NAPMS Strategic DDD model

Status: `S2 affected-edge convergence: AD boundary and minimal RC address contract accepted; AG behavior questions remain S1-open`.

Source baseline: DDD-BDM-010, 2026-09-14 G1 revalidation, ADR-019/020/021, global Strategic convergence pass, and 2026-09-15 AD/RC clarification.

Canonical relationship map: `context-map.md`.

## Current target Bounded Contexts

| Bounded Context | Semantic center | Responsibility |
|---|---|---|
| **Business Connectivity** | why is application connectivity needed? | Business Process, Connectivity Need, attribution/justification |
| **Access Governance** | has a governed interaction received and retained required consent? | Request history, bilateral consent, grant/withdrawal provenance |
| **Access Policy** | what semantic network access is currently authorized? | authoritative Policy Rule truth and effective authorization projection |
| **Authority Management** | who may perform a domain action for scope/time? | effective actor/action/scope authority and assignment semantics |
| **Resource Catalogue** | what access-domain resources exist and how are they realized? | Resource identity/lifecycle, one effective HostAddress-or-Prefix realization for current scope, scope affiliation/responsibility |
| **Application Communication Catalogue** | what applications/components exist and how may components communicate? | Application/Component/Interaction identity and immutable interaction traffic contract |
| **Application Deployment** | where are logical application deployments placed? | ApplicationDeployment identity/lifecycle and Component-to-Resource placement truth |
| **Network Enforcement Placement** | where may a technical pair be enforced? | candidate Firewall/policy-locator relevance |
| **Technical Access Evidence** | what source-qualified technical material was observed/imported? | immutable normalized evidence with source/time/provenance |
| **Access Policy Realization** | how does configured effective access compare with required effective access? | source-neutral realization assessment, delta, change design and verification |
| **Network Environment Operations** | how is one verified target mutation executed and explained? | controlled mutation identity, authority, preconditions/concurrency, outcome/provenance |

`Connectivity Requirements` and `Connectivity Decision` remain legacy/current-state boundaries, not target BCs.

## Core semantic ladder

```text
Observed != Recognized != Needed != Authorized != Materialized != Realized
```

## Application / deployment / resource boundary

```text
ACC
  Application / Component / InteractionContractRevision
          |
          | ApplicationRef / ComponentRef
          v
AD
  ApplicationDeployment
  ComponentPlacement -> ResourceRef
          |
          v
RC
  Resource
  effective AddressSpace [0..1] = HostAddress | Prefix
  ResourceScopeAffiliation
  ResourceResponsibility
```

`ApplicationDeployment` is an identifiable logical deployment of one Application. Its identity survives ordinary scaling, migration and placement replacement while continuity of that logical deployment is preserved.

`ComponentPlacement` relates a Component to one Resource. It is not automatically a process/container/pod/runtime instance.

For the current scope, RC owns at most one effective network `AddressSpace` per Resource at one logical time, represented as either one host address or one prefix. AD references only `ResourceRef`; it owns no address/endpoint selection. Address changes do not redefine Resource, ApplicationDeployment or governed-subject identity.

Multiple simultaneous addresses/interfaces, endpoint purpose, VIPs and deployment-specific exposure are explicitly future extensions, not current open model obligations. `ResourceEndpoint` and `DeploymentEndpointBinding` are not current target concepts.

## Governance chain

```text
BC -- Process-backed Need --> AG
ACC -- InteractionContractRevision --> AG
AD -- ApplicationDeployment identity/placement facts --> AG
RC -- effective Resource Scope Affiliation --> AG
AM -- effective authority --> AG
AG -- AuthorizationGranted / AuthorizationWithdrawn --> AP
```

`Grant = source consent AND destination consent`.
`Revoke = source withdrawal OR destination withdrawal`.

```text
GovernedInteractionSubject {
    interactionContractRevisionRef
    sourceApplicationDeploymentRef
    destinationApplicationDeploymentRef
}
```

Subject identity and current authorization validity remain distinct. Placement changes can alter effective Resource Scope Affiliations and approval obligations without changing subject identity; resulting product behavior remains S1-open.

## Required Policy Materialization

```text
AP effective Policy Rules
+ ACC immutable Interaction traffic semantics
+ AD applicable ComponentPlacements / ResourceRefs
+ RC ResourceRef -> effective HostAddress | Prefix as-of selected time
+ NEP candidate target/policy locators
        -> normalized required technical predicates
        -> TargetRequiredPolicy
        -> APR
```

Missing/unresolved placement, Resource AddressSpace or locator input remains explicit and is not an empty required policy. Prefixes remain prefixes; materialization need not enumerate their host addresses.

The boundary must not require a Cartesian distributed join at scale. Consumer-local rebuildable projections may be introduced later without moving semantic ownership.

## Strategic invariants

- ACC owns Application, Component and Interaction semantics; not deployment placement.
- AD owns logical deployment identity and Component-to-Resource placement truth.
- RC owns Resource identity/lifecycle, effective AddressSpace, Scope Affiliation and responsibility.
- current target RC network realization is at most one effective `HostAddress | Prefix` per Resource/time.
- AD references Resource only; it does not own address/endpoint realization.
- technical realization change does not redefine semantic authorization identity.
- Required Policy Materialization is derived composition; unresolved is not empty required policy/APR drift.
- technical evidence is not authorization or automatically current/complete configured policy.
- provider interpretation/rendering remain adapters; APR core remains provider-neutral.
- NEO owns execution lifecycle, not policy reinterpretation/placement.
- no Shared Kernel is accepted between target BCs.

## Active strategic / S1 questions

1. What product constraints determine selectable source/destination `ApplicationDeployment` pairs for an Access Request?
2. When placement or Resource Scope Affiliation changes alter approval obligations, does existing authorization remain valid, require reapproval, warn, or withdraw?
3. When several Responsibility Scopes are simultaneously applicable to one governance side, what approval obligations are required?

## Strategic convergence disposition

The Application Deployment Boundary Challenge is `PASS`. The RC/AD network-address question is closed for the current scope by the minimal Resource-level AddressSpace rule. The former RC -> ACC deployment binding, ACC-owned `ComponentDeployment` subject and endpoint-based target realization are superseded.

Global G2 is not implied. Foundational Tactical work should converge ACC and RC as independent upstream owners, then AD (`ACC + RC -> AD`), then AM/governance contracts before downstream materialization details are frozen.