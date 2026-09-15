# NAPMS Strategic DDD model

Status: `current target`.

## Purpose

Define the target semantic ownership of NAPMS independently from current physical packages, persistence schemas and compatibility runtime structures. This is the primary Strategic DDD contract for new design work.

Current implemented/as-built architecture is documented separately in `docs/architecture/current-architecture.md`. As-built compatibility concepts do not become target Bounded Contexts merely because current code still uses them.

## Core semantic ladder

NAPMS keeps the following meanings distinct:

```text
Observed != Recognized != Needed != Authorized != Materialized != Realized != Executed
```

- **Observed** — technical material was collected/imported/reported.
- **Recognized** — evidence has been normalized/correlated enough for a consumer to interpret it.
- **Needed** — business/application connectivity is required.
- **Authorized** — the exact governed interaction subject currently has the required consent.
- **Materialized** — semantic authorization has been expanded into complete target-specific required technical policy.
- **Realized** — configured effective policy is semantically equal to required effective policy for the comparison scope.
- **Executed** — a concrete target mutation operation has been attempted and has an explicit operational outcome.

No downstream state implies an upstream state automatically. In particular, observed/configured access does not imply authorization, and successful device transport does not imply semantic realization.

## Target Bounded Contexts

| Bounded Context | Semantic center | Authoritative responsibility |
|---|---|---|
| Business Connectivity (BC) | why application connectivity is needed | Business Process, Connectivity Need, current business justification/attribution |
| Access Governance (AG) | whether the exact governed interaction has required consent | Access Request history, bilateral approval obligations/decisions, current grant/withdrawal |
| Access Policy (AP) | what semantic network access is currently authorized | authoritative current Policy Rule truth |
| Authority Management (AM) | who may perform a domain action for scope/time | effective actor/action/scope authority and authority-assignment semantics |
| Resource Catalogue (RC) | what access-domain resources exist and how they are currently realized | Resource identity/lifecycle, current AddressSpace, scope affiliation and responsibility |
| Application Communication Catalogue (ACC) | what applications/components may communicate and what the traffic contract means | Application, Component, Interaction and immutable InteractionContractRevision |
| Application Deployment (AD) | where logical application deployments place Components | ApplicationDeployment identity/continuity and current Component-to-Resource placement-set truth |
| Network Enforcement Placement (NEP) | where a technical pair may be enforced | candidate Firewall/policy-locator relevance |
| Technical Access Evidence (TAE) | what source-qualified technical material was observed/reported/imported | canonical normalized immutable evidence plus source/time/provenance |
| Access Policy Realization (APR) | how configured effective access compares with required effective access | realization assessment, semantic delta and verified source-neutral additive change intent |
| Network Environment Operations (NEO) | how one verified target mutation is executed and explained | controlled operation identity, authority, preconditions/concurrency, outcome and provenance |

## Capabilities that are not peer Bounded Contexts

The following are deliberate non-peer capabilities/compositions:

- **Required Policy Materialization (RPM)** — derived cross-context composition producing complete target-specific required policy or explicit unresolved state.
- **Provider Policy Interpreter (PPI)** — integration capability translating provider-native configured policy into source-neutral effective semantics.
- **Provider Policy Renderer** — integration capability translating verified source-neutral change intent into provider/target-specific representation without changing meaning.
- **Technical Evidence Acquisition / Collectors** — source-specific collection/translation capabilities that feed TAE.
- **Required Access Matrix composition** — selected first implementation slice deriving pre-authorization technical connectivity from ACC + AD + RC.

None of these owns independent authoritative business truth merely because it orchestrates or derives data.

## Shared model rule

No DDD Shared Kernel is accepted between target Bounded Contexts.

Cross-context references are opaque semantic references or published values, not persistence foreign keys into peer-owned tables and not imports of peer-private Domain models.

## Application Communication Catalogue

ACC answers:

> what logical application interaction exists and what immutable traffic contract revision does it mean?

ACC owns:

```text
Application
Component
Interaction
InteractionContractRevision
TrafficAlternative
```

`Interaction` is a stable directed Component-to-Component template. A material traffic-semantics change creates a new immutable `InteractionContractRevision` while preserving Interaction identity.

All traffic alternatives in one revision form one atomic decision-relevant contract. Consumers may not silently select only a convenient subset of alternatives when the revision is the governed/materialized subject.

ACC does not own Resource placement, Resource addresses, deployment lifecycle or authority.

## Application Deployment

AD answers:

> which logical deployment of an Application exists and on which Resources are its Components currently placed?

AD owns stable `ApplicationDeployment` identity/continuity and current placement-set truth:

```text
ComponentPlacement = (ComponentRef, ResourceRef)

CurrentPlacements(applicationDeploymentRef, componentRef)
    = Set<ResourceRef>
```

Current target semantics allow zero, one or many Resources for a Component. The exact same `(ComponentRef, ResourceRef)` pair may not occur twice in one ApplicationDeployment.

`ComponentPlacement` is a relation value, not an independently identified/lifecycled entity in the current target.

ApplicationDeployment identity is independent of its current placement set. Ordinary scaling, Resource migration, placement replacement and Resource-address change do not by themselves redefine deployment identity.

A complete empty placement set is distinct from an unavailable/unresolved placement result. Consumers may not collapse unresolved to empty or choose one arbitrary placement when several exist.

AD does not own Resource addresses, Resource responsibility, interaction traffic or runtime process/container identity.

## Resource Catalogue

RC answers:

> which access-domain Resource exists, how is it currently realized, and with which responsibility scope/responsibility facts is it associated?

RC owns stable Resource identity and current target realization:

```text
Resource
AddressSpace = HostAddress | Prefix
ResourceScopeAffiliation
ResourceResponsibility
```

For the current target scope, at most one effective AddressSpace exists for one Resource at one logical time.

Changing AddressSpace does not redefine Resource identity, ACC identity or ApplicationDeployment identity.

`ResourceScopeAffiliation` correlates a Resource to a `ResponsibilityScopeRef`; it does not grant actor authority. `ResourceResponsibility` is operational/business responsibility/contact information and likewise does not grant actor authority.

Multi-address/VIP/interface-purpose semantics are not part of the current target unless introduced by a later accepted requirement.

## Business Connectivity

BC answers:

> why is this application-semantic connectivity needed?

BC owns Business Process and Connectivity Need meaning, including the current business justification/attribution of the need.

A Connectivity Need references stable ACC Interaction meaning. It is not itself authorization, technical placement or firewall policy.

BC does not own bilateral consent or actor authority.

## Authority Management

AM answers one exact question:

```text
ActorRef + ActionRef + ResponsibilityScopeRef + effectiveTime
    -> EffectiveAuthority
```

AM owns the authority-assignment semantics required to derive:

```text
Admitted(authorityEvidence)
| Denied
| Unknown
```

Authority is independent from Resource responsibility/contact, Resource Scope Affiliation, application owner metadata or UI selection.

Unknown/ambiguous authority never degrades to admission. Protected consumers fail closed according to their accepted contract.

Responsibility Scope is a stable correlation value shared semantically with RC and AG; it is not a separate Shared Kernel aggregate.

## Access Governance

AG answers:

> has the exact deployment-level interaction received and retained the required bilateral consent?

The governed subject is exactly:

```text
GovernedInteractionSubject =
    InteractionContractRevisionRef
  + sourceApplicationDeploymentRef
  + destinationApplicationDeploymentRef
```

Placement ResourceRefs and Resource AddressSpaces are not part of governed-subject identity.

AG derives approval obligations from the applicable source/destination deployment placements and their RC Responsibility Scope affiliations. AM supplies actor/action/scope/time authority for request/approval/withdrawal actions.

For the current target governance contract:

- source-side and destination-side obligations are independent;
- grant requires the accepted required obligations to be satisfied;
- rejection does not create a deny Policy Rule;
- withdrawal can remove current grant;
- a material obligation change may require withdrawal/re-evaluation;
- no silent restoration occurs from old historical approvals;
- unresolved or ambiguous required obligation/authority facts fail closed.

Where the current MVP contract requires one distinct applicable Responsibility Scope per side, zero or several applicable scopes are unresolved rather than arbitrarily selected.

AG emits explicit current authorization facts to AP; AP does not reconstruct bilateral governance.

## Access Policy

AP answers:

> what semantic network access is currently authorized?

AP owns current authoritative `PolicyRule` truth for the exact governed subject.

At most one current authoritative Rule meaning exists per governed subject. Equivalent/retried grant delivery is semantically idempotent and does not create duplicate authorization meaning.

AP consumes explicit AG facts:

```text
AuthorizationGranted(subject, provenance)
AuthorizationWithdrawn(subject, provenance)
```

Pending/rejected governance does not create a deny Rule. Withdrawal prevents old grants from silently restoring current authorization. A later explicit grant may re-establish current authorization for the same subject.

Technical placement/address/materialization failure does not erase semantic authorization; downstream materialization reports that technical incompleteness separately.

## Selected first implementation slice — Required Access Matrix

The first implementation slice intentionally stops before governance/authorization/enforcement placement:

```text
PolicyBuildSelection[]
  each item =
      InteractionContractRevisionRef
    + sourceApplicationDeploymentRef
    + destinationApplicationDeploymentRef

            + ACC traffic contract
            + AD current placements
            + RC current AddressSpace
                    |
                    v
          Required Access Matrix
                    |
                    +--> table
                    `--> vendor-neutral export
```

This is an application-level derived composition, not a new Bounded Context and not Access Policy.

For each explicit selection item, the composition:

1. loads the exact immutable InteractionContractRevision;
2. resolves the source and destination Components from that revision;
3. loads the exact source/destination ApplicationDeployments;
4. loads the complete current placement sets for those Components;
5. resolves every placed Resource to its current AddressSpace;
6. expands the full source-placement × destination-placement × traffic-alternative cross-product;
7. returns a source-neutral technical connectivity matrix with sufficient provenance to explain why each row exists.

No automatic “all matching deployments communicate” inference is accepted. The exact deployment pair is explicit input.

Missing/unresolved required ACC/AD/RC input is never silently treated as empty. The concrete result shape, partial-vs-all-or-nothing presentation behavior, deduplication/provenance projection and read-consistency mechanism remain S3 Architecture decisions unless already fixed by the MVP requirement.

This matrix means **technical connectivity implied by the selected application/deployment model**. It does not mean `Authorized`, does not select a Firewall and does not compare configured policy.

## Required Policy Materialization

RPM is the downstream derived composition for **authorized** policy and must not be conflated with the first Required Access Matrix slice.

Conceptually:

```text
current AP PolicyRule
+ exact ACC InteractionContractRevision
+ exact AD source/destination deployments and complete placements
+ RC current AddressSpace
+ NEP candidate targets/policy locators
    -> TargetRequiredPolicy[] | Unresolved
```

RPM owns no independent authoritative policy identity.

For every authorized subject it preserves the full applicable source-placement × destination-placement × traffic-alternative product and every relevant NEP candidate target. Missing/unresolved input is explicit unresolved state, never empty policy.

For the currently accepted enforcement-materialization scope, unsupported address/placement/target semantics fail closed rather than being approximated. A target-specific `ComparisonScope` is based on the Firewall plus policy/ACL locator supplied by NEP.

## Network Enforcement Placement

NEP answers:

> for this technical source/destination pair, which Firewall/policy locators are relevant candidate enforcement locations?

NEP owns candidate relevance, not authorization, configured policy meaning or change intent.

Multiple candidate targets are retained. NEP does not silently choose one winner. Candidate relevance is not proof of full end-to-end traversal.

## Technical Access Evidence

TAE answers:

> what source-qualified technical material has been recorded, and exactly what did that source claim/observe/import?

TAE owns canonical normalized immutable evidence sets/entries, source qualification, source-time/recording-time distinction and provenance.

TAE does not initiate collection. Polling cadence, scheduling, retries, credentials, source transport and provider-specific acquisition belong to Technical Evidence Acquisition/Collector capabilities.

Evidence never manufactures authorization, desired policy or mutation intent.

## Provider Policy Interpreter

PPI is an integration capability that interprets provider-native configured-policy semantics — including ordering, deny/default behavior, objects/groups and other supported provider constructs — into:

```text
ConfiguredEffectivePolicySnapshot {
    comparisonScope
    effectivePermitSpace
    completeness
    freshness
    provenance
    unsupportedSemantics
}
```

PPI may consume provider source directly, source-qualified TAE configured evidence under contract, or both. APR never parses provider-native syntax.

## Access Policy Realization

APR answers:

> for one exact comparable policy scope, how does configured effective access differ from required effective access, and what safe source-neutral additive change intent can be verified?

APR consumes complete comparable required/configured effective permit spaces and derives:

```text
common  = required ∩ configured
missing = required - configured
excess  = configured - required
```

Assessment semantics:

```text
Realized     <=> missing is empty AND excess is empty
Drift        <=> comparable AND (missing non-empty OR excess non-empty)
Uncomparable <=> scope mismatch, incomplete/unknown/unsupported required comparison input
```

The current accepted automated remediation boundary is additive only:

```text
missing != empty -> MAY design ENSURE-PERMIT
excess != empty  -> report/explain only; no automatic removal authority
Realized         -> no intent
Uncomparable     -> no intent
```

A `VerifiedChangeIntent` proves the accepted additive semantic effect against the configured basis. It does not itself prove final `Realized`; final convergence requires later configured observation and comparison.

The current APR target does not require a durable editable remediation aggregate merely to store a derived calculation. Persistence/materialization/indexing for scale is Architecture, not domain ownership.

## Provider Policy Renderer

Renderer is an integration capability that consumes:

```text
VerifiedChangeIntent
+ provider capabilities
+ exact target/base correlation
```

and produces `TargetPolicyArtifact` only when the provider representation is semantically equivalent to the verified source-neutral intent.

Renderer may not broaden or narrow the verified meaning. Provider-specific syntax remains outside APR Domain.

## Network Environment Operations

NEO answers:

> how is one verified target artifact applied under explicit authority, preconditions and concurrency, and what operational outcome resulted?

Conceptually:

```text
TargetPolicyArtifact
+ operationId
+ actor / mutation authority
+ base target revision/correlation
    -> authority check
    -> precheck
    -> conditional apply
    -> postcheck
    -> Verified | Rejected | PreconditionFailed | Drift | Unknown
```

NEO does not recompute authorization, target selection, APR comparison/change design or provider rendering.

Retries are idempotent by operation identity. An uncertain apply outcome is not blindly retried. Transport acceptance alone is not semantic convergence.

Technical evidence acquisition is a separate semantic concern. NEO and collectors may share lower-level device/client infrastructure only as an Architecture choice that preserves their distinct ports and responsibilities.

## Cross-cutting strategic invariants

1. Every authoritative semantic fact/decision has one clear owner.
2. A Bounded Context is a semantic ownership boundary, not automatically a service, database, team or deployment unit.
3. Cross-context orchestration owns no peer business truth.
4. Unknown/incomplete information never silently becomes absence, denial, empty policy or success.
5. Technical identity/realization changes do not silently redefine business/application semantic identity.
6. Authentication identity does not itself grant business authority.
7. Resource responsibility/scope affiliation does not itself grant business authority.
8. Provider-native syntax and transport remain at integration boundaries.
9. Historical/current evidence or authorization provenance is not rewritten merely because current catalogue/realization data changes.
10. Physical persistence colocation does not permit peer-private table coupling.

## Current target exclusions

The following are not part of the currently accepted target semantics unless a later requirement explicitly introduces them:

- generic process/workflow lifecycle beyond accepted BC-specific meanings;
- ACC draft/publish/versioning workflow beyond immutable InteractionContractRevision semantics;
- rich AD deployment-state/history model or independently identified placement facts;
- nested groups, role inheritance, ABAC/policy-expression language, quorum/multi-actor authority policy;
- generalized multi-scope approval rules beyond accepted AG contracts;
- generalized multi-address/VIP/interface-purpose Resource realization;
- automatic destructive removal/narrowing of excess configured policy;
- durable editable APR remediation-plan lifecycle without a real user journey;
- provider transport/rollback/multi-target transaction semantics without accepted operational requirements.

These are exclusions/boundaries of current design, not a roadmap obligation.

## As-built compatibility relation

The current product may still contain concepts such as `Connectivity Requirement`, `Connectivity Decision`, ACC compatibility `ComponentDeployment`, `DeploymentResourceBinding`, `DirectedInteractionIdentity`, `ResourceEndpoint` and older APR/Realization workflow shapes.

Those concepts are documented in as-built requirements, Tactical/architecture/engineering contracts when needed to reconstruct current behavior. They do not override the target ownership defined here.
