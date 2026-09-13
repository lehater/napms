# Domain capability ownership map

Status: `accepted NAPMS-DDD-001 living capability map`.

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
| Enforcement Target Relevance | which Firewalls/policy locators are relevant for supplied technical traffic pairs? | NEP |
| Technical Access Evidence Management | what normalized source-qualified technical access material was observed/derived/imported? | Technical Access Evidence |
| Policy Realization Assessment | how exactly does configured effective access realize required effective access on a supplied target? | Access Policy Realization |
| Semantic Policy Reconciliation | what effective access is common, missing and excessive for a comparable target policy? | Access Policy Realization |
| Policy Change Design | what vendor-neutral policy edit should remove the semantic delta? | Access Policy Realization |
| Proposed Change Verification | would the proposed resulting effective policy exactly satisfy the required policy without unintended access? | Access Policy Realization |
| Target Policy Rendering | how is verified policy intent represented for a concrete target without changing semantics? | Access Policy Realization |
| Technical Access Attribution / Explanation | what domain/business meaning can be attributed to a technical access region for explanation or diagnostics? | Access Policy Realization supporting capability |
| Requirement-to-Policy Alignment | is current required connectivity covered by effective authorized policy? | non-peer composition over Connectivity Requirements + Access Policy |
| Scoped Connectivity Inventory | what Resources are local to one admitted responsibility scope and how do their component interactions relate to need/decision/policy truth? | non-peer application composition over AM + RC + ACC + Connectivity Requirements + Connectivity Decision + Access Policy |
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

I13 Tactical DDD accepts:
- stable surrogate `ConnectivityRequirementId`;
- active semantic uniqueness by Requirement Governance Scope + Dependent Component Deployment + exact Required Semantic Interaction;
- exact interaction = Source Component Deployment + Destination Component Deployment + immutable DCS revision;
- Applicability = Ongoing or absolute half-open window;
- lifecycle = `Active -> Retired`;
- justification/applicability mutable; dependent/interaction immutable.

Advanced alternative/conditional requirement semantics remain deferred.

## Network Enforcement Placement

NEP determines relevant Firewalls and applicable policy/ACL locators for supplied technical traffic pairs from current collected routing/interface state plus explicit active override rules.

Its target semantics are defined by `docs/domain/network-enforcement-placement/target-tactical-model.md` and ADR-018.

APR consumes the target-specific outcome as upstream input and does not re-run or reinterpret NEP relevance reasoning.

## Technical Access Evidence

Configured, TrafficDerived and Imported evidence are one source-qualified evidence capability at the normalized evidence level. They share normalized predicate semantics, provenance, source scope and evidence-time representation. Evidence does not authorize desired access.

Completeness/currentness that a downstream comparison requires must be established by an explicit source/consumer contract; an evidence record does not acquire that meaning merely because it exists.

## Access Policy Realization

APR is a separate bounded context whose current canonical problem statement is:

- `docs/domain/access-policy-realization/README.md`.

Its target capability chain is:

```text
supplied target + required effective policy
                +
comparable configured effective policy
                |
                v
Policy Realization Assessment
                |
                v
Semantic Policy Reconciliation
                |
                v
Policy Change Design
                |
                v
Proposed Change Verification
                |
                v
Target Policy Rendering
```

Core direction:

- compare **effective technical access semantics**, not textual rule/configuration identity;
- preserve exact `common / missing / excess` policy-space meaning;
- keep semantic delta distinct from the concrete change design;
- verify proposed resulting policy semantics before execution;
- keep target selection/relevance outside APR;
- keep provider/device mutation execution outside APR;
- allow technical-to-domain/business attribution as supporting explanation without making it the definition of technical policy equivalence;
- keep large policy-space computation data-local behind APR semantic contracts rather than requiring complete object-graph hydration in the application process;
- consume only published upstream contracts/projections even when data is physically co-located.

The target Tactical DDD, ERD, persistence model and concrete computation engine are still under design.

Requirement-to-Policy Alignment is outside APR: it compares `NEEDED` with effective `AUTHORIZED`, while APR compares required target policy semantics with configured target policy semantics.

## Source acquisition and firewall semantics

NetFlow/syslog capture, vendor polling/parsers, CSV/XLSX import and raw config storage remain adapters/mechanisms. Provider-specific policy evaluation semantics must be normalized through an explicit owning/integration contract before APR may treat configured input as effective access semantics.

## Strategic DDD closure

`DDD-BDM-010` remains the source Strategic DDD baseline. The living `NAPMS-DDD-001` model has since been extended by accepted domain decisions. Historical reconstruction evidence remains provenance rather than current target truth.

Strategic DDD is revisited when new evidence changes language, lifecycle, authority or responsibility boundaries.
