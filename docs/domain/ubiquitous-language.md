# Ubiquitous Language

This file contains current strategic vocabulary. Context-local Tactical vocabulary belongs in the owning context documentation. As-built compatibility terms remain documented in their as-built contracts but are not promoted into target ubiquitous language.

## Business Connectivity

**Business Process** — business context that explains why connectivity is needed.

**Connectivity Need** — application-semantic business requirement for an Interaction; not permission and not technical realization. A Need may outlive one concrete deployment or traffic revision.

## Application Communication Catalogue

**Application** — reusable application definition/grouping.

**Component** — stable application role inside one Application.

**Interaction** — directed semantic communication template from one Component to another Component of the same Application. It contains no deployment, Resource or address identity.

**Interaction Contract Revision** — immutable decision-relevant traffic contract revision of one Interaction. An exact revision identifies the owning Interaction and therefore its source/destination Component definitions.

**Traffic Alternative** — one vendor-neutral protocol/port selector inside an atomic Interaction Contract Revision.

## Application Deployment

**Component Deployment** — one concrete independently addressable deployed instance of one ACC Component on one Resource for the first MVP:

```text
ComponentDeployment
    ComponentRef
    ResourceRef
```

Deploying the same Component on a second Resource creates another Component Deployment. Component Deployment is not a whole-Application deployment, placement set, pod/container identity or Resource address.

## Resource Catalogue

**Resource** — stable access-domain resource identity whose lifecycle/realization matters to governed access.

**Address Space** — current network realization of one Resource at a logical time:

```text
HostAddress | Prefix
```

Changing Address Space does not change Resource or Component Deployment identity.

**Resource Scope Affiliation** — RC-owned time-qualified relation from Resource to `ResponsibilityScopeRef`. It does not grant actor authority.

**Resource Responsibility** — operational/business responsibility/contact fact for a Resource; not approval authority.

## Access Policy

**Policy Rule** — Access Policy-owned durable semantic object for one concrete directed source/destination Component Deployment pair. It owns current effective access state/revision plus the governance history required to explain how that state changed.

**Policy Rule ID** — Access Policy-internal stable identity of a Policy Rule. The exact representation is Tactical/Architecture work.

**Policy Rule Ref** — opaque external reference by which another context/composition refers to a Policy Rule without depending on AP-internal identity representation.

**Rule Change Proposal** — a proposed initial or subsequent traffic-contract revision for one Policy Rule, with business/evidence provenance and governance state. It is not current effective policy merely because it exists.

**Current Effective Revision** — the exact immutable Interaction Contract Revision currently authorized for one Policy Rule. A pending/rejected proposal does not replace it.

**Approval Obligation** — source-side or destination-side consent obligation derived for the concrete Rule endpoints. The first MVP requires exactly one distinct applicable Responsibility Scope per side.

**Recognized Access Candidate** — non-authoritative correlation result derived from technical evidence plus RC/AD/ACC truth that may initiate the same Access Policy proposal lifecycle as manual creation. It is not a Need, approval or Policy Rule effect by itself.

**Vendor-Neutral Policy Export** — complete technical projection of the current effective Access Policy set through ACC traffic semantics, concrete Component Deployments and RC Address Spaces. It exposes access-list-oriented source/destination address, protocol and port/range meaning while remaining independent of firewall, device, ACL and provider syntax. It is a workflow/read composition and owns no Policy Rule truth.

## Authority Management

**Responsibility Scope** — stable correlation reference shared semantically between RC affiliation and AM authority contracts; it is not a shared aggregate.

**Effective Authority** — actor/action/scope/time admission result with provenance.

## Technical Access Evidence

**Technical Access Evidence** — immutable source-qualified technical facts reported, observed/derived or imported. Evidence is not authorization or desired policy.

**Evidence Access Recognition** — non-peer composition that correlates TAE technical predicates with RC Resources, AD Component Deployments and ACC communication semantics to derive a Recognized Access Candidate or an unresolved/ambiguous result.

## Realization

**Required Policy Materialization** — non-peer derived composition of current effective Access Policy rules, ACC traffic semantics, concrete AD Component Deployments, RC Address Space and NEP target relevance.

**Traffic Pair** — technical source/destination Address Space pair used for enforcement-placement reasoning.

**Target Required Policy** — target-specific normalized required effective policy produced by materialization.

**Configured Effective Policy Snapshot** — provider-interpreted source-neutral configured effective policy for an explicit comparison scope.

**Semantic Delta** — `common = required ∩ configured`, `missing = required - configured`, `excess = configured - required`.

**Verified Change Intent** — APR-owned vendor-neutral proposed change whose resulting additive semantics have been verified.

**Target Policy Artifact** — provider-rendered representation of verified intent.

**Network Operation** — NEO-owned controlled mutation attempt with authority, preconditions/concurrency, outcome and provenance.

## Core distinctions

```text
Observed != Recognized != Needed != Proposed != Authorized != Materialized != Realized != Executed
```

Recognized evidence may exist before Process/Need attribution. Deliberate proposal submission still requires accepted business justification. Proposed change and current effective policy are distinct truths.

The Vendor-Neutral Policy Export starts from current effective Access Policy truth and materializes a complete technical read projection. It does not claim enforcement placement, configured reality, provider rendering, realization or execution.

## As-built compatibility vocabulary

Terms such as `ApplicationDeployment`, `DeploymentInteraction`, ACC-owned compatibility `ComponentDeployment`, `DeploymentResourceBinding`, `DirectedInteractionIdentity`, `Connectivity Requirement`, `Connectivity Decision`, legacy DCS revision names and legacy APR stage/status names may still exist in current as-built contracts and runtime compatibility paths. They remain documented where needed to reconstruct that implementation, but they do not replace the target vocabulary above.
