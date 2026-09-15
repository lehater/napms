# NAPMS Strategic DDD model

Status: `S2 first MVP DDD baseline converged 2026-09-15; future extensions deferred`.

Source baseline: DDD-BDM-010, 2026-09-14 G1 revalidation, ADR-019/020/021, global Strategic convergence and the 2026-09-15 full Tactical convergence pass.

Canonical relationship map: `context-map.md`.
DDD convergence checkpoint: `mvp-ddd-convergence-checkpoint.md`.

## Current target Bounded Contexts

| Bounded Context | Semantic center | Responsibility |
|---|---|---|
| **Business Connectivity** | why is application connectivity needed? | Business Process, Connectivity Need, attribution/current justification |
| **Access Governance** | has a governed interaction received and retained required consent? | Request history, bilateral obligations/decisions, current grant/withdrawal |
| **Access Policy** | what semantic network access is currently authorized? | authoritative current Policy Rule truth |
| **Authority Management** | who may perform a domain action for scope/time? | effective actor/action/scope authority and membership/role/scope assignment semantics |
| **Resource Catalogue** | what access-domain resources exist and how are they realized? | Resource identity/lifecycle, effective HostAddress-or-Prefix realization, scope affiliation/responsibility |
| **Application Communication Catalogue** | what applications/components exist and how may components communicate? | Application/Component/Interaction identity and immutable InteractionContractRevision traffic meaning |
| **Application Deployment** | where are logical application deployments placed? | ApplicationDeployment identity/continuity and current Component-to-Resource placement-set truth |
| **Network Enforcement Placement** | where may a technical pair be enforced? | candidate Firewall/policy-locator relevance |
| **Technical Access Evidence** | what source-qualified technical material was observed/imported? | immutable normalized evidence with source/time/provenance |
| **Access Policy Realization** | how does configured effective access compare with required effective access? | source-neutral assessment, semantic delta, accepted additive change design and verification |
| **Network Environment Operations** | how is one verified target mutation executed and explained? | controlled mutation identity, authority, preconditions/concurrency, outcome/provenance |

`Connectivity Requirements` and `Connectivity Decision` are legacy/current-state boundaries, not target BCs.

Provider Policy Interpreter and Provider Policy Renderer are integration capabilities, not peer Bounded Contexts. Required Policy Materialization is a non-peer derived composition.

## Core semantic ladder

```text
Observed != Recognized != Needed != Authorized != Materialized != Realized != Executed
```

Execution success does not imply semantic convergence; convergence is established only by later normalized observation/interpretation and comparison.

## Business need versus governed contract

Business Connectivity Need and Access Governance deliberately operate at different identity levels:

```text
ConnectivityNeed
    -> stable ACC InteractionRef

Concrete governed subject
    -> exact immutable InteractionContractRevisionRef
    -> source ApplicationDeploymentRef
    -> destination ApplicationDeploymentRef
```

A business Need may outlive one deployment or one traffic-contract revision. A concrete Request/Policy Rule must preserve the exact traffic revision actually governed.

## Application / deployment / resource boundary

```text
ACC
  Application / Component / Interaction
  immutable InteractionContractRevision
          |
          | ApplicationRef / ComponentRef
          v
AD
  ApplicationDeployment
  current Set<(ComponentRef, ResourceRef)>
          |
          v
RC
  Resource
  effective AddressSpace [0..1] = HostAddress | Prefix
  ResourceScopeAffiliation
  ResourceResponsibility
```

### ACC

`Interaction` is the stable directed communication template between two Components. A material traffic change creates a new immutable `InteractionContractRevision` while preserving Interaction identity. Old revisions remain historically resolvable.

The complete traffic-alternative set of one revision is atomic for governance/materialization; a consumer cannot silently authorize only a preferred subset.

### AD

`ApplicationDeployment` is a stable logical deployment identity. Its identity survives ordinary scaling, Resource migration and placement replacement while logical deployment continuity is preserved.

For MVP, `ComponentPlacement` is the relation value `(ComponentRef, ResourceRef)` inside the deployment's complete current placement set:

- zero, one or many Resources per Component are valid;
- the exact same pair is unique;
- all applicable placements are preserved downstream;
- complete empty placement truth is distinct from unavailable/unresolved placement truth.

No deployment lifecycle state machine or independently identified placement entity is invented because the first happy path does not require them.

### RC

RC owns Resource identity and, for current scope, at most one effective network `AddressSpace` per Resource/time, represented as `HostAddress | Prefix`.

AD references only Resource identity. Address changes do not redefine Resource, ApplicationDeployment, ComponentPlacement or governed-subject identity.

Multiple simultaneous addresses/interfaces, endpoint purpose, VIPs and deployment-specific exposure are explicit future extensions; `ResourceEndpoint` is not current target truth.

## Authority and responsibility

Responsibility and authority are separate truths:

```text
RC: ResourceRef -> ResponsibilityScopeRef affiliation
AM: ActorRef + ActionRef + ResponsibilityScopeRef + effectiveTime -> EffectiveAuthority
AG: correlates those truths into approval obligations
```

AM's MVP authority basis is effective Actor Group Membership + Group Role Assignment in a Responsibility Scope + Role-permitted Action.

`Admitted | Denied | Unknown` are distinct. Protected consumers fail closed on Denied/Unknown. Resource owner/admin/contact/responsibility metadata never grants authority by itself.

Historical decisions preserve the authority basis/evidence valid at decision time; later assignment changes do not rewrite history.

## Governance chain

```text
BC -- Process-backed Need --> AG
ACC -- exact InteractionContractRevision --> AG
AD -- ApplicationDeployment identity + complete current endpoint placements --> AG
RC -- effective Resource Scope Affiliation --> AG
AM -- effective authority --> AG
AG -- AuthorizationGranted / AuthorizationWithdrawn --> AP
```

```text
GovernedInteractionSubject {
    interactionContractRevisionRef
    sourceApplicationDeploymentRef
    destinationApplicationDeploymentRef
}
```

Accepted MVP behavior:

- a deployment pair is selectable only when each deployment realizes the corresponding Interaction endpoint Component and approval obligations are resolvable;
- every applicable placement is considered; AG never chooses an arbitrary Resource to simplify scope resolution;
- MVP requires exactly one distinct applicable Responsibility Scope per governance side; zero or several fail closed;
- source and destination obligations are independent and both are required for grant;
- either pending side may reject;
- either authorized side may withdraw current consent;
- placement/scope changes that leave obligations materially unchanged preserve authorization;
- a material obligation change causes AG to withdraw current authorization without changing subject identity;
- authorization may return only after current obligations are satisfied and AG explicitly grants again;
- historical approvals never silently restore a withdrawn grant.

Generalized overlapping-scope approval algebra is deliberately deferred.

## Access Policy

AP owns current semantic Policy Rule truth and reacts only to explicit AG grant/withdrawal facts. It does not reconstruct bilateral approvals, Resource scope affiliations or actor authority.

At most one current authoritative Policy Rule meaning exists per exact governed subject. Technical materialization failure does not erase semantic authorization.

## Required Policy Materialization

RPM remains a derived composition:

```text
AP effective Policy Rules
+ ACC exact immutable InteractionContractRevision
+ AD complete applicable ComponentPlacement sets
+ RC ResourceRef -> effective HostAddress | Prefix
+ NEP candidate Firewall / AccessListLocator results
        -> normalized required permit predicates
        -> TargetRequiredPolicy[] | unresolved
        -> APR
```

For each effective Policy Rule, every applicable source placement × destination placement technical pair participates in completeness.

Missing/unresolved placement, Resource realization, candidate target or policy locator is explicit unresolved state and is not an empty required policy.

The first MVP NEP edge supports only HostAddress-to-HostAddress TrafficPairs. Prefix remains first-class RC truth and fails closed at this edge rather than being expanded into hosts.

```text
ComparisonScope = firewallId + accessListName
```

Several NEP candidates/locators yield several comparison scopes; RPM never chooses a route/winner.

## Technical evidence and provider interpretation

TAE owns immutable source-qualified technical evidence. It does not decide which capture is current/complete configured policy for APR.

Provider Policy Interpreter is the integration capability that interprets provider ordering, deny/default, objects/groups/aliases and other native semantics into a trustworthy:

```text
ConfiguredEffectivePolicySnapshot
    comparisonScope
    effectivePermitSpace
    completeness
    freshness/provenance
    unsupported semantics
```

APR never parses raw provider syntax.

## Access Policy Realization

APR's MVP Tactical model requires no durable remediation aggregate. Its core concepts are immutable/derived semantic values:

```text
ComparisonScope
EffectivePermitSpace
SemanticDelta
RealizationAssessment
VerifiedChangeIntent
```

For complete comparable inputs:

```text
common  = required ∩ configured
missing = required - configured
excess  = configured - required

Realized <=> missing == empty AND excess == empty
Drift    <=> missing != empty OR excess != empty
```

Incomplete, mismatched, unknown or unsupported input is `Uncomparable`, not drift.

The accepted MVP remediation boundary is additive-only:

```text
missing -> VerifiedChangeIntent(ENSURE-PERMIT)
excess  -> report/audit only; no automatic removal
Realized -> no intent
Uncomparable -> no intent
```

Verified additive intent must cover exactly the selected missing permit space without narrowing previously configured access. If excess also existed, applying the additive intent does not itself prove `Realized`; a new observation/comparison is required.

Provenance/explainability is domain-significant. Its storage/index shape is not.

## Provider rendering boundary

Provider Policy Renderer translates a verified source-neutral intent into target/provider representation only when semantic equivalence can be established:

```text
VerifiedChangeIntent
+ TargetProviderCapabilities
+ base target correlation
    -> TargetPolicyArtifact
```

The renderer may not broaden, narrow or reinterpret APR intent. Unsupported semantics or inability to prove equivalence fails closed.

## Network Environment Operations

NEO consumes one already-rendered `TargetPolicyArtifact` plus actor/authority/precondition context and owns one controlled `NetworkOperation` lifecycle.

```text
TargetPolicyArtifact
+ operationId
+ actor / mutation authority scope
+ expected/base revision correlation
    -> authority check
    -> pre-check
    -> apply
    -> immediate post-check
    -> Verified | Rejected | PreconditionFailed | Drift | Unknown
```

NEO does not recompute authorization, target selection, APR change design or provider rendering. Unknown/stale authority or preconditions fail closed. Identical retries are idempotent; uncertain apply is not blindly retried.

NEO `Verified` proves immediate artifact/application correspondence under the execution contract, not final semantic convergence.

## Strategic invariants

- each authoritative semantic fact/decision has one explicit owner;
- cross-context references are opaque semantic references, not persistence foreign keys;
- no Shared Kernel is accepted between target BCs;
- unknown/incomplete evidence does not silently become absence, denial, empty policy or success;
- technical realization changes do not redefine higher-level semantic identities unless their accepted identity rules say so;
- current-state and historical evidence are not conflated;
- workflows/compositions may derive values but acquire no business authority merely by orchestrating owners;
- provider-native semantics remain at integration boundaries.

## Explicit non-blocking future extensions

- richer BusinessProcess retirement/criticality/duplicate-Need behavior;
- richer ApplicationDeployment lifecycle/history;
- ACC draft/publish/version-presentation workflow beyond immutable revisions;
- nested groups, role inheritance, explicit deny/ABAC/quorum authority rules;
- generalized approval semantics for several Responsibility Scopes on one governance side;
- Prefix-aware NEP query/matching semantics;
- several simultaneous Resource addresses/interfaces, endpoint purpose, VIP and deployment-specific exposure;
- managed-policy ownership/removal semantics for APR excess;
- richer APR change vocabulary or durable remediation-plan lifecycle;
- production provider transport, rollback and multi-target transaction mechanisms.

These are revisit-triggered extensions, not unresolved requirements for the first MVP happy path.

## S2 disposition

Strategic ownership and the Tactical models required by the first MVP are mutually coherent. No known P0/P1 semantic ownership, identity, lifecycle or invariant contradiction remains in the target baseline.

The formal G2 result is recorded in `mvp-ddd-convergence-checkpoint.md`.

G2 completion does **not** authorize Architecture, Implementation Readiness or code changes. The project remains parked at design until an explicit later request advances it.
