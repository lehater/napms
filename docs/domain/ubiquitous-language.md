# Ubiquitous Language

Status: `current target strategic vocabulary; 2026-09-15`.

This file is intentionally compact. Context-local Tactical vocabulary belongs in the owning context documentation. Legacy `Connectivity Requirement`, `Connectivity Decision`, ACC-owned `ComponentDeployment`, `DeploymentResourceBinding`, `DirectedInteractionIdentity` and `ResourceEndpoint` remain runtime/history terms only and are not current target vocabulary.

## Business Connectivity

**Business Process** — business context that explains why connectivity is needed.

**Connectivity Need** — application-semantic business requirement for an Interaction; not permission and not technical realization.

## Application Communication Catalogue

**Application** — reusable application definition/grouping.

**Component** — stable application role inside one Application.

**Interaction** — directed semantic communication template from one Component to another. It contains no deployment, Resource or address identity.

**Interaction Contract Revision** — immutable decision-relevant traffic contract revision of an Interaction.

**Traffic Alternative** — one vendor-neutral protocol/port selector inside an atomic Interaction Contract Revision.

## Application Deployment

**Application Deployment** — stable logical deployment of one Application. Ordinary scaling, Resource migration and placement replacement do not change identity while logical deployment continuity is preserved.

**Component Placement** — AD-owned fact that one Component of an Application Deployment is placed on one Resource.

```text
ComponentPlacement
    ApplicationDeploymentRef
    ComponentRef
    ResourceRef
```

It is not automatically a process/container/pod/runtime instance.

## Resource Catalogue

**Resource** — stable access-domain resource identity whose lifecycle/realization matters to governed access.

**Address Space** — current target network realization of one Resource at a logical time. At most one is effective for current scope:

```text
HostAddress | Prefix
```

Changing Address Space does not change Resource identity. Multiple simultaneous addresses/interfaces, endpoint purpose and VIP/exposure modelling are future extensions.

**Resource Scope Affiliation** — time-qualified RC-owned relation from Resource to ResponsibilityScopeRef. It does not grant actor authority.

**Resource Responsibility** — operational/business responsibility/contact fact for a Resource; not approval authority.

## Access Governance / Access Policy

**Governed Interaction Subject** — semantic authorization subject:

```text
InteractionContractRevisionRef
+ sourceApplicationDeploymentRef
+ destinationApplicationDeploymentRef
```

It is intentionally independent from ComponentPlacement and Resource Address Space.

**Access Request** — one explicit attempt to obtain bilateral authorization for a governed subject under a business basis.

**Approval Obligation** — source-side or destination-side consent obligation. Grant requires both sides; either side may withdraw current consent.

**Policy Rule** — Access Policy-owned authoritative current semantic authorization meaning for one governed subject.

## Authority Management

**Responsibility Scope** — stable correlation reference shared semantically between RC affiliation and AM authority contracts; not a shared aggregate.

**Effective Authority** — actor/action/scope/time admission result with provenance.

## Realization

**Required Policy Materialization** — non-peer derived composition of AP authorization, ACC traffic semantics, AD placements, RC Address Space and NEP target relevance.

**Traffic Pair** — technical source/destination address-space pair used for enforcement-placement reasoning.

**Target Required Policy** — target-specific normalized required effective policy produced by materialization.

**Configured Effective Policy Snapshot** — provider-interpreted source-neutral configured effective policy for an explicit comparison scope.

**Semantic Delta** — `common = required ∩ configured`, `missing = required - configured`, `excess = configured - required`.

**Verified Change Intent** — APR-owned vendor-neutral proposed change whose resulting semantics have been verified.

**Target Policy Artifact** — provider-rendered representation of verified intent.

**Network Operation** — NEO-owned controlled mutation attempt with authority, preconditions/concurrency, outcome and provenance.

## Core distinction

```text
Observed != Recognized != Needed != Authorized != Materialized != Realized
```
