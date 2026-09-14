# NAPMS Strategic DDD model

Status: `S2 strategic revalidation in progress`.

Source baseline: DDD-BDM-010, revalidated by 2026-09-14 G1 requirements and ADR-019.

This document defines model/language/responsibility boundaries. It does not define services, databases, teams or deployment units.

## Current target Bounded Contexts

| Bounded Context | Semantic center | Responsibility |
|---|---|---|
| **Business Connectivity** | why is application connectivity needed by the business? | Business Process meaning/responsibility, application-semantic Connectivity Need, business attribution and justification reconciliation |
| **Access Governance** | has a concrete deployed interaction received and retained the required consent? | Access Request history, source/destination approval obligations, side decisions, bilateral grant, withdrawal/revocation and governance provenance |
| **Access Policy** | what network access is currently authorized to exist? | authoritative Policy Rule truth, semantic uniqueness/idempotency and effective authorized-policy projection |
| **Authority Management** | who may perform a domain action for scope/time? | effective actor/action/scope authority, role/group/scope assignments and accountability semantics |
| **Resource Catalogue** | what access-domain resources exist, to which responsibility scopes do they belong, and how are they currently realized? | Resource/Endpoint identity, Resource Scope Affiliation, current/historical realization and access-relevant lifecycle facts |
| **Application Communication Catalogue** | which application/component interactions and concrete Component Deployments are structurally valid? | Application/Component/ComponentDeployment/Interaction identities and immutable interaction traffic contracts |
| **Network Enforcement Placement** | which enforcement locations and policy locators are candidates for a technical source/destination pair? | Firewall candidate relevance from current network state/overrides and applicable policy/ACL locators |
| **Technical Access Evidence** | what technical access material did a source report? | immutable/source-qualified normalized technical evidence with scope/time/provenance; no authorization claim |
| **Access Policy Realization** | how does configured effective access compare with required effective access for a supplied comparable target, and what semantic policy change is needed? | realization assessment, semantic reconciliation, change design and proposed-change semantic verification; provider rendering ownership remains under revalidation |

`Connectivity Requirements` and `Connectivity Decision` are **legacy/current-state context boundaries**, not current target Bounded Contexts. ADR-019 supersedes the stronger MVP-scope assumptions of ADR-016 while preserving the decision not to carry those old boundaries forward unchanged.

## Core semantic ladder

The target model keeps these meanings independent:

```text
Observed != Recognized != Needed != Authorized != Realized
```

- **Needed** is owned by Business Connectivity.
- **Authorized** governance/consent history is owned by Access Governance.
- current authoritative Policy Rule truth is owned by Access Policy.
- **Realized** comparison is downstream of semantic-to-technical materialization and normalized network evidence.

A fact at one level must not be silently promoted to another.

## Business Connectivity boundary

Business Connectivity owns enduring business justification for application-semantic communication.

Its central facts are conceptually:

```text
Business Process
    -> Connectivity Need
        -> required Application Interaction
        -> dependent participant/component role
```

A Need:

- is not permission;
- is not identified by IP address, ResourceEndpoint or concrete ComponentDeployment;
- may survive address changes and concrete deployment replacement while the business requirement remains;
- may lead to several concrete Access Requests over time;
- may coexist with authorized access or with no authorization;
- may disappear without rewriting historical Requests/approvals.

Business Connectivity does not own bilateral consent or Policy Rule state.

## Access Governance boundary

Access Governance owns the lifecycle and history of consent for a concrete deployed interaction.

The authorization subject is based on:

```text
source ComponentDeployment
+ destination ComponentDeployment
+ stable Interaction meaning
```

Ordinary grant semantics are:

```text
source-side consent
AND destination-side consent
    -> Authorization Granted
```

Current consent may be withdrawn by either authorized side:

```text
source withdrawal
OR destination withdrawal
    -> Authorization Withdrawn
```

Access Governance preserves Request/side-decision/grant/withdrawal history and publishes authorization grant/withdrawal semantics to Access Policy. It does not own business Need identity and does not derive actor authority from Resource ownership metadata.

## Authority Management boundary

Authority Management owns effective authorization to perform an action for a scope/time. It is independent from both Resource membership and business/security decisions made by consumers.

Conceptually:

```text
actor + action + scope + time
    -> admitted | denied | unknown/ambiguous
```

Role/group/scope assignment mechanics stay inside Authority Management. Consumers depend on the effective authority result and sufficient provenance for audit, not on peer-private role structures.

## Access Policy boundary

Access Policy owns current semantic authorization truth expressed as authoritative Policy Rules and effective authorized-policy projection.

It consumes `Authorization Granted` / `Authorization Withdrawn` semantics from Access Governance for the exact semantic subject. It does not run approval workflow or persist rejection as a deny Policy Rule.

Multiple Connectivity Needs and multiple approved Requests may justify one current Policy Rule. Address/Endpoint changes on the same Resource do not redefine Rule semantic identity.

## Primary contracts for the governance chain

### Business Connectivity -> Access Governance

Purpose: provide structured business justification for a deliberate concrete Access Request.

Minimal semantic content:

```text
ConnectivityNeedRef
BusinessProcessRef / explainable business basis
required Interaction meaning
current/applicable justification status
```

Access Governance must not treat Need existence as authorization and must preserve the justification basis used when a Request was made.

### Application Communication Catalogue -> Access Governance / Access Policy

Purpose: publish trusted concrete deployed-interaction identity and immutable interaction meaning.

Current subject:

```text
sourceComponentDeploymentRef
+ destinationComponentDeploymentRef
+ interactionContractRevisionRef
```

For MVP each ComponentDeployment belongs to exactly one Resource. ResourceEndpoint/address realization remains Resource Catalogue truth.

### Authority Management -> Access Governance

Purpose: answer whether an actor may request/approve/revoke for the relevant scope/time and provide sufficient authority provenance for the governance journal.

Access Governance must not reproduce role/group resolution logic.

### Access Governance -> Access Policy

Purpose: publish current authorization changes without exposing peer-private workflow state.

Conceptually:

```text
AuthorizationGranted(subject, provenance)
AuthorizationWithdrawn(subject, provenance)
```

Pending/rejected Requests are governance history, not desired deny policy.

## Responsibility Scope relationship

A stable Responsibility Scope reference correlates independent facts:

```text
Resource Catalogue
    Resource --Resource Scope Affiliation--> Responsibility Scope

Authority Management
    Actor --effective action authority--> Responsibility Scope
```

- Resource Catalogue owns Resource membership.
- Authority Management owns actor/action authority.
- Resource affiliation does not grant authority.
- actor authority does not manufacture Resource membership.
- current catalogue visibility is independently governed.

## Realization chain

The accepted high-level chain is:

```text
Business Connectivity
    -> Access Governance
        -> Access Policy
            -> semantic-to-technical materialization
                -> Resource Catalogue + ACC realization
                -> Network Enforcement Placement
                -> normalized required target policy
                    -> Access Policy Realization
                        <-> configured effective-policy evidence
                            -> change execution / post-check downstream
```

Ownership of the semantic-to-technical materialization/projection seam and provider-specific rendering remains to be resolved by later S2/S3 work. The strategic model must not assign those responsibilities merely to preserve current implementation structure.

NEP owns candidate enforcement location/policy-locator selection. APR must not reinterpret why a target was selected.

Technical Access Evidence supplies source-qualified technical evidence and never becomes authorization simply because evidence exists.

## Non-peer compositions

`Scoped Connectivity Inventory` is an application/read composition over authoritative contexts. It may summarize Need, governance, Policy and realization independently but owns none of those truths.

Requirement-to-Policy Alignment is legacy/current-state composition terminology and must be revalidated against Business Connectivity / Access Policy semantics before reuse as target behavior.

## Strategic invariants

- A Bounded Context is not a service/deployment unit.
- Business Need and security authorization are separate authoritative truths and lifecycles.
- Business Connectivity and Access Governance are separate target Bounded Contexts per ADR-019.
- Authority Management owns effective actor/action/scope authority; domain contexts own the decisions made using that authority.
- Access Governance owns bilateral consent history; Access Policy owns current Policy Rule truth.
- Resource Scope Affiliation does not imply actor authority, and actor authority does not imply Resource membership.
- technical evidence is not authorization.
- NEP owns enforcement-location relevance; APR does not second-guess placement.
- APR compares normalized effective policy semantics rather than raw textual configuration identity.
- technical realization changes do not redefine semantic authorization identity.
- legacy Connectivity Requirements / Connectivity Decision artifacts are migration/history evidence and do not override revalidated target semantics.
- Strategic DDD is revisited when new evidence changes language, lifecycle, authority, responsibility or cross-context contracts.

## Remaining strategic questions

The following are intentionally unresolved and do not invalidate the Business Connectivity / Access Governance boundary decision:

- final owner/name for semantic-to-technical required-policy materialization;
- provider-specific effective-policy normalization/rendering boundaries around TAE/APR/operations;
- whether responsibility-scope changes require warning, reapproval or automatic revocation;
- exact Process organizational-responsibility contract with external enterprise structure;
- tactical identities/state machines inside Business Connectivity, Access Governance and revalidated Access Policy.
