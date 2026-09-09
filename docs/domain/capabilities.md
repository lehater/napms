# Domain capability ownership map

Status: `accepted NAPMS-DDD-001 living capability map; source DDD-BDM-010 extended through I19`.

A capability is not automatically a Bounded Context, service or deployment unit.

## Current capabilities

| Capability | Business question / outcome | Semantic owner / disposition |
|---|---|---|
| Connectivity Requirement Management | what semantic connectivity is needed by an identified dependent concern under defined applicability conditions? | **Connectivity Requirements** |
| Access Rule governance | what concrete Access Rule exists, with what state/authorization? | Access Policy |
| Desired-policy projections | which Rules are authorized/effective? | Access Policy |
| Domain Responsibility Assignment | who may perform which access-domain responsibility? | AM |
| Resource Scope Affiliation | which access-domain Resources belong to responsibility scope S at time T? | RC |
| Resource knowledge | what access-domain Resource/Endpoint/current realization exists? | RC |
| Application communication contract | what application/component/deployment/DCS semantics exist? | Application Communication Catalogue |
| Network / Forwarding State | where can traffic traverse? | NEP |
| Enforcement Selection | where is traffic evaluated? | NEP |
| Technical Access Evidence Management | what normalized source-qualified technical access list was observed/derived/imported? | Technical Access Evidence |
| Technical-to-Domain Access Resolution | what domain interaction(s) does a technical predicate represent/cover? | Access Policy Realization |
| Enforcement Policy Derivation / Quality / Optimization | what enforcement policy does the domain consider correct/preferred? | Access Policy Realization |
| Desired-vs-Configured Reconciliation | does configured evidence realize desired access and what semantic delta remains? | Access Policy Realization |
| Requirement-to-Policy Alignment | is current required connectivity covered by effective authorized policy? | non-peer composition over Connectivity Requirements + Access Policy |
| Scoped Connectivity Inventory | what Resources are local to one admitted responsibility scope and how do their component interactions relate to need/decision/policy truth? | non-peer application composition over AM + RC + ACC + Connectivity Requirements + Connectivity Decision + Access Policy |
| Access Rule Proposal Derivation | which resolved interactions not already represented should be surfaced as proposals? | non-peer application composition over APR + AP |
| Connectivity Impact Analysis | what depends on connectivity and what is the consequence of loss under a scenario? | cross-context analysis; no peer BC accepted |
| Source acquisition/parsing | obtain/parse traffic/device/file sources | adapter/mechanism |

## Responsibility scope and Resource affiliation

I16A accepts two independent capabilities around one stable scope reference:

```text
Resource Scope Affiliation
    Resource Catalogue
    -> which Resources belong to scope S at time T?

Domain Responsibility Assignment
    Authority Management
    -> which actions may actor A perform for scope S at time T?
```

Resource Scope Affiliation is time-qualified and non-identity. One Resource may be effectively affiliated with more than one Responsibility Scope when overlapping responsibility is real.

The relation does not itself grant authority and does not define catalogue visibility.

Authority Management adds independent action `ReadScopedConnectivity` for selecting/reading one responsibility scope as the local context of the owner workspace. Other reads/mutations remain independently admitted.

The first I16A model introduces no standalone Scope aggregate, hierarchy or lifecycle. A Responsibility Scope is a stable scope reference shared for correlation; Resource Catalogue owns Resource membership, while Authority Management owns actor/action eligibility.

## Scoped Connectivity Inventory

Scoped Connectivity Inventory is a non-peer application/read composition.

It answers:

> for one actor-admitted Responsibility Scope and logical time, which Resources are local, what Component Deployments are bound to them, with whom do they interact, and what independent Need/Decision/Policy truth can be safely summarized?

It creates no authoritative `ConnectivityStatus`, does not duplicate source-context truth and is not a new Bounded Context.

## Connectivity Requirement Management

Domain-owner confirmed on 2026-09-08:

- system/resource owners may declare connectivity need for their owned scope;
- declaring need does not authorize access;
- a different user with corresponding policy/security authority must approve or deny access.

Strategic invariants:

```text
Required != Authorized
Required != Configured/Observed
Authority-to-declare != Requirement
ConnectivityRequirement != AccessRequest/ticket
```

I13 Tactical DDD now accepts:
- stable surrogate `ConnectivityRequirementId`;
- active semantic uniqueness by Requirement Governance Scope + Dependent Component Deployment + exact Required Semantic Interaction;
- exact interaction = Source Component Deployment + Destination Component Deployment + immutable DCS revision;
- Applicability = Ongoing or absolute half-open window;
- lifecycle = `Active -> Retired`;
- justification/applicability mutable; dependent/interaction immutable.

Advanced alternative/conditional requirement semantics remain deferred.

## Network Enforcement Placement identity

Network / Forwarding State and Enforcement Selection are one NEP capability boundary for I19.

The first executable slice accepts:
- one exact source/destination IP pair as an ephemeral Traffic Relation;
- zero/one complete normalized Forwarding Path with ordered provider/path Traversal Points;
- stable Logical Firewall identity independent from provider realization;
- temporal Logical Firewall Correspondence and Enforcement Attachment;
- selection `Placed | NoEnforcement | NoForwardingPath | Ambiguous | Unknown`.

Multipath/ECMP and unrepresented forwarding discriminators remain explicit `Unknown` until a concrete environment requires and defines their semantics.

## Technical Access Evidence identity

Configured, TrafficDerived and Imported evidence are `SAME_CAPABILITY` at the normalized evidence level. They share source-qualified normalized predicate semantics, provenance, source scope and explicit evidence-time representation. Evidence does not authorize desired access. Universal freshness/coverage/confidence semantics are not part of the I17 core; they remain deferred until a concrete source/consumer contract gives them trustworthy meaning.

## Technical-to-Domain Access Resolution identity

Proposal-side and Reconciliation-side matching are `SAME_CAPABILITY`.

> same Technical Access Predicate + same RC/Application Communication Catalogue/effective-time knowledge -> same Domain Access Resolution, independent of consumer.

No consumer-specific resolution mode may change domain meaning.

## Access Rule Proposal Derivation

Proposal remains useful but non-peer while it has no independent identity, lifecycle, acceptance/rejection policy or authority.

## Access Policy Realization

This BC combines Technical-to-Domain Access Resolution, Enforcement Policy Derivation / Quality / Optimization and Desired-vs-Configured Reconciliation because one exact technical/domain coverage algebra must be used consistently in both directions.

I18 accepts and implements the first shared resolution slice:
- pairwise `Exact | Covers | CoveredBy | PartialOverlap | None`;
- overall `Exact | Covered | Partial | Ambiguous | Unresolved | Unknown`;
- exact unresolved technical remainder for supported exact-protocol predicates;
- no winner selection under ambiguity;
- explicit predicate-relevant Unknown;
- exact `asOf` and attributable TAE/RC/ACC provenance;
- one resolution meaning independent of proposal/reconciliation consumer.

Protocol Any remains an explicit first-slice Unknown until a protocol-wide port-applicability/difference model is accepted.

Requirement-to-Policy Alignment is deliberately outside APR: it compares `NEEDED` with effective `AUTHORIZED`; APR compares authorized/desired policy with technical realization/evidence.

I14 accepted Requirement-centric outcomes:
- `Covered`;
- `Uncovered`;
- `NotCurrent`;
- `Unknown`.

`Denied` remains deferred because current Access Policy truth does not persist a durable NotAllowed decision. Policy-centric orphan detection remains deferred until an operator view with accepted cross-scope authority semantics requires it.

An actor admitted to `ReadConnectivityRequirement` may see the derived alignment status for that Requirement. Rule-level evidence/details remain separately protected by Access Policy read authority.

## Source acquisition and firewall semantics

NetFlow/syslog capture, vendor polling/parsers, CSV/XLSX import and raw config storage remain adapters/mechanisms. Zones/interfaces/default deny belong to NEP/firewall interpretation, not Technical Access Evidence.

## Strategic DDD closure

`DDD-BDM-010` remains the source Strategic DDD baseline. The living `NAPMS-DDD-001` model has since been extended by accepted Connectivity Requirements, Connectivity Decision and I16A responsibility-scope semantics. Historical DDD-BDM-010 evidence remains provenance rather than the count/name of the current living context set.

The legacy-reconstruction scorer was not rerun for the accepted DDD-BDM-010 baseline. No scorer metrics are claimed by the NAPMS living model; historical scoring evidence remains in the source reconstruction repository.

Strategic DDD is closed for the current scope. This statement does not start or imply Tactical DDD.
