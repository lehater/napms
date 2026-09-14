# NAPMS Strategic DDD model

Status: `S2 strategic revalidation accepted through provider-policy boundaries`.

Source baseline: DDD-BDM-010, revalidated by 2026-09-14 G1 requirements, ADR-019, ADR-020 and ADR-021.

This document defines model/language/responsibility boundaries. It does not define services, databases, teams or deployment units.

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
Access Governance
    -- AuthorizationGranted / AuthorizationWithdrawn --> Access Policy
```

`Grant = source consent AND destination consent`.
`Revoke = source withdrawal OR destination withdrawal`.

## Resource realization contract

Resource Catalogue owns:

```text
Resource
    -> ResourceEndpoint [0..N]
        -> current corporate-visible address/prefix [0..1]
```

Endpoint identity survives address changes. Missing current address remains valid catalogue truth and produces unresolved downstream materialization rather than silent omission.

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

NEO owns controlled target mutation lifecycle, authority admission, precondition/concurrency checks, apply outcome and operation provenance for a supplied `TargetPolicyArtifact`.

NEO does not reinterpret policy semantics or repair unsupported renderer output. Apply success is not convergence proof; post-change configured policy must later be interpreted and compared again.

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

## Strategic invariants

- A Bounded Context is not a service/deployment unit.
- Business Need, consent, Policy Rule truth, technical materialization and realization are separate dimensions.
- Authority Management owns effective action authority; consumers own decisions made using that authority.
- ResourceEndpoint identity is stable across address changes.
- Required Policy Materialization is derived composition, not peer domain truth.
- unresolved materialization is not empty required policy or realization drift.
- technical evidence is not authorization and is not automatically current/complete configured policy.
- NEP owns candidate enforcement-location relevance.
- provider interpretation/rendering are adapter/integration capabilities around source-neutral contracts, not peer BCs.
- APR core remains provider-neutral and owns effective-policy algebra/change semantics, not provider syntax.
- rendering must preserve verified semantics; unsupported semantics fail closed.
- NEO owns execution lifecycle, not policy reinterpretation.
- technical realization changes do not redefine semantic authorization identity.

## Remaining strategic questions

- whether responsibility-scope changes require warning, reapproval or automatic revocation;
- exact Process organizational-responsibility contract with external enterprise structure.
