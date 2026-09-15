# Ubiquitous Language

This file contains current strategic vocabulary. Context-local Tactical vocabulary belongs in the owning context documentation. As-built compatibility terms remain documented in their as-built contracts but are not promoted into target ubiquitous language.

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

**Component Placement** — AD-owned fact that one Component of an Application Deployment is placed on one Resource:

```text
ComponentPlacement = (ComponentRef, ResourceRef)
```

It is a relation value, not automatically a process/container/pod/runtime instance and not an independently identified placement aggregate in the current target model.

## Resource Catalogue

**Resource** — stable access-domain resource identity whose lifecycle/realization matters to governed access.

**Address Space** — current network realization of one Resource at a logical time:

```text
HostAddress | Prefix
```

Changing Address Space does not change Resource identity.

**Resource Scope Affiliation** — RC-owned time-qualified relation from Resource to `ResponsibilityScopeRef`. It does not grant actor authority.

**Resource Responsibility** — operational/business responsibility/contact fact for a Resource; not approval authority.

## Access Governance / Access Policy

**Governed Interaction Subject** — semantic authorization subject:

```text
InteractionContractRevisionRef
+ sourceApplicationDeploymentRef
+ destinationApplicationDeploymentRef
```

It is intentionally independent from Component Placement and Resource Address Space.

**Access Request** — one explicit attempt to obtain bilateral authorization for a governed subject under a business basis.

**Approval Obligation** — source-side or destination-side consent obligation. Grant requires the accepted bilateral obligations; withdrawal follows Access Governance semantics.

**Policy Rule** — Access Policy-owned authoritative current semantic authorization meaning for one governed subject.

**Vendor-Neutral Policy Export** — complete technical projection of the current effective AP policy set through ACC traffic semantics, AD placements and RC Address Spaces. It exposes access-list-oriented source/destination address, protocol and port/range meaning while remaining independent of firewall, device, ACL and provider syntax. It is a workflow/read composition and owns no Policy Rule truth.

## Authority Management

**Responsibility Scope** — stable correlation reference shared semantically between RC affiliation and AM authority contracts; it is not a shared aggregate.

**Effective Authority** — actor/action/scope/time admission result with provenance.

## Realization

**Required Policy Materialization** — non-peer derived composition of Access Policy authorization, ACC traffic semantics, AD placements, RC Address Space and NEP target relevance.

**Traffic Pair** — technical source/destination Address Space pair used for enforcement-placement reasoning.

**Target Required Policy** — target-specific normalized required effective policy produced by materialization.

**Configured Effective Policy Snapshot** — provider-interpreted source-neutral configured effective policy for an explicit comparison scope.

**Semantic Delta** — `common = required ∩ configured`, `missing = required - configured`, `excess = configured - required`.

**Verified Change Intent** — APR-owned vendor-neutral proposed change whose resulting additive semantics have been verified.

**Target Policy Artifact** — provider-rendered representation of verified intent.

**Network Operation** — NEO-owned controlled mutation attempt with authority, preconditions/concurrency, outcome and provenance.

## Core distinctions

```text
Observed != Recognized != Needed != Authorized != Materialized != Realized != Executed
```

The Vendor-Neutral Policy Export starts from current `Authorized` AP truth and materializes a complete technical read projection. It does not claim enforcement placement, configured reality, provider rendering, realization or execution.

## As-built compatibility vocabulary

Terms such as `Connectivity Requirement`, `Connectivity Decision`, ACC-owned compatibility `ComponentDeployment`, `DeploymentResourceBinding`, `DirectedInteractionIdentity`, `ResourceEndpoint` and legacy APR stage/status names may still exist in current as-built contracts and runtime compatibility paths. They remain documented where needed to reconstruct that implementation, but they do not replace the target vocabulary above.
