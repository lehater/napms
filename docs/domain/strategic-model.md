# NAPMS Strategic DDD model

Status: `S2 first MVP semantic vertical converged through NEO execution boundary; broader extensions deferred`.

Source baseline: DDD-BDM-010, 2026-09-14 G1 revalidation, ADR-019/020/021, global Strategic convergence pass, and 2026-09-15 ACC/AD/RC/AG/AP/RPM/APR/NEO clarification.

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
| **Access Policy Realization** | how does configured effective access compare with required effective access? | source-neutral realization assessment, delta, accepted change design and verification |
| **Network Environment Operations** | how is one verified target mutation executed and explained? | controlled mutation identity, authority, preconditions/concurrency, outcome/provenance |

`Connectivity Requirements` and `Connectivity Decision` remain legacy/current-state boundaries, not target BCs.

Provider Policy Interpreter and Provider Policy Renderer are integration capabilities, not peer Bounded Contexts. Required Policy Materialization is a non-peer derived composition.

## Core semantic ladder

```text
Observed != Recognized != Needed != Authorized != Materialized != Realized != Executed
```

Execution success still does not imply semantic convergence; convergence is established only by later normalized observation and comparison.

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

For the current scope, RC owns at most one effective network `AddressSpace` per Resource at one logical time, represented as either one HostAddress or one Prefix. AD references only `ResourceRef`; it owns no address/endpoint selection. Address changes do not redefine Resource, ApplicationDeployment or governed-subject identity.

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

```text
GovernedInteractionSubject {
    interactionContractRevisionRef
    sourceApplicationDeploymentRef
    destinationApplicationDeploymentRef
}
```

Current MVP behavior is accepted:

- a deployment pair is selectable only when each deployment realizes the corresponding Interaction endpoint Component and current approval obligations are resolvable;
- MVP requires exactly one distinct applicable Responsibility Scope per governance side; zero or several scopes fail closed and are not selectable/authorizable;
- source and destination obligations are independent and both are required for grant;
- either pending side may reject;
- either authorized side may withdraw current consent;
- placement/scope changes that leave obligations materially unchanged preserve authorization;
- a material obligation change causes AG to publish `AuthorizationWithdrawn` without changing governed-subject identity;
- current authorization may return only after current obligations are satisfied and AG publishes a new `AuthorizationGranted`;
- historical approvals never silently restore a withdrawn grant.

Generalized overlapping-scope approval algebra is deliberately deferred beyond the first happy path.

## Access Policy edge

AP owns current semantic Policy Rule truth and reacts only to explicit AG grant/withdrawal facts. It does not infer bilateral obligations from AD/RC state.

A later `AuthorizationGranted` after withdrawal re-establishes authorization for the same governed subject; it does not create a different subject identity.

## Required Policy Materialization

RPM remains a non-peer derived composition:

```text
AP effective Policy Rules
+ ACC immutable Interaction traffic semantics
+ AD applicable ComponentPlacements / ResourceRefs
+ RC ResourceRef -> effective HostAddress | Prefix as-of selected time
+ NEP candidate Firewall / AccessListLocator results
        -> normalized required permit predicates
        -> TargetRequiredPolicy[] | unresolved
        -> APR
```

For one target comparison scope:

```text
ComparisonScope = firewallId + accessListName

TargetRequiredPolicy {
    comparisonScope
    requiredPermitSpace
    contributingPolicyRuleRefs
    logicalTime
    inputProvenance
    inputFreshness
}
```

Multiple NEP candidates/locators are preserved as multiple comparison scopes; RPM never chooses an arbitrary route or winning Firewall.

Missing/unresolved placement, Resource realization, candidate target or policy locator is explicit unresolved state and is not an empty required policy.

RC Prefix remains a first-class AddressSpace and is never expanded into hosts. The first end-to-end MVP NEP edge currently supports only HostAddress-to-HostAddress TrafficPairs; if RPM receives a Prefix on either side it fails closed as unresolved until Prefix-aware NEP query semantics are explicitly designed.

Consumer-local rebuildable projections may be introduced later for scale without moving source semantic ownership.

## Access Policy Realization

APR consumes complete comparable source-neutral required/configured permit semantics for exactly one `ComparisonScope = firewallId + accessListName`.

```text
common  = required ∩ configured
missing = required - configured
excess  = configured - required
```

`Realized` means both `missing` and `excess` are empty. `Drift` means either is non-empty. Incomplete, mismatched or unsupported inputs are `Uncomparable`, not drift.

The accepted MVP remediation boundary is additive-only:

```text
missing -> VerifiedChangeIntent(ENSURE-PERMIT)
excess  -> report/audit only; no automatic removal
Realized -> no intent
Uncomparable -> no intent
```

The target has no accepted managed-policy scope proving that NAPMS owns all configured permit space in an ACL. Automatic removal/narrowing is therefore explicitly deferred.

The minimum source-neutral intent is:

```text
VerifiedChangeIntent {
    comparisonScope
    operation = ENSURE-PERMIT
    permitSpace
    baseConfiguredCorrelation
    requiredPolicyProvenance
    deltaProvenance
    verificationEvidence
}
```

APR owns semantic verification, not provider-native representation.

## Provider rendering boundary

Provider Policy Renderer is an integration capability implementing ADR-021:

```text
VerifiedChangeIntent
+ TargetProviderCapabilities
+ base target revision/correlation
    -> TargetPolicyArtifact
```

A successful `TargetPolicyArtifact` carries target/comparison scope, base correlation, renderer identity/version, exact artifact payload/digest, equivalence evidence and intent provenance.

The renderer may not broaden, narrow or reinterpret APR intent. Unsupported semantics or inability to establish semantic equivalence fails closed and yields no executable artifact.

## Network Environment Operations

NEO consumes the already-rendered `TargetPolicyArtifact` plus actor/authority/precondition context and owns one controlled `NetworkOperation` lifecycle.

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

NEO does not recompute authorization, APR change design or provider rendering. Unknown/stale authority or preconditions fail closed. Identical retries are idempotent; uncertain apply is never blindly retried.

`Applied` is only a transport result. NEO `Verified` proves immediate artifact/application correspondence under the execution adapter contract, not final semantic convergence. Final convergence requires subsequent provider observation, configured-policy interpretation and APR comparison again.

## Strategic invariants

- ACC owns Application, Component and Interaction semantics; not deployment placement.
- AD owns logical deployment identity and Component-to-Resource placement truth.
- RC owns Resource identity/lifecycle, effective AddressSpace, Scope Affiliation and responsibility.
- current target RC network realization is at most one effective `HostAddress | Prefix` per Resource/time.
- AD references Resource only; it does not own address/endpoint realization.
- technical realization change does not redefine semantic authorization identity.
- Access Governance historical Request truth is distinct from current authorization truth.
- Required Policy Materialization is derived composition; unresolved is not empty required policy/APR drift.
- APR comparison is source-neutral exact effective permit-space algebra for complete comparable inputs.
- MVP automatic remediation is additive-only on `missing`; `excess` is not removal authority.
- provider interpretation/rendering remain adapters; APR core remains provider-neutral.
- provider rendering must prove semantic equivalence or fail closed.
- NEO owns execution lifecycle, not policy reinterpretation/placement/rendering.
- operation/application success is not final semantic convergence proof.
- no Shared Kernel is accepted between target BCs.

## Deferred strategic extensions

The following are explicit future extensions rather than current blockers:

- generalized approval semantics when several Responsibility Scopes apply to one governance side;
- Prefix-aware NEP query/matching semantics;
- multiple simultaneous Resource addresses/prefixes, interfaces, endpoint purpose, VIP and deployment-specific exposure;
- managed-policy ownership/removal semantics for APR `excess`;
- richer APR remediation/change-design vocabulary beyond additive `ENSURE-PERMIT`;
- production provider transport, generic rollback and multi-target transaction semantics.

## Strategic convergence disposition

The first MVP semantic vertical is now coherent from ACC/AD/RC through AG/AP, HostAddress-based RPM, APR exact comparison/additive remediation, provider rendering and NEO controlled execution.

No known S1 product decision remains open for this happy path. Deferred cases are explicit and fail closed or stay outside the path instead of being approximated.

Global G2 and implementation authorization are not implied. The next action should be an explicit implementation-authorization decision or a concrete affected-edge reopen, not more speculative domain expansion.
