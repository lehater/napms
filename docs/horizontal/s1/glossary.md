# NAPMS full-width glossary

Status: CANDIDATE / non-canonical / S1 vocabulary reconstructed from accepted `docs/**`.

This glossary defines cross-capability product language. Strategic ownership is recorded in S2; context-local tactical vocabulary remains downstream of this horizontal pass. Legacy/as-built compatibility terms are not promoted into target language.

## Intent and application semantics

**Business Process** — business context explaining why connectivity is needed.

**Connectivity Need** — application-semantic business requirement for an Interaction. It is neither permission nor technical realization and may outlive a concrete deployment or traffic revision.

**Application** — reusable application definition/grouping.

**Component** — stable application role inside one Application.

**Interaction** — directed semantic communication template between two Components of the same Application. It contains no concrete deployment, Resource or address identity.

**Interaction Contract Revision** — immutable decision-relevant traffic-contract revision of one Interaction. The exact revision resolves its owning Interaction and therefore its source/destination Components.

**Traffic Alternative** — one vendor-neutral protocol/port selector within an Interaction Contract Revision.

## Deployment and resources

**Component Deployment** — one concrete independently governed deployed instance of one Component on one Resource. Deploying the same Component on another Resource creates another Component Deployment. It is not a whole-Application deployment, placement set, container identity or Resource address.

**Resource** — stable access-domain resource identity whose lifecycle and network realization matter to managed access.

**Address Space** — effective network realization of a Resource at a logical time. Current target cardinality is zero or one effective Address Space, whose value is exactly `HostAddress | Prefix`.

**Resource Scope Affiliation** — time-qualified relation between a Resource and a Responsibility Scope reference. It does not grant actor authority and is not automatically a Policy Rule decision input.

**Resource Responsibility** — operational/business responsibility or contact fact for a Resource. It is not policy-decision authority.

## Access policy and authority

**Policy Rule** — durable concrete access-policy object for one directed source/destination Component Deployment pair. It preserves current effective communication revision and the change/withdrawal history needed to explain that state.

**Policy Rule Ref** — opaque external reference to a Policy Rule that does not expose the owning context's internal identity representation.

**Rule Change** — one formally submitted attempt to establish or change the exact Interaction Contract Revision of a Policy Rule. Its formal state is `Pending | Accepted | Rejected`.

**Formal Rule Decision** — terminal `Accepted` or `Rejected` outcome for one Rule Change with actor/time/provenance sufficient for explanation. It does not itself model a customer-specific approval procedure.

**Current Effective Revision** — exact immutable Interaction Contract Revision currently effective for one Policy Rule. Pending or Rejected changes do not replace it.

**Withdrawal** — explicit fact clearing current effectiveness without deleting the Policy Rule or rewriting its history.

**Responsibility Scope** — stable correlation reference used for scope/authority reasoning. It is not a shared aggregate and does not itself imply approval responsibility.

**Effective Authority** — actor/action/scope/time admission result with provenance for a protected action. Authority admission is distinct from a business approval workflow.

## Evidence and recognition

**Technical Access Evidence** — immutable source-qualified technical facts that were observed, reported, derived or imported. Evidence is neither authorization nor desired policy.

**Evidence Access Recognition** — owner-preserving composition correlating technical evidence with Resource, Component Deployment and application-communication truth.

**Recognized Access Candidate** — non-authoritative result of evidence recognition that may seed policy work. It is not a Connectivity Need, formal decision or effective Policy Rule by itself.

**Unknown / Unavailable** — explicit state that trustworthy knowledge needed for a conclusion is missing or cannot be established. It must not be silently converted into absence, denial, permission or success.

**Ambiguous** — explicit state in which more than one candidate interpretation remains supported and no authoritative rule permits choosing one silently.

## Materialization, realization and operation

**Vendor-Neutral Policy Export** — complete technical projection of current effective Access Policy through exact application communication semantics, concrete Component Deployments and Resource Address Spaces. It is independent of provider/device syntax and owns no Policy Rule truth.

**Required Policy Materialization** — owner-preserving composition deriving target-required technical policy from current effective policy plus communication, deployment, resource-realization and applicable enforcement-placement truth.

**Traffic Pair** — technical source/destination Address Space pair used for enforcement-placement reasoning.

**Target Required Policy** — normalized required effective policy produced for an explicit target/comparison scope.

**Configured Effective Policy Snapshot** — provider-interpreted source-neutral representation of configured effective policy for an explicit scope, with source/completeness/freshness semantics.

**Semantic Delta** — source-neutral comparison where `common = required ∩ configured`, `missing = required - configured`, and `excess = configured - required`.

**Verified Change Intent** — vendor-neutral proposed realization change whose intended additive semantics have been verified before provider rendering/execution.

**Target Policy Artifact** — provider-specific representation rendered from verified source-neutral intent without changing its meaning.

**Network Operation** — controlled network-environment mutation attempt with identity, authority, preconditions/concurrency, outcome and provenance.

**Execution Success** — successful completion of a Network Operation. It is not by itself proof that configured effective policy has converged to required policy.

**Convergence Verification** — later evidence-based determination that configured effective policy corresponds to the required/expected result after execution.

## Read and analysis compositions

**Scoped Connectivity Inventory** — owner-preserving resource/connectivity read composition for investigation and operational navigation. It owns none of the facts it combines.

**Checker / Traffic Analysis** — technical tuple analysis workspace over explicit source/destination address, protocol, port/range and logical `asOf`. Required, allowed, configured evidence and network relevance remain separate conclusions.

**Connectivity Impact Analysis** — cross-context analysis of consequences/relationships using authoritative source facts without becoming their owner.

## Core distinctions

```text
Observed != Recognized != Needed != Proposed != Accepted != Materialized != Realized != Executed != Verified
```

These terms name different kinds of truth. They must not be collapsed into a generic access/status state.

## Compatibility vocabulary

Older accepted/as-built documents may contain terms such as `ApplicationDeployment`, `DeploymentInteraction`, ACC-owned compatibility `ComponentDeployment`, `DeploymentResourceBinding`, `DirectedInteractionIdentity`, `Connectivity Requirement`, `Connectivity Decision`, legacy DCS revision names and older APR stage/status names.

They remain reconstruction/compatibility vocabulary only. In particular, target `Interaction` is Component-level, target concrete deployment truth belongs to Application Deployment, and a target Policy Rule governs a compatible concrete source/destination Component Deployment pair using an exact Interaction Contract Revision.
