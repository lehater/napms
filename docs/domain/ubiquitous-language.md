# Ubiquitous Language

This file contains current strategic vocabulary. Context-local Tactical vocabulary belongs in the owning context documentation.

## Application Communication Catalogue

**Application** — reusable application definition/grouping.

**Component** — stable application role inside one Application.

**Interaction** — directed semantic communication template from one Component to another; contains no deployment, Resource or address identity.

**Interaction Contract Revision** — immutable traffic-contract revision of an Interaction.

**Traffic Alternative** — one vendor-neutral protocol/port selector inside an atomic Interaction Contract Revision.

## Application Deployment

**Application Deployment** — stable logical deployment of one Application.

**Component Placement** — AD-owned `(ComponentRef, ResourceRef)` relation inside an Application Deployment.

## Resource Catalogue

**Resource** — stable access-domain resource identity.

**Address Space** — current Resource network realization: `HostAddress | Prefix`.

**Resource Scope Affiliation** — RC-owned Resource-to-ResponsibilityScopeRef relation; it does not grant actor authority.

**Resource Responsibility** — responsibility/contact fact for a Resource; not approval authority.

## Business Connectivity

**Business Process** — business context explaining why connectivity is needed.

**Connectivity Need** — application-semantic need for an Interaction; not permission or technical realization.

## Access Governance / Access Policy

**Governed Interaction Subject** — `InteractionContractRevisionRef + sourceApplicationDeploymentRef + destinationApplicationDeploymentRef`.

**Access Request** — explicit attempt to obtain bilateral authorization for a governed subject.

**Approval Obligation** — source-side or destination-side consent obligation.

**Policy Rule** — Access Policy-owned current semantic authorization meaning for one governed subject.

## Authority Management

**Responsibility Scope** — stable correlation reference used by RC affiliation and AM authority contracts.

**Effective Authority** — actor/action/scope/time admission result with provenance.

## Required Access Matrix

**Required Access Matrix** — vendor-neutral technical connectivity rows derived directly from selected ACC interaction revisions, AD placements and RC AddressSpaces. It is the output of the first implementation MVP and does not imply authorization or enforcement placement.

## Realization

**Required Policy Materialization** — derived composition of authorized policy with ACC/AD/RC facts and NEP target relevance.

**Traffic Pair** — technical source/destination AddressSpace pair used for enforcement-placement reasoning.

**Target Required Policy** — target-specific normalized required effective policy.

**Configured Effective Policy Snapshot** — provider-interpreted source-neutral configured effective policy for one comparison scope.

**Semantic Delta** — `common = required ∩ configured`, `missing = required - configured`, `excess = configured - required`.

**Verified Change Intent** — APR-owned vendor-neutral verified change intent.

**Target Policy Artifact** — provider-rendered representation of verified intent.

**Network Operation** — NEO-owned controlled mutation attempt with authority, preconditions, outcome and provenance.
