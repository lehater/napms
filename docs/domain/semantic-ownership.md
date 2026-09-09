# Semantic Ownership

Status: `accepted NAPMS-DDD-001 / I20 WP-0 current semantic ownership`.

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
| technical↔domain access correspondence and enforcement realization | **Access Policy Realization** | I18 resolution: TAE + RC + Application Communication Catalogue; I20 derivation/reconciliation: Access Policy + NEP + explicitly selected/configured TAE projection + source/scope contract | Domain Access Resolution / desired enforcement policy / Policy Reconciliation |

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

It owns:
- normalized forwarding/path meaning used for placement;
- Logical Firewall identity;
- temporal provider-realization correspondence;
- Enforcement Attachment;
- Enforcement Selection.

It does not own:
- Resource/Endpoint identity;
- authorization or Access Rule lifecycle;
- configured technical access evidence;
- desired-vs-configured satisfaction/change;
- vendor configuration or provider execution.

The first I19 slice is fail-closed when endpoint-pair semantics are insufficient for routing truth (for example unsupported forwarding discriminators or multipath).

## Access Policy Realization authority

Access Policy Realization owns the interpretation/decision layer above evidence:

```text
Technical Access Evidence
    -> what domain interactions does it represent?

Access Policy + NEP
    -> what vendor-neutral enforcement policy is technically capable of expressing the effective desired access?

configured effective-policy evidence + same managed scope
    -> does configured enforcement satisfy that desired policy and what exact semantic delta remains?
```

### Consistency invariant

The same Technical Access Predicate against the same authoritative catalogue/resource knowledge and effective time must not resolve to different Domain Interactions because one consumer is Proposal derivation and another is Reconciliation.

I18 makes that invariant executable. Domain Access Resolution owns exact overlap witnesses, ambiguity, predicate-relevant Unknown and unresolved technical remainder.

I20 adds a policy-level interpretation without changing I18 meaning:
- desired enforcement is derived from effective desired Access Policy and NEP placement at one explicit `asOf`;
- the first Enforcement Target is Logical Firewall + Enforcement Attachment;
- configured TAE material is not directly “current configured policy”;
- a complete comparison requires an explicit managed reconciliation-scope/source contract proving the selected TAE source/scope represents the same target and policy partition;
- configured absence is meaningful only when that contract proves a complete effective Permit set at the same instant;
- raw Block/order/default/vendor evaluation is not interpreted generically;
- exact common/missing/extra regions are APR truth;
- `Add | Remove | Replace | No-op` is semantic delta only and grants no device-mutation authority.

Desired Enforcement Policy and Policy Reconciliation remain derived on demand in the first I20 slice; no APR persistence lifecycle is implied.

## Proposal ownership

Access Rule Proposal is an application-level handoff.

It carries an exact candidate Rule semantic identity and accepted proposal authority scope. It owns no final permission decision and no authoritative Rule ID/state.

Connectivity Decision consumes the proposal subject/scope; only Access Policy materializes/resolves authoritative Access Rules from an effective Allowed Decision.

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
```

No Requirement, evidence or proposal silently becomes authorization.
