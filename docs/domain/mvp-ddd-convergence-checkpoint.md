# First MVP DDD Convergence Checkpoint

Status: `G2 PASS for the first MVP target DDD baseline; TAE acquisition edge revalidated 2026-09-15`.

## Purpose

Record the bounded first-MVP Domain Design closure after revalidating Strategic and Tactical DDD across every target Bounded Context required by the accepted happy path.

This checkpoint is a design gate only. It does not authorize Architecture, Implementation Readiness or code changes.

## Scope

```text
Business Connectivity
    -> Access Governance
    -> Access Policy

Application Communication Catalogue
    -> Application Deployment
    -> Resource Catalogue

Authority Management
    -> protected actions / governance / execution

Access Policy + ACC + AD + RC + NEP
    -> Required Policy Materialization
    -> Access Policy Realization
    -> Provider rendering boundary
    -> Network Environment Operations

Technical Evidence Acquisition / Collectors
    -> normalized source-qualified evidence
    -> Technical Access Evidence

Technical Access Evidence
    -> source-qualified technical evidence
Provider Policy Interpreter
    -> configured effective policy for APR
```

Required Policy Materialization is derived composition. Provider Policy Interpreter, Provider Policy Renderer and Technical Evidence Acquisition/Collectors are integration/application capabilities. They are not additional Bounded Contexts.

## Target Bounded Context matrix

| Bounded Context | Canonical Tactical owner | MVP Tactical disposition |
|---|---|---|
| Business Connectivity | `business-connectivity/target-tactical-model.md` | PASS — Process/Need identity/currentness and business-basis contracts explicit |
| Access Governance | `access-governance/target-tactical-model.md` | PASS — request history, bilateral obligations/decisions and current grant/withdrawal explicit |
| Access Policy | `access-policy/tactical-model.md` | PASS — one current semantic Policy Rule meaning per governed subject; AG handoff explicit |
| Authority Management | `authority-management/tactical-model.md` | PASS — actor/action/scope/time authority and assignment/evidence semantics explicit |
| Resource Catalogue | `resource-catalogue/tactical-model.md` | PASS — Resource identity, AddressSpace, scope affiliation and responsibility semantics explicit |
| Application Communication Catalogue | `application-communication-catalogue/target-tactical-model.md` | PASS — Interaction identity and immutable InteractionContractRevision semantics explicit |
| Application Deployment | `application-deployment/tactical-model.md` | PASS — deployment identity/continuity and zero/one/many placement-set semantics explicit |
| Network Enforcement Placement | `network-enforcement-placement/target-tactical-model.md` | PASS — candidate Firewall/policy-locator relevance model explicit |
| Technical Access Evidence | `technical-access-evidence/tactical-model.md` | PASS — canonical normalized source-qualified evidence semantics explicit; collection initiation remains outside TAE |
| Access Policy Realization | `access-policy-realization/tactical-model.md` | PASS — comparison/delta/additive intent are exact immutable/derived values; no invented aggregate |
| Network Environment Operations | `network-environment-operations/tactical-model.md` | PASS — controlled mutation identity/authority/precondition/outcome semantics explicit; no general evidence-acquisition ownership |

Implemented/current-state Tactical documents that conflict with these target owners are migration evidence only and do not redefine target semantics.

## Cross-context coherence checks

### Business need and communication contract

```text
ConnectivityNeed -> stable InteractionRef
Concrete governance -> exact InteractionContractRevisionRef
```

PASS. A business Need may survive a traffic revision/deployment change, while each concrete authorization preserves the exact immutable traffic contract it governs.

### ACC / AD / RC separation

```text
ACC: Application / Component / Interaction / immutable contract revision
AD:  ApplicationDeployment / complete current Set<(ComponentRef, ResourceRef)>
RC:  Resource / effective HostAddress | Prefix / ScopeAffiliation
```

PASS. No target owner imports endpoint/address/deployment meaning from another context.

### Application Deployment multiplicity

PASS.

- ComponentPlacement is an MVP relation value, not a separately identified entity.
- one Component may have zero, one or many current Resource placements;
- exact duplicate `(ComponentRef, ResourceRef)` pairs are invalid;
- all applicable placements are preserved downstream;
- ordinary scaling/migration does not change ApplicationDeployment identity;
- current empty placement truth is distinct from unavailable/unresolved placement truth.

Historical placement time-travel is not required by the current happy path and remains a future product/domain extension if a concrete journey requires it.

### Authority and responsibility

PASS.

```text
RC ResourceScopeAffiliation != AM EffectiveAuthority
```

AM derives exact actor/action/scope/time admission from membership + role + scope assignment. Resource owner/admin/contact facts do not grant authority. Unknown authority fails closed. Historical consuming decisions retain authority evidence rather than being rewritten when current assignments change.

### Governed subject and obligation change

PASS.

```text
GovernedInteractionSubject =
    InteractionContractRevisionRef
  + sourceApplicationDeploymentRef
  + destinationApplicationDeploymentRef
```

Placement/address/scope-affiliation changes do not change subject identity by themselves. AG requires exactly one distinct applicable ResponsibilityScope per side for MVP. Material obligation change withdraws current authorization; materially unchanged obligations preserve it.

### AG -> AP

PASS.

```text
AuthorizationGranted
AuthorizationWithdrawn
```

AP does not duplicate bilateral governance. Historical requests/approvals cannot silently reactivate current policy after withdrawal.

### Required Policy Materialization

PASS.

RPM consumes published owner truth and produces complete target-specific required policy or explicit unresolved state. It is not a Bounded Context and owns no independent authorization/placement/resource truth.

Every applicable source placement × destination placement pair participates in completeness. Missing evidence is never converted into an empty required policy.

### RC / NEP first technical edge

PASS with explicit MVP boundary.

RC preserves `HostAddress | Prefix`. The current end-to-end NEP edge accepts only `HostAddress -> HostAddress`; Prefix causes unresolved rather than host expansion or invented matching semantics.

### NEP candidate semantics

PASS.

Candidate Firewall/access-list output means relevance-to-inspect/affect, not a proven route. Multiple candidates/locators are preserved and become independent comparison scopes.

### Technical Evidence Acquisition -> TAE

PASS.

```text
device/config acquisition ----\
NetFlow/IPFIX collector -------+--> faithful normalization --> TAE
file/import adapter -----------/
```

TAE owns the canonical normalized evidence vocabulary and immutable evidence history. Source-specific acquisition/collector capabilities own collection and faithful translation into the TAE contract.

TAE does not own polling cadence, scheduling, retries, credentials or source transport. Those capabilities are not new Bounded Contexts.

NEO is not the TAE read/acquisition gateway. NEO remains the controlled-mutation owner. Any shared provider/device access client or adapter layer between acquisition and NEO is an S3 Architecture question and is not required for G2.

### TAE / Provider Policy Interpreter

PASS.

TAE owns source-qualified normalized evidence and deliberately does not select globally current/fresh/complete configured policy.

Provider Policy Interpreter owns provider-native interpretation and publishes `ConfiguredEffectivePolicySnapshot` with explicit completeness/freshness/unsupported semantics for APR. PPI may consume provider material directly, selected TAE configured evidence under an explicit source contract, or both.

`TrafficDerived` evidence may feed recognition/reconciliation compositions instead. Recording evidence alone never creates authorization, desired policy, an ACL/access proposal or remediation intent.

### APR

PASS.

For complete comparable input:

```text
common  = required ∩ configured
missing = required - configured
excess  = configured - required
```

`Realized` iff missing/excess are both empty. `Drift` iff either is non-empty. Invalid/incomplete correlation is `Uncomparable`.

MVP remediation is additive-only:

```text
missing -> ENSURE-PERMIT
excess  -> evidence only
```

Assessment, delta and VerifiedChangeIntent are immutable/derived values. No durable remediation aggregate is required by the current product behavior.

### Renderer / NEO

PASS at the semantic boundary.

Provider renderer is not APR domain ownership and may publish a TargetPolicyArtifact only when verified semantics can be represented equivalently. NEO owns controlled execution and does not reinterpret the intent/artifact. Immediate execution verification is not final semantic convergence.

## Superseded conflicts closed in the DDD baseline

The following formerly canonical/stale assumptions were removed from the target baseline:

- ACC-owned `ComponentDeployment` as target deployment identity;
- exactly-one Resource per Component deployment as target semantics;
- moving Resource necessarily creates a new governed deployment subject;
- `ResourceEndpoint` as current target realization identity;
- ACC current mutable traffic without immutable decision-relevant revision identity;
- Access Governance obligation-change behavior marked S1-open;
- APR Tactical DDD marked open solely because persistence/scale/migration mechanics were not chosen;
- missing canonical Authority Management Tactical semantics;
- old scoped-inventory/materialization requirements that reintroduced ComponentDeployment/Endpoint semantics.

The 2026-09-15 affected-edge revalidation additionally made explicit that TAE is not its own collector/scheduler and NEO is not a generic read gateway.

Git history and current runtime documents may still contain superseded meanings as migration/current-state evidence.

## Explicit non-blocking deferrals

The first MVP DDD deliberately does not solve:

- generalized several-scope approval algebra;
- nested groups, role inheritance, explicit deny/ABAC/quorum authority rules;
- detailed BusinessProcess retirement/criticality/duplicate-Need policy;
- richer ApplicationDeployment lifecycle or historical placement facts;
- ACC draft/publish/version-number workflow beyond immutable contract snapshots;
- Prefix-aware NEP matching;
- several simultaneous Resource addresses/interfaces/VIPs/deployment-specific exposure;
- managed-policy ownership and automatic removal/narrowing of APR excess;
- richer APR change vocabulary or durable remediation-plan lifecycle;
- concrete acquisition polling/scheduling framework and shared provider/device access implementation between collectors and NEO;
- provider transport, rollback, distributed transactions, persistence schemas or package structure.

Each is reopened only when a concrete requirement/journey creates pressure. None is required to express the accepted first happy path.

## G2 evaluation

`G2 PASS` for the first MVP target DDD baseline, including the revalidated TAE acquisition edge.

Reasons:

- every material authoritative domain fact/decision in the path has one identifiable semantic owner;
- all 11 target Bounded Contexts have Tactical semantics sufficient for their MVP responsibilities;
- relevant identities, sameness rules, current-vs-historical distinctions and invariants are explicit;
- TAE normalized evidence ownership is separate from acquisition orchestration and downstream interpretation;
- NEO mutation ownership is separate from general evidence acquisition;
- Strategic and Tactical models are mutually coherent after the affected-edge revalidation;
- cross-context contracts expose public semantic meaning rather than peer-private models;
- derived composition/integration capabilities are not promoted into false Bounded Contexts;
- no known P0/P1 semantic ownership, identity, lifecycle or invariant contradiction remains;
- remaining unknowns are explicitly outside the first MVP or belong to S3 Architecture and carry clear revisit triggers;
- an eventual implementer need not invent domain meaning to understand the accepted target model.

## Stop condition

Per project-owner instruction on 2026-09-15, work stops at design after DDD closure.

```text
Lifecycle stage: S2
Stage state: ACCEPTED
G2: PASS
Implementation authorization: none
```

The branch diff against `main` is documentation-only at this checkpoint. No further code work is permitted by this checkpoint.

A later move to Architecture/S3, Implementation Readiness/S4 or code requires a new explicit request and a fresh downstream lifecycle decision based on this G2 baseline.
