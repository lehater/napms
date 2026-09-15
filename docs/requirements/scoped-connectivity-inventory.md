# Scoped Connectivity Inventory requirements

Status: `G1 revalidated product contract; AD target semantics aligned 2026-09-15; composition details pending later design`.

Date: 2026-09-15.

## Purpose

Define the resource-centric workspace that lets an authenticated actor understand connectivity for one selected Responsibility Scope without exposing NAPMS bounded-context boundaries.

The workspace is a cross-capability read/action composition. It is not a new source of business truth.

Primary user question:

> What Resources are in my selected area of responsibility, which Application Components are currently placed on them, what application interactions exist, what business need/authorization exists, and how is that authorization realized?

`Needed`, `Authorized` and `Realized` remain independent dimensions.

## Responsibility scope and local Resources

The selected Responsibility Scope is the workspace context.

Two independent truths use the same stable scope reference:

```text
Resource Catalogue:
Resource --Resource Scope Affiliation--> Responsibility Scope

Authority Management:
Actor --effective action authority--> Responsibility Scope
```

Requirements:

- scope discovery exposes only scopes for which the actor has effective `ReadScopedConnectivity` authority;
- reading a selected scope re-evaluates that authority for the requested logical time;
- ambiguous/denied/unknown authority exposes no local inventory data;
- local Resources are those effectively affiliated with the selected scope at that logical time;
- Resource membership does not imply actor authority and actor authority does not manufacture Resource membership;
- Resource identity is not defined by one owner/scope field;
- caller-supplied actor identity is never trusted.

## Catalogue visibility and Application Deployment relation

Current target semantics:

- Resources are catalogue-visible to authenticated users for discovery/context;
- mutation authority is independent from visibility;
- Application Deployment owns one stable `ApplicationDeploymentRef` for one logical deployment of an Application;
- its current placement set contains unique `(ComponentRef, ResourceRef)` relations;
- one Component may have zero, one or many current Resource placements inside the same logical ApplicationDeployment;
- ordinary scaling, Resource migration and placement replacement do not by themselves change ApplicationDeployment identity;
- RC Resource AddressSpace changes do not change ApplicationDeployment or placement meaning;
- a complete empty placement set is different from unavailable/unresolved placement truth.

The resource-centric inventory may therefore project:

```text
Resource
    -> ApplicationDeployment / ComponentPlacement rows [0..N]
        -> Component
        -> known Interaction [0..N]
```

The same ApplicationDeployment/Component may legitimately appear under several Resources when the Component is placed on several Resources. This is not duplicate domain identity.

A local Resource remains visible even when it has no current AddressSpace or no Component placement.

## Local-relative interaction projection

The governed interaction subject is:

```text
InteractionContractRevisionRef
+ sourceApplicationDeploymentRef
+ destinationApplicationDeploymentRef
```

For each local placement, expand ACC-known directed Interactions involving that Component and correlate the relevant source/destination ApplicationDeployments.

Presentation direction is relative to the selected local side:

```text
local Component is source       -> outgoing
local Component is destination  -> incoming
```

If both participants have placements on local Resources, the same governed interaction may appear through several local Resource/placement paths without creating duplicate Interaction, Request or Policy Rule identity.

Remote Resource context is derived from all applicable placements of the remote endpoint Component in the selected remote ApplicationDeployment. Consumers must preserve all applicable placements rather than choose one arbitrary Resource.

If remote placement or RC AddressSpace realization is unresolved, show that explicitly rather than treating the semantic interaction as absent.

## Coarse business and authorization summaries

`ReadScopedConnectivity` admits a coarse owner overview only. Protected detail remains independently authorized.

### Business need summary

For the exact Interaction/current context, the workspace may summarize whether known current Business Process / Connectivity Need justification exists.

```text
Need = Known | None | Unknown
```

The summary must not expose protected Need/Process provenance/details unless separately admitted.

`None` does not mean forbidden. `Unknown` must not be converted to absence.

### Access governance summary

For the exact governed subject, the workspace may summarize current request/governance state without exposing protected decision provenance.

At minimum:

```text
NoRequest
PendingApprovals
Approved
Rejected
Revoked
Unknown
```

The summary is derived from Access Governance truth and is not a new persisted inventory lifecycle.

### Policy summary

The workspace may summarize whether an authoritative current Policy Rule exists and whether it contributes to effective authorized policy at the selected time.

```text
rule = Exists | None | Unknown
effectiveAuthorization = Yes | No | Unknown
```

Rule identity/provenance/audit details require independent Access Policy read authority.

### Realization summary

Where trustworthy realization data is available:

```text
Satisfied
MissingRequiredAccess
ExcessUnauthorizedAccess
Unresolved
Unknown
```

These are realization summaries, not authorization states.

## Request access action

A user may initiate access for an in-scope source context when Authority Management admits the request action.

The action reuses trusted semantic context:

- selected source Resource and the source ApplicationDeployment/Component placement shown under it;
- selected destination ApplicationDeployment/Component context;
- existing immutable ACC `InteractionContractRevisionRef`;
- Process-backed Connectivity Need required for deliberate access.

The Access Request subject remains the logical source/destination ApplicationDeployment pair plus exact InteractionContractRevisionRef. Individual placement ResourceRefs are current applicability/obligation inputs, not request-subject identity.

The flow submits into bilateral Access Governance; it does not materialize a Policy Rule directly.

Request initiation, source-side approval, destination-side approval, withdrawal and network execution are independently authorizable actions.

If no valid Process-backed Need exists, the product must establish that business justification through Business Connectivity rather than fabricate one inside the inventory.

## Zero-interaction Components

A placed Component with no ACC-known Interaction has no trusted remote participant/traffic contract that the inventory can authorize.

Current behavior:

- show the local Resource/deployment/component placement;
- state that no catalogued interaction is known;
- do not construct arbitrary access from client-entered UUIDs/IP/ports.

Authoring a new application Interaction belongs to ACC.

## Query semantics and bounded results

Conceptual query input:

- authenticated actor from server/session;
- selected Responsibility Scope;
- explicit logical `asOf` where time-qualified truth is requested;
- bounded Resource paging;
- search/filter/sort as supported.

Use one coherent logical time where owner contracts support time-qualified truth. Partial enrichment remains explicit; unavailable information is `Unknown`, not false absence.

Top-level paging is over local Resources so Resource groups are not split across pages. Bounded child collections require explicit continuation/truncation semantics.

## Non-goals

- a new Connectivity Overview Bounded Context;
- copied cross-context truth as authoritative inventory state;
- authorization inferred from Resource owner/administrator metadata;
- a single global `Allowed | NotAllowed` Decision model;
- exactly-one Resource placement per Component;
- arbitrary remote/interaction construction from client-entered technical identifiers;
- vendor/device rendering or execution.

## Canonical target references

- Business Connectivity: `docs/requirements/business-connectivity-g1.md`;
- Access Governance: `docs/requirements/access-governance-g1.md`;
- Application/Interaction and AD/RC split: `docs/requirements/application-catalogue-domain-target.md`;
- AD Tactical semantics: `docs/domain/application-deployment/tactical-model.md`;
- Resource Catalogue: `docs/domain/resource-catalogue/tactical-model.md`;
- Authority Management: `docs/domain/authority-management/tactical-model.md`;
- Access Policy / realization owners: current canonical domain and requirement artifacts.
