# Semantic Ownership

Status: `S2 strategic revalidation in progress`.

This file defines semantic ownership, not runtime/service ownership.

## Ownership map

| Knowledge / decision | Semantic owner | Upstream authority / source | Primary result |
|---|---|---|---|
| Business Process meaning/responsibility used for connectivity justification | **Business Connectivity** | stakeholder/business catalogue inputs | Business Process |
| application-semantic connectivity Need, applicability and justification | **Business Connectivity** | Business Process + ACC Interaction meaning | Connectivity Need |
| business attribution / missing-justification finding | **Business Connectivity** or non-peer composition using its truth | Process/Need truth + recognized/authorized interaction reference | Attribution / reconciliation finding |
| concrete Access Request and source/destination approval obligations | **Access Governance** | Process-backed Need + trusted deployed-interaction subject | Access Request + Approval Obligations |
| side approve/reject decision and historical authority provenance | **Access Governance** | Authority Management effective authority + Request subject | Side Decision |
| bilateral current authorization grant / withdrawal | **Access Governance** | side-consent history and revocation action | Authorization Granted / Withdrawn |
| current authoritative Policy Rule truth and effective semantic authorization projection | **Access Policy** | Access Governance grant/withdrawal + trusted ACC subject | Policy Rule + effective authorized policy |
| scoped actor/action authority and assignment semantics | **Authority Management** | group/role/scope membership/assignment decisions | Effective Authority / assignment facts |
| Resource membership in one responsibility scope/time | **Resource Catalogue** | authoritative organizational/resource affiliation facts | Resource Scope Affiliation |
| Resource/Endpoint/current address realization | **Resource Catalogue** | trusted inventory/network facts | Resource/Endpoint/current realization |
| application/component communication contract and concrete ComponentDeployment identity | **Application Communication Catalogue** | authorized catalogue sources | Application/Component/ComponentDeployment/Interaction Contract |
| scoped resource-centric connectivity inventory | **non-peer application composition** | AM + RC + ACC + Business Connectivity + Access Governance + Access Policy + realization sources | Scoped Connectivity Inventory |
| enforcement-target relevance and applicable policy/ACL locators | **Network Enforcement Placement** | current routing/interface state + candidate overrides + locator bindings | Firewall candidate/target refs + policy locators |
| normalized source-qualified technical access evidence | **Technical Access Evidence** | device/traffic/import adapters and external sources | Technical Access Evidence Set / Entry |
| effective-policy realization assessment, semantic delta, vendor-neutral change design and proposed-result semantic verification | **Access Policy Realization** | target-specific required policy + comparable configured effective policy | Assessment / Delta / Change Design / Verification |
| provider-specific target rendering | `DIRTY` / owner under revalidation | verified vendor-neutral intent + provider semantics | target representation |
| provider/device operation identity, concurrency, mutation outcome and execution provenance | **Network Environment Operations** | target representation + Authority Management mutation admission + target/provider observations | Network Operation Result |

## Business Connectivity authority

Business Connectivity owns the claim:

> Business Process P currently requires application-semantic Interaction I from dependent participant/role D under the stated applicability/justification.

It does not own:

- concrete ComponentDeployment authorization;
- source/destination consent;
- Policy Rule state;
- technical realization.

A Need may survive deployment replacement or access revocation while the business requirement remains. Need existence therefore cannot be used as proof of authorization.

## Access Governance authority

Access Governance owns the governance claim for one concrete deployed authorization subject:

```text
source ComponentDeployment
+ destination ComponentDeployment
+ stable Interaction meaning
```

It owns:

- Request history;
- source/destination approval obligations;
- side approve/reject decisions;
- bilateral grant evaluation;
- current consent withdrawal/revocation;
- sufficient provenance to explain who decided for which side, when, and on what authority basis.

Strategic rules:

```text
Grant  = source consent AND destination consent
Revoke = source withdrawal OR destination withdrawal
```

A rejected Request is governance history, not a deny Policy Rule. Revocation does not delete the underlying Connectivity Need or rewrite the original approved Request as rejected.

## Authority Management ownership

Authority Management owns whether Actor A may perform action X for Scope S at logical time T and the private assignment/group/role mechanics that establish that result.

Consumers receive an effective authority result such as:

```text
admitted | denied | unknown/ambiguous
```

plus sufficient provenance where audit requires it.

Access Governance and other consumers must not infer permission from Resource owner/administrator metadata or peer into role/group internals.

## Access Policy ownership

Access Policy owns current authoritative Policy Rule truth and effective authorized-policy projection.

It consumes Access Governance authorization grant/withdrawal semantics for an exact trusted subject and does not re-run bilateral consent logic.

Several Needs and several approved Requests may support one current semantic Policy Rule. Rejected Requests do not create semantic deny Rules.

## Responsibility Scope / Resource affiliation ownership

Two independent truths share a stable scope reference:

```text
Resource Catalogue:
Resource --Resource Scope Affiliation--> Responsibility Scope

Authority Management:
Actor --effective authority(action,time)--> Responsibility Scope
```

Resource Catalogue owns whether Resource R belongs to Scope S at time T.
Authority Management owns whether Actor A may perform action X for Scope S at time T.
Neither truth implies the other.

Current global catalogue visibility remains a third independent concern.

## Scoped Connectivity Inventory ownership

Scoped Connectivity Inventory is a non-peer application/read composition. It correlates trusted facts from the authoritative contexts and owns no new business identity/lifecycle/status.

It may summarize independently:

- local Resource/ComponentDeployment/Interaction context;
- business Need/justification state;
- Access Governance request/approval/revocation state;
- Access Policy current effective authorization;
- technical realization/reconciliation.

No summary dimension may be inferred from another (for example Need != Authorized, Authorized != Realized).

## Primary governance-chain contracts

### Business Connectivity -> Access Governance

Provides Process-backed Connectivity Need / business-justification meaning for a deliberate request. Access Governance must preserve the justification basis used historically and must not treat Need as consent.

### Application Communication Catalogue -> Access Governance / Access Policy

Provides exact deployed-interaction identity:

```text
sourceComponentDeploymentRef
+ destinationComponentDeploymentRef
+ interactionContractRevisionRef
```

ComponentDeployment is bound to exactly one Resource for MVP. Endpoint/address realization remains Resource Catalogue truth.

### Authority Management -> Access Governance

Provides effective request/approve/revoke action authority for the relevant actor/scope/time plus needed audit provenance.

### Access Governance -> Access Policy

Provides semantic authorization transitions such as:

```text
AuthorizationGranted(subject, provenance)
AuthorizationWithdrawn(subject, provenance)
```

It does not publish peer-private Request state as Access Policy domain state.

## Technical Access Evidence authority

Technical Access Evidence owns the claim that source X provided or allowed NAPMS to derive technical access material Y for scope/time T. It does not own whether Y is desired, authorized or correctly realized.

## Network Enforcement Placement authority

NEP owns candidate enforcement-location relevance and applicable policy/ACL locator information for supplied technical traffic pairs. It does not own authorization, configured policy contents, desired-vs-configured reconciliation, rendering or provider execution.

APR must not reevaluate why NEP selected a target.

## Access Policy Realization authority

APR owns normalized required-vs-configured effective-policy comparison for a supplied comparable target, including:

- realization assessment;
- exact `common / missing / excess` semantic delta;
- vendor-neutral policy-change design;
- semantic verification of the proposed resulting effective policy.

Provider-specific rendering is currently a `DIRTY` strategic ownership question and is not treated as settled APR truth by this document.

APR does not own target relevance, Policy Rule authorization, catalogue identity, evidence source truth or provider/device mutation execution.

## Network Environment Operations authority

Network Environment Operations owns provider/device operation lifecycle, idempotency/concurrency, mutation outcome and execution provenance downstream of an accepted target representation.

Apply response remains distinct from final convergence verification. Unknown apply is never silently converted to success.

## Legacy ownership disposition

The old target claims are superseded:

```text
Connectivity Requirements -> Business Connectivity
Connectivity Decision     -> Access Governance
```

Legacy `ConnectivityRequirement`, `ConnectivityDecision`, Access Rule Proposal and related runtime models remain migration/current-state evidence until later Tactical/Architecture/Implementation work replaces or retires them. They are not target ownership merely because they exist in code.

## Independent truth dimensions

```text
Observed interaction/evidence
Recognized application interaction
Business Need exists
Access Request exists
Source-side decision exists
Destination-side decision exists
Authorization currently granted / withdrawn
Policy Rule exists / contributes to effective authorization
Required technical policy materializable / unresolved
Target relevance established
Configured effective policy available
Realization common / missing / excess computed
Policy change designed
Proposed result verified
Target representation rendered
Network operation attempted
Convergence post-check observed
```

No fact at one dimension silently becomes another context's authoritative truth.
