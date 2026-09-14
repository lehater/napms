# Scoped Connectivity Inventory requirements

Status: `G1 revalidated product contract; composition details pending later design`.

Date: 2026-09-14.

## Purpose

Define the resource-centric workspace that lets an authenticated actor understand connectivity for one selected responsibility scope without exposing NAPMS bounded-context boundaries.

The workspace is a cross-capability read/action composition. It is not a new source of business truth.

Primary user question:

> What Resources are in my selected area of responsibility, what Components are deployed on them, what application interactions exist, what business need/authorization exists, and how is that authorization realized?

## Product model

```text
authenticated actor
    -> selected Responsibility Scope
    -> local Resources
    -> Component Deployments on those Resources
    -> known Interactions
         -> Business Need / justification
         -> Access Request / bilateral governance
         -> current Policy Rule authorization
         -> realization/reconciliation
```

`Needed`, `Authorized` and `Realized` remain independent dimensions. The workspace must not collapse them into one generic connectivity status.

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

- scope discovery exposes only scopes for which the actor has unambiguous effective `ReadScopedConnectivity` authority;
- reading a selected scope re-evaluates that authority for the requested logical time;
- ambiguous/denied/unknown authority exposes no local inventory data;
- local Resources are those effectively affiliated with the selected scope at that logical time;
- Resource membership does not imply actor authority and actor authority does not manufacture Resource membership;
- Resource identity is not defined by one owner/scope field;
- caller-supplied actor identity is never trusted.

## Catalogue visibility and Resource/Deployment relation

Current MVP semantics:

- Resources are catalogue-visible to authenticated users for discovery/context;
- mutation authority is independent from visibility;
- each ComponentDeployment belongs to exactly one Resource for its lifetime;
- Resource association is mandatory at ComponentDeployment creation;
- Resource Endpoint/address changes do not change ComponentDeployment identity;
- moving the Component to another Resource yields a different ComponentDeployment rather than rebinding the existing authorization subject.

The inventory hierarchy is therefore:

```text
Resource
    -> ComponentDeployment[0..N]
        -> known Interaction[0..N]
```

A local Resource remains visible even when it has no current Endpoint/address realization or no ComponentDeployment.

## Local-relative interaction projection

The exact deployed interaction subject is:

```text
source ComponentDeployment
+ destination ComponentDeployment
+ immutable Interaction Contract Revision
```

For each local ComponentDeployment, expand ACC-known directed interactions involving it.

Presentation direction is relative to the selected local side:

```text
local == source       -> outgoing
local == destination  -> incoming
```

If both participants are local, the same interaction may appear under both local Resource/Deployment paths without creating duplicate domain interaction or Policy Rule identity.

Remote Resource context is obtained from the remote ComponentDeployment's single Resource reference. If Resource Endpoint/address realization is unresolved, show that explicitly rather than treating the semantic interaction as absent.

## Coarse business and authorization summaries

`ReadScopedConnectivity` admits a coarse owner overview only. Protected detail remains independently authorized.

### Business need summary

For the exact interaction and selected scope/context, the workspace may summarize whether known current Business Process / Connectivity Need justification exists.

Conceptual result:

```text
Need = Known | None | Unknown
```

The summary must not expose protected Need/Process provenance or details unless separately admitted.

`None` does not mean forbidden. `Unknown` must not be converted to absence.

### Access governance summary

For the exact deployed interaction subject, the workspace may summarize current request/governance state without exposing protected decision provenance.

At minimum the composition must distinguish:

```text
NoRequest
PendingApprovals
Approved
Rejected
Revoked
Unknown
```

The summary is derived from Access Governance truth. It is not a new persisted inventory lifecycle.

`Approved` means the required bilateral approval obligations were satisfied for the current authorization action. `Revoked` means previously granted authorization is no longer current because a side withdrew consent or equivalent accepted revocation occurred. Exact aggregate/state representation remains owned outside this read composition.

### Policy summary

The workspace may summarize whether an authoritative current Policy Rule exists and whether it contributes to effective authorized policy at the selected time.

Conceptual fields:

```text
rule = Exists | None | Unknown
effectiveAuthorization = Yes | No | Unknown
```

Rule identity, provenance, audit and governance detail require independent Access Policy read authority.

### Realization summary

Where realization/reconciliation data is available, the workspace may distinguish:

```text
Satisfied
MissingRequiredAccess
ExcessUnauthorizedAccess
Unresolved
Unknown
```

These are derived realization summaries, not authorization states.

## Request access action

A user may initiate access for an in-scope source Resource when Authority Management admits the request action.

The action reuses trusted context:

- selected source Resource / source ComponentDeployment;
- selected destination Resource / destination ComponentDeployment;
- existing ACC Interaction Contract Revision;
- Process-backed Connectivity Need required for deliberate access.

The flow creates/submits an Access Request governed by the bilateral source/destination approval contract. It does not bypass Access Governance by materializing a Policy Rule directly.

Request initiation, source-side approval, destination-side approval, revocation and network execution are independently authorizable actions.

If no valid Process-backed Need exists for deliberate access, the product must obtain/establish that business justification through the owning capability rather than fabricate one inside the inventory.

## Zero-interaction Components

A ComponentDeployment with no ACC-known interaction has no trusted remote participant/traffic contract that the inventory can authorize.

Current behavior:

- show the local Resource/Deployment;
- state that no catalogued interaction is known;
- do not construct an arbitrary access subject from client-entered UUIDs/IP/ports.

Authoring a new application interaction belongs to the Application Communication Catalogue capability.

## Query semantics and bounded results

Conceptual query input:

- authenticated actor from server/session;
- selected Responsibility Scope;
- explicit logical `asOf` where time-qualified truth is requested;
- bounded Resource paging;
- search/filter/sort as supported.

Use one coherent logical time for authority, Resource affiliation/realization and any time-qualified business/authorization summaries. Partial enrichment must remain explicit; unavailable information is `Unknown`, not false absence.

Top-level paging is over local Resources so Resource groups are not split across pages. Bounded child collections require explicit continuation/truncation semantics.

## Non-goals

- a new Connectivity Overview Bounded Context;
- copied cross-context business truth as authoritative inventory state;
- authorization inferred from Resource owner/administrator metadata;
- a single `Allowed | NotAllowed` global Decision model;
- multiple Resource bindings for one ComponentDeployment in the current MVP;
- arbitrary remote/interaction construction from client-entered technical identifiers;
- vendor/device rendering or execution.

## Canonical references

- Business Connectivity: `docs/requirements/business-connectivity-g1.md`;
- Access Governance: `docs/requirements/access-governance-g1.md`;
- Access Policy: `docs/requirements/access-policy-core.md`;
- ACC target: `docs/requirements/application-catalogue-domain-target.md`;
- realization/reconciliation: `docs/requirements/policy-realization-reconciliation-g1.md`;
- revalidation checkpoint: `docs/engineering/context-problems/capability-revalidation-checkpoint-2026-09-14.md`.

Older Requirement/Decision inventory semantics remain historical implementation evidence where they conflict with these revalidated target requirements.
