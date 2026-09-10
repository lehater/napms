# Resource Catalogue Tactical Model for Curation

Status: `accepted for I27 catalogue curation Stage 0`.

Date: 2026-09-10.

## Purpose

Define the Resource Catalogue write semantics required for normal user-facing curation of access-relevant Resources without turning NAPMS into a generic asset inventory or merging catalogue data with Authority Management.

This document complements `docs/domain/resource-role-model.md`, which remains the strategic owner of Resource identity, Resource Scope Affiliation, Resource Responsibility and their relationship to authority.

## Product boundary

The curation slice manages only facts needed by governed network-access outcomes:

```text
Resource
  -> Resource Realization Version
      -> Endpoint Address
  -> Resource Scope Affiliation
  -> Resource Responsibility
```

Resource identity is independent from provider/device realization, Logical Firewall identity, Application/Component Deployment and organizational ownership.

## Resource identity

```text
Resource
    resourceReference: stable non-empty string
    displayName: optional non-empty string
    lifecycle: Active | Retired
    provenanceReference: non-empty string
```

`resourceReference` is server-owned for UI-created Resources in I27. Existing pre-I27 resource references remain unchanged.

Display-name changes do not change Resource identity.

The Resource lifecycle is:

```text
Active -> Retired
```

Retirement is terminal for the first curation slice and preserves historical realization, affiliation, responsibility, binding and policy references.

Normal product workflows do not hard-delete Resource identity.

## Temporal fact provenance

Resource realization, scope affiliation and responsibility are historical facts. Their creation provenance and a later explicit end action are different business events and must remain distinguishable.

For those fact types I27 therefore preserves:

```text
provenanceReference
    source/provenance of the fact as created

endProvenanceReference: optional
    provenance of a later explicit End/Replace action that established validUntil
```

When a fact is created with a finite validity interval already known, `validUntil` may be present while `endProvenanceReference` is absent: the end instant is part of the original declaration.

When an open-ended fact is ended later by a curation command, the command must set both `validUntil` and `endProvenanceReference` in one semantic mutation. The original `provenanceReference` is not overwritten.

This distinction preserves business auditability without turning operational logs or command receipts into the source of domain provenance.

## Resource realization

The existing temporal `ResourceRealizationVersion` remains the owner of effective endpoint/address facts:

```text
Resource Realization Version
    factReference
    resourceReference
    EndpointAddress+
    [validFrom, validUntil)
    provenanceReference
    optional endProvenanceReference
```

A realization version contains at least one Endpoint Address.

Changing the effective endpoint/address set is represented by ending the previous effective realization when applicable and creating another version. Historical rows are not rewritten merely to reflect current state.

For one Resource at one logical time, the application layer must not accept overlapping authoritative realization versions that would make the current endpoint set ambiguous unless a later requirement explicitly models multiple simultaneous authoritative realizations.

An explicit replacement that ends an existing open realization and creates its successor is one Resource Catalogue use case and must preserve the previous fact identity/provenance while recording the end provenance of the previous fact.

## Endpoint Address

```text
Endpoint Address
    endpointReference
    technicalAddress
```

The endpoint reference is stable within its realization fact. The technical address is normalized and validated according to the accepted technical-address contract before persistence.

I27 initially supports the address forms already consumed by the current Resource Catalogue/Checker implementation. Expanding the address algebra is a separate domain change.

## Resource Scope Affiliation

Existing semantics remain unchanged:

```text
Resource Scope Affiliation
    affiliationReference
    resourceReference
    responsibilityScope
    [validFrom, validUntil)
    provenanceReference
    optional endProvenanceReference
```

The relation controls which Resources belong to a responsibility-oriented workspace. It does not grant actor authority.

For the same Resource + Responsibility Scope + logical time, at most one effective affiliation is accepted.

Curation may create an affiliation or end an effective affiliation. Historical affiliations are not hard-deleted.

An explicit end preserves the affiliation's creation provenance and records separate end provenance.

## Resource Responsibility

Existing I26 ownership/contact semantics remain independent from Authority Management:

```text
Resource Responsibility
    resourceReference
    responsiblePartyReference
    partyKind: Person | Team
    role: ServiceOwner | TechnicalOwner | OperationsContact | BusinessOwner
    displayName
    optional contactPoint
    [validFrom, validUntil)
    provenanceReference
    optional endProvenanceReference
```

I27 curation may create responsibility assignments and end current assignments. It does not invent a mandatory single primary owner.

Resource Responsibility does not place the Resource into a Responsibility Scope and does not grant NAPMS mutation permission.

An explicit end preserves the assignment's creation provenance and records separate end provenance.

## Lifecycle and mutation consequences

### Retiring a Resource

A Resource may be retired only after no new authoring path requires it as an active participant.

Retirement:

- removes the Resource from new binding/authoring selection where an active Resource is required;
- preserves historical endpoint realization, scope affiliation, responsibility and Deployment Resource Binding references;
- does not rewrite existing Requirement, Decision, Rule or realization history;
- does not silently end Authority Management assignments because those belong to another context.

Before Resource retirement, currently effective Resource Scope Affiliations and current Resource Responsibilities must be explicitly ended. I27 does not silently cascade those cross-record changes.

A currently effective realization does not block retirement in I27. It remains historical/technical realization truth and downstream current projections that require an Active Resource must apply the Resource lifecycle contract explicitly.

### Hard deletion

Hard deletion is outside normal I27 product commands. Database/operator repair remains outside the product contract.

## Temporal mutation/version consequences

Resource identity and temporal relation rows use optimistic versioning for user-facing mutation.

For an explicit end operation:

```text
open fact version N
    -> validate expectedVersion == N
    -> set validUntil
    -> set endProvenanceReference
    -> version N + 1
```

An already ended fact is not ended again under another command identity. Equivalent retry is handled by the application idempotency contract; a different later command attempting another end fails its state/concurrency precondition.

## Command responsibility

Expected Resource Catalogue command families after Stage 0 closure:

```text
CreateResource
RenameResource
RetireResource

CreateResourceRealization
ReplaceResourceRealization

CreateResourceScopeAffiliation
EndResourceScopeAffiliation

CreateResourceResponsibility
EndResourceResponsibility
```

Exact command names may change during implementation; the semantic responsibilities above must remain explicit.

## Query responsibility

The curation workspace needs read models for:

```text
Resources
  -> current endpoints/addresses
  -> current scope affiliations
  -> current responsibilities/contacts
  -> bound Component Deployments where useful for impact/explainability
```

Cross-context bound-deployment information may be composed as a read projection. Resource Catalogue does not own Component Deployment identity or binding semantics.

## Authority boundary

Catalogue mutation authority is evaluated separately by Authority Management.

The following remain independent:

```text
catalogue visibility
Resource Scope Affiliation
Resource Responsibility
catalogue mutation authority
Requirement/Decision/Rule authority
```

An actor may be a Service Owner or Technical Owner without being allowed to mutate the Resource Catalogue. Conversely, a catalogue curator may change catalogue facts without receiving policy-decision authority.

## Compatibility with existing data

I27 must preserve every existing `resource_reference`, realization fact reference, endpoint reference and Resource Scope Affiliation reference unless a specific repair migration has independent evidence to change it.

Schema extensions for display metadata/lifecycle/version control must use conservative defaults for existing rows and explicit migration provenance where a new fact is manufactured by migration.

`endProvenanceReference` is nullable for migrated/pre-I27 rows. A historical finite `validUntil` without end provenance means the repository has no accepted evidence that the end was established by a later explicit I27 end command; migration must not manufacture an actor or authority source.

The migration must not infer Resource responsibility, ownership, company, organization or scope membership from addresses or naming conventions.

## Concurrency

Concurrent mutation must not silently overwrite Resource catalogue facts. The I27 command/ETag/idempotency contract applies consistently to Resource identity and mutable temporal relation state.

## Consequences

- Resources gain a safe user-facing write model without becoming generic CMDB assets;
- temporal realization/affiliation/responsibility remain historical facts rather than mutable current-state columns;
- creation provenance is not destroyed when a temporal fact is explicitly ended later;
- resource identity remains stable when addresses, scope membership or responsible people change;
- policy and authority boundaries remain independent;
- HTTP/Web mutation remains downstream of owner-domain/application contracts.
