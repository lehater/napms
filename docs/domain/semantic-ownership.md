# Semantic Ownership

Status: `accepted NAPMS-DDD-001 current semantic ownership`.

This file defines semantic ownership, not runtime/service ownership.

## Ownership map

| Knowledge / decision | Semantic owner | Upstream authority / source | Primary result |
|---|---|---|---|
| semantic connectivity need identity/lifecycle/applicability/justification | **Connectivity Requirements** | AM-authorized responsible actor + ACC interaction facts | Connectivity Requirement |
| final permission decision for exact proposed connectivity, including reason/validity/supersession | **Connectivity Decision** | AM-authorized deciding principal + proposal subject + referenced evidence | Connectivity Decision |
| requirement-to-policy coverage status | **non-peer application composition** | Connectivity Requirements + effective Access Policy | Covered / Uncovered / NotCurrent / Unknown |
| Access Rule identity/properties/state/authorization | **Access Policy** | effective Allowed Connectivity Decision + catalogue facts + AM-authorized operation | Access Rule + desired projections |
| scoped actor authority/eligibility | **Authority Management** | assignment/delegation/transfer/revocation decisions | Effective Authority / Responsibility Assignment |
| Resource membership in one responsibility scope/time | **Resource Catalogue** | authoritative organizational/resource affiliation facts | Resource Scope Affiliation |
| Resource/Endpoint/current address realization | **Resource Catalogue** | trusted inventory/network facts | Resource/Endpoint/current realization |
| scoped resource-centric connectivity inventory | **non-peer application composition** | AM + RC + ACC + Connectivity Requirements + Connectivity Decision + Access Policy | Scoped Connectivity Inventory |
| application/component communication contract | **Application Communication Catalogue** | authorized catalogue sources | Application/Component/DCS/Deployment |
| enforcement-target relevance and applicable policy/ACL locators | **Network Enforcement Placement** | current routing/interface state + configured candidate overrides + source-specific locator bindings | Firewall candidate/target references + policy locators |
| normalized source-qualified technical access evidence | **Technical Access Evidence** | device/traffic/import adapters and external sources | Technical Access Evidence Set / Entry |
| effective-policy realization assessment, semantic delta, change design, pre-change semantic verification and target representation equivalence | **Access Policy Realization** | target-specific required-policy contract + comparable configured effective-policy contract | Realization Assessment / Semantic Delta / Policy Change Design / Verification Result / Rendered Configuration |
| provider/device operation identity, concurrency, mutation outcome and execution provenance | **Network Environment Operations** | rendered configuration projection + Authority Management mutation admission + target/provider observations | Network Operation Result |

## Responsibility Scope / Resource affiliation ownership

I16A separates two truths that share the same stable scope reference:

```text
Resource Catalogue:
Resource --Resource Scope Affiliation--> Responsibility Scope

Authority Management:
Actor --Responsibility Assignment(action,time)--> Responsibility Scope
```

Resource Catalogue owns whether Resource R belongs to Responsibility Scope S at logical time T.

Authority Management owns whether Actor A may perform action X for Scope S at logical time T.

Neither truth implies the other:

```text
Resource in scope
!= actor authorized

actor authorized for scope
!= Resource in scope
```

Current global catalogue visibility is a third independent concern. A foreign Resource may be readable without being local to the actor's selected responsibility scope.

The first workspace-specific Authority action is `ReadScopedConnectivity`. It admits use of one scope as local workspace context only. It does not imply any Requirement/Decision/Rule detail read or mutation action.

## Scoped Connectivity Inventory ownership

Scoped Connectivity Inventory is a non-peer application/read composition.

It correlates:
- `ReadScopedConnectivity` scope admission from Authority Management;
- effective Resource Scope Affiliations and Resource realization from Resource Catalogue;
- Component Deployment / DeploymentResourceBinding / DCS from Application Communication Catalogue;
- accepted safe summaries from Connectivity Requirements, Connectivity Decision and Access Policy.

It owns no new business identity, lifecycle, status or persistence truth.

## Connectivity Decision authority

Connectivity Decision owns the claim:

> for exact proposed subject R in governance scope S, final decision D was Allowed/NotAllowed, for validity V, for reason/provenance P.

It does not own:
- whether connectivity is required;
- who has decision authority;
- Access Rule state/lifecycle;
- catalogue/resource truth.

Authority Management owns `DecideConnectivity` / `ReadConnectivityDecision` eligibility.

Connectivity Requirements may supply evidence of need, but `Required != Authorized`.

## Technical Access Evidence authority

Technical Access Evidence owns the claim:

> source X provided or allowed us to derive technical access material Y for scope/time T.

It does not own the truth that Y is desired, authorized or correctly realized.

Evidence kinds:

```text
Configured
TrafficDerived
Imported
```

Source-specific parsing/collection is outside the BC.

## Network Enforcement Placement authority

Network Enforcement Placement owns target relevance for supplied technical traffic pairs using its current network-state and override semantics. It also owns the applicable policy/ACL locator information needed to identify the relevant policy surface on a returned Firewall.

NEP does not own authorization, configured policy contents, desired-vs-configured reconciliation, policy change design, rendering or provider execution.

Once a target/policy locator has been supplied downstream, APR does not reevaluate why NEP selected it.

## Access Policy Realization authority

Access Policy Realization owns the semantic comparison and transformation layer for one supplied technical policy target:

```text
required effective access
        versus
configured effective access
```

APR owns:

- realization assessment for trustworthy comparable inputs;
- exact `common / missing / excess` semantic delta;
- policy-change design over that delta;
- semantic pre-change verification of the proposed resulting policy;
- semantics-preserving target-specific rendering;
- supporting explanation/attribution of technical access where required by an APR use case.

APR does not own target relevance, Access Rule authorization, catalogue identities, evidence source truth or provider/device mutation execution.

APR results are derived unless a later accepted product lifecycle establishes independent durable APR state. Data-local indexes/worksets used to compute large policy spaces do not become authoritative peer business truth.

Canonical APR framing: `docs/domain/access-policy-realization/README.md`.

## Network Environment Operations authority

Network Environment Operations owns the provider/device operation lifecycle downstream of rendering:
- NEO-owned `OperationTarget` is a projection of the upstream technical target, not a redefinition of its identity;
- `operation_id` binds exactly one target + artifact digest and is the first-slice idempotency key;
- mutation authority is consumed through an explicit Authority Management-facing port and read access does not imply mutation permission;
- pre-check/current target revision and conditional apply provide optimistic concurrency;
- apply result is distinct from final verification;
- final outcomes are `Verified | PreconditionFailed | Rejected | Drift | Unknown`;
- `Verified` requires post-check evidence matching the requested artifact digest;
- Unknown apply is never converted into success and is not blindly retried;
- operation provenance preserves pre/apply/post evidence and correlation.

The current executable adapter is a deterministic in-process stub because no real lab is available. Stub success proves the operation semantics only; it is not evidence of real Cisco transport compatibility. The current in-memory operation repository does not claim crash-durable execution audit.

## Proposal ownership

Access Rule Proposal is an application-level handoff. It carries an exact candidate Rule semantic identity and accepted proposal authority scope. It owns no final permission decision and no authoritative Rule ID/state.

## Independent truth dimensions

```text
Connectivity requirement exists
Proposal exists
Decision exists: Allowed | NotAllowed
Rule exists
Active / Inactive
Technical evidence exists
Target relevance established upstream
Required effective target policy available
Configured effective target policy available
Realization assessment computed
Semantic delta computed
Policy change designed
Proposed resulting policy semantically verified
Rendered representation exists
Network operation attempted
Applied response observed
Verified target state observed
```

No Requirement, evidence, target selection, reconciliation result, rendered representation or apply response silently becomes another context's authoritative truth.
