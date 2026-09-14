# NAPMS Strategic DDD model

Status: `S2 global Strategic DDD convergence accepted; Tactical revalidation remains active where noted`.

Source baseline: DDD-BDM-010, revalidated by 2026-09-14 G1 requirements, ADR-019, ADR-020, ADR-021 and the 2026-09-14 global Strategic convergence pass.

This document defines model/language/responsibility boundaries. It does not define services, databases, teams or deployment units.

Canonical relationship map: `context-map.md`.

## Current target Bounded Contexts

| Bounded Context | Semantic center | Responsibility |
|---|---|---|
| **Business Connectivity** | why is application connectivity needed? | Business Process, Connectivity Need, attribution/justification |
| **Access Governance** | has a concrete deployed interaction received and retained required consent? | Request history, bilateral consent, grant/withdrawal provenance |
| **Access Policy** | what semantic network access is currently authorized? | authoritative Policy Rule truth and effective authorization projection |
| **Authority Management** | who may perform a domain action for scope/time? | effective actor/action/scope authority and assignment semantics |
| **Resource Catalogue** | what access-domain resources exist and how are they currently realized? | Resource/Endpoint identity, scope affiliation, corporate-visible address realization |
| **Application Communication Catalogue** | what application/component interaction/deployment semantics exist? | ComponentDeployment/Interaction identity and immutable traffic contract |
| **Network Enforcement Placement** | where may a technical pair be enforced? | candidate Firewall/policy-locator relevance |
| **Technical Access Evidence** | what source-qualified technical material was observed/imported? | immutable normalized evidence with source/time/provenance |
| **Access Policy Realization** | how does configured effective access compare with required effective access? | source-neutral realization assessment, semantic delta, vendor-neutral change design and proposed-result verification |
| **Network Environment Operations** | how is one verified target mutation executed and explained? | controlled mutation operation identity, authority admission, precondition/concurrency checks, outcome and execution provenance |

`Connectivity Requirements` and `Connectivity Decision` remain legacy/current-state boundaries, not current target BCs.

## Core semantic ladder

```text
Observed != Recognized != Needed != Authorized != Materialized != Realized
```

No level silently becomes another context's truth.

## Governance chain

```text
Business Connectivity
    -- Process-backed Need --> Access Governance
Authority Management
    -- effective authority --> Access Governance
ACC
    -- deployed Interaction subject --> Access Governance / Access Policy
Resource Catalogue
    -- effective Resource Scope Affiliation --> Access Governance
Access Governance
    -- AuthorizationGranted / AuthorizationWithdrawn --> Access Policy
```

`Grant = source consent AND destination consent`.
`Revoke = source withdrawal OR destination withdrawal`.

Resource Catalogue owns which Responsibility Scope affiliations are effective for a Resource at a logical time. Access Governance owns how those scope facts establish source/destination approval obligations. Authority Management owns whether an Actor may perform the corresponding action for a selected scope/time. Resource responsibility/contact or owner/administrator metadata is not approval authority.

## Resource realization contract

Resource Catalogue owns:

```text
Resource
    -> ResourceEndpoint [0..N]
        -> current corporate-visible address/prefix [0..1]
```

Endpoint identity survives address changes. Missing current address remains valid catalogue truth and produces unresolved downstream materialization rather than silent omission.

ACC binds one ComponentDeployment to exactly one opaque ResourceRef for its lifetime in the current target. Resource Catalogue remains authoritative for Resource/Endpoint/address truth.

## Required Policy Materialization

ADR-020 establishes semantic-to-technical required-policy materialization as a **non-peer derived composition**:

```text
Access Policy effective Policy Rules
+ ACC Interaction traffic
+ Resource Catalogue Endpoint/address realization
        -> normalized required technical predicates
        -> NEP candidate target/policy locators
        -> TargetRequiredPolicy
        -> APR
```

It owns no upstream source truth or independent business lifecycle. Predicate deduplication preserves all contributing Policy Rule provenance. Missing address/placement/locator yields explicit `unresolved`, not empty required policy or APR drift.

## Provider configured-policy interpretation

ADR-021 establishes provider-specific effective-policy interpretation as an **integration/adapter capability**, not a Bounded Context and not TAE domain ownership.

```text
ProviderPolicyState
+ ProviderSemantics
+ target/policy comparison scope
    -> ConfiguredEffectivePolicySnapshot
```

The provider interpreter resolves provider-specific ordering, deny/default behavior, objects/groups, aliases and other constructs needed to determine source-neutral effective behavior exactly for the supported slice.

`ConfiguredEffectivePolicySnapshot` supplies APR with:

- comparable target/policy scope;
- normalized effective permit space;
- source/evidence references and time;
- explicit `Complete | Incomplete | Unknown` coverage semantics;
- interpreter identity/version and unsupported-semantics outcome.

Unsupported or incomplete provider semantics fail closed for a complete APR realization conclusion. Empty/incomplete evidence is not an empty configured policy.

TAE may preserve normalized source-qualified evidence, but it does not select the current capture, assert APR completeness, or own configured-effective-policy publication.

## Access Policy Realization boundary

APR core is provider-neutral. It consumes:

```text
TargetRequiredPolicy
ConfiguredEffectivePolicySnapshot
```

and owns:

```text
common  = required ∩ configured
missing = required - configured
excess  = configured - required
```

plus realization assessment, vendor-neutral change design and semantic verification of the proposed resulting policy.

Provider syntax, rule ordering, objects/groups/defaults and provider capability mechanics are not APR core concepts.

## Provider rendering boundary

ADR-021 establishes provider-specific rendering as an **output adapter/integration capability**, not APR domain ownership.

```text
VerifiedChangeIntent
+ target/provider capabilities
+ base target revision/correlation
    -> TargetPolicyArtifact
    -> NEO
```

The renderer translates representation only. It may not reinterpret or widen/narrow APR's verified semantic intent.

A successful rendering path must establish semantic equivalence between the verified intent and target representation for supported provider semantics. The proof mechanism—deterministic construction, round-trip interpretation, simulation, or another method—is S3 Architecture, not S2 domain truth.

If equivalence cannot be established, rendering fails closed and no executable artifact is handed to NEO.

## Network Environment Operations boundary

Network Environment Operations is a target Bounded Context. Its separate semantic boundary is justified by its own operation identity, mutation-authority admission, optimistic-concurrency/precondition boundary, failure/recovery vocabulary and audit lifecycle.

NEO owns controlled target mutation lifecycle, authority admission, precondition/concurrency checks, apply outcome and operation provenance for a supplied `TargetPolicyArtifact`.

NEO does not reinterpret policy semantics, repair unsupported renderer output or re-decide Network Enforcement Placement. Apply success is not convergence proof; post-change configured policy must later be interpreted and compared again.

## Technical Access Evidence boundary

TAE owns immutable source-qualified technical evidence. A capture carries its source/scope/capture identity, evidence time, recorded provenance and normalized source-faithful entries.

TAE does not assert universal currentness/completeness and does not become authorization, desired policy, placement or realization truth. Any consumer requiring freshness/currentness/completeness establishes that meaning in its own source/consumer contract.

## End-to-end realization chain

```text
Business Connectivity
 -> Access Governance
 -> Access Policy
 -> Required Policy Materialization
 -> TargetRequiredPolicy
                          +
provider/device state
 -> Provider Policy Interpreter
 -> ConfiguredEffectivePolicySnapshot
                          |
                          v
                         APR
              assessment / delta
              change design
              semantic verification
                          |
                          v
                VerifiedChangeIntent
                          |
                          v
              Provider Policy Renderer
                          |
                          v
                TargetPolicyArtifact
                          |
                          v
                         NEO
                          |
                          v
                subsequent observation
 -> Provider Policy Interpreter
 -> configured effective policy
 -> APR convergence comparison
```

## External seams

Current strategic external seams are:

- **provider/network-device environment** — source/target for routing, configured policy, technical observation and controlled mutation; provider-native meaning is isolated through adapters;
- **optional external identity provider** — may establish a source-qualified identity that maps to one NAPMS Actor; it never grants business authority directly;
- **optional enterprise source systems** — may later supply Authority Management, ACC, Resource Catalogue or organizational-responsibility reference data through context-owned import/projection seams.

The supported product remains local-first. No concrete enterprise IdP, directory, CMDB, organization registry or synchronization protocol is required until a future accepted requirement selects one.

Business Connectivity may carry source-neutral organizational-responsibility references for Business Process explanation/governance correlation. An external organizational unit is not automatically a NAPMS Responsibility Scope and cannot silently grant Authority Management permissions.

## Strategic invariants

- A Bounded Context is not a service/deployment unit.
- Business Need, consent, Policy Rule truth, technical materialization and realization are separate dimensions.
- Authority Management owns effective action authority; consumers own decisions made using that authority.
- Resource Catalogue owns Resource Scope Affiliation; the same `ResponsibilityScopeRef` may correlate authority without making affiliation equal authority.
- ResourceEndpoint identity is stable across address changes.
- ACC owns ComponentDeployment -> ResourceRef binding; Resource Catalogue owns the referenced Resource/Endpoint realization.
- Required Policy Materialization is derived composition, not peer domain truth.
- unresolved materialization is not empty required policy or realization drift.
- technical evidence is not authorization and is not automatically current/complete configured policy.
- NEP owns candidate enforcement-location relevance.
- provider interpretation/rendering are adapter/integration capabilities around source-neutral contracts, not peer BCs.
- APR core remains provider-neutral and owns effective-policy algebra/change semantics, not provider syntax.
- rendering must preserve verified semantics; unsupported semantics fail closed.
- NEO is a Bounded Context owning execution lifecycle, not policy reinterpretation or placement.
- technical realization changes do not redefine semantic authorization identity.

## Global Strategic convergence disposition

The 2026-09-14 global boundary/relationship pass is `PASS` for the current target scope. The canonical relationship details and challenge result are in `context-map.md`.

Closed strategic gaps include:

- Network Environment Operations normalized into the target BC set;
- explicit Resource Catalogue -> Access Governance contract for effective responsibility-scope facts;
- explicit external seams and local-first ownership boundaries;
- one canonical Context Map for all material current relationships.

The following remain deliberately deferred without blocking strategic convergence:

- whether a later Resource Scope Affiliation/responsibility change causes warning, reapproval or automatic withdrawal of existing authorization;
- how Access Governance selects among simultaneously applicable overlapping responsibility scopes;
- exact organization-reference/provider shape when a concrete external enterprise organization source is required.

The first two are Access Governance/product-behavior questions and must re-enter S1 when a use case requires behavior not already accepted. The last is an optional external-source detail and re-enters Strategic DDD only if a concrete source changes ownership/language boundaries.

Strategic convergence does not imply global `G2 PASS`: context-local Tactical DDD must still converge wherever identity/lifecycle/invariant work remains dirty.
