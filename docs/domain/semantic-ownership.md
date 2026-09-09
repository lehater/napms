# Semantic Ownership

Status: `accepted NAPMS-DDD-001 / I22 current semantic ownership`.

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
| forwarding and enforcement relevance | **Network Enforcement Placement** | provider/network observations + corrections | path/Logical Firewall/Enforcement Attachment semantics |
| normalized source-qualified technical access evidence | **Technical Access Evidence** | device/traffic/import adapters and external sources | Technical Access Evidence Set / Entry |
| technical↔domain access correspondence, enforcement realization and target representation equivalence | **Access Policy Realization** | I18 resolution: TAE + RC + Application Communication Catalogue; I20 derivation/reconciliation: Access Policy + NEP + explicitly selected/configured TAE projection + source/scope contract; I21 rendering: accepted desired enforcement intent + renderer contract | Domain Access Resolution / desired enforcement policy / Policy Reconciliation / Rendered Configuration |
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

It does not own the truth that Y is desired, authorized or domain-valid.

Evidence kinds:

```text
Configured
TrafficDerived
Imported
```

Source-specific parsing/collection is outside the BC.

## Network Enforcement Placement authority

Network Enforcement Placement owns the claim:

> for exact endpoint-pair traffic relation R at logical time T, normalized forwarding knowledge places traffic through path P, whose provider/path attachment points correspond to Logical Firewall enforcement placements E.

It owns normalized forwarding/path meaning, Logical Firewall identity, temporal provider correspondence, Enforcement Attachment and Enforcement Selection. It does not own authorization, desired-vs-configured satisfaction, vendor configuration or provider execution.

## Access Policy Realization authority

Access Policy Realization owns the interpretation/decision layer above evidence and the exact target representation of accepted desired enforcement intent. I21 rendering remains derived on demand and does not prove device application.

## Network Environment Operations authority

Network Environment Operations owns the provider/device operation lifecycle downstream of rendering:
- NEO-owned `OperationTarget` is a projection of the upstream enforcement target, not a redefinition of APR/NEP identity;
- `operation_id` binds exactly one target + artifact digest and is the first-slice idempotency key;
- mutation authority is consumed through an explicit Authority Management-facing port and read access does not imply mutation permission;
- pre-check/current target revision and conditional apply provide optimistic concurrency;
- apply result is distinct from final verification;
- final outcomes are `Verified | PreconditionFailed | Rejected | Drift | Unknown`;
- `Verified` requires post-check evidence matching the requested artifact digest;
- Unknown apply is never converted into success and is not blindly retried;
- operation provenance preserves pre/apply/post evidence and correlation.

The current I22 executable adapter is a deterministic in-process stub because no real lab is available. Stub success proves the operation semantics only; it is not evidence of real Cisco ASA transport compatibility. The first slice uses an in-memory operation repository and therefore does not claim crash-durable execution audit.

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
Domain resolution known / ambiguous / unresolved
Enforcement policy derived
Configured evidence observed
Satisfied
Rendered representation exists
Network operation attempted
Applied response observed
Verified target state observed
```

A rendered representation does not imply provider/device application, and an apply response does not imply verification. No Requirement, evidence or proposal silently becomes authorization.
