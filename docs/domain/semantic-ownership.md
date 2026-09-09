# Semantic Ownership

Status: `accepted NAPMS-DDD-001 / I15 current semantic ownership`.

This file defines semantic ownership, not runtime/service ownership.

## Ownership map

| Knowledge / decision | Semantic owner | Upstream authority / source | Primary result |
|---|---|---|---|
| semantic connectivity need identity/lifecycle/applicability/justification | **Connectivity Requirements** | AM-authorized responsible actor + ACC interaction facts | Connectivity Requirement |
| final permission decision for exact proposed connectivity, including reason/validity/supersession | **Connectivity Decision** | AM-authorized deciding principal + proposal subject + referenced evidence | Connectivity Decision |
| requirement-to-policy coverage status | **non-peer application composition** | Connectivity Requirements + effective Access Policy | Covered / Uncovered / NotCurrent / Unknown |
| Access Rule identity/properties/state/authorization | **Access Policy** | effective Allowed Connectivity Decision + catalogue facts + AM-authorized operation | Access Rule + desired projections |
| scoped actor authority/eligibility | **Authority Management** | assignment/delegation/transfer/revocation decisions | Effective Authority / Responsibility Assignment |
| Resource/Endpoint/current address realization | **Resource Catalogue** | trusted inventory/network facts | Resource/Endpoint/current realization |
| application/component communication contract | **Application Communication Catalogue** | authorized catalogue sources | Application/Component/DCS/Deployment |
| forwarding and enforcement relevance | **Network Enforcement Placement** | provider/network observations + corrections | path/Logical Firewall/Enforcement Attachment semantics |
| normalized source-qualified technical access evidence | **Technical Access Evidence** | device/traffic/import adapters and external sources | Technical Access Evidence Set / Entry |
| technical↔domain access correspondence and enforcement realization | **Access Policy Realization** | TAE + AP + RC + Application Communication Catalogue + NEP | Domain Access Resolution / business-optimal enforcement policy / reconciliation result |

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

## Access Policy Realization authority

Access Policy Realization owns the interpretation/decision layer above evidence:

```text
Technical Access Evidence
    -> what domain interactions does it represent?

Access Policy + NEP
    -> what technical/enforcement policy should be considered correct?

configured evidence + required semantics
    -> does reality satisfy desired policy and what semantic delta remains?
```

### Consistency invariant

The same Technical Access Predicate against the same authoritative catalogue/resource knowledge and effective time must not resolve to different Domain Interactions because one consumer is Proposal derivation and another is Reconciliation.

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
