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

## Resource realization

The existing temporal `ResourceRealizationVersion` remains the owner of effective endpoint/address facts:

```text
Resource Realization Version
    factReference
    resourceReference
    EndpointAddress+
    [validFrom, validUntil)
    provenanceReference
```

A realization version contains at least one Endpoint Address.

Changing the effective endpoint/address set is represented by ending the previous effective realization when applicable and creating another version. Historical rows are not rewritten merely to reflect current state.

For one Resource at one logical time, the application layer must not accept overlapping authoritative realization versions that would make the current endpoint set ambiguous unless a later requirement explicitly models multiple simultaneous authoritative realizations.

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
```

The relation controls which Resources belong to a responsibility-oriented workspace. It does not grant actor authority.

For the same Resource + Responsibility Scope + logical time, at most one effective affiliation is accepted.

Curation may create an affiliation or end an effective affiliation. Historical affiliations are not hard-deleted.

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
```

I27 curation may create responsibility assignments and end current assignments. It does not invent a mandatory single primary owner.

Resource Responsibility does not place the Resource into a Responsibility Scope and does not grant NAPMS mutation permission.

## Lifecycle and mutation consequences

### Retiring a Resource

A Resource may be retired only after no new authoring path requires it as an active participant.

Retirement:

- removes the Resource from new binding/authoring selection where an active Resource is required;
- preserves historical endpoint realization, scope affiliation, responsibility and Deployment Resource Binding references;
- does not rewrite existing Requirement, Decision, Rule or realization history;
- does not silently end Authority Management assignments because those belong to another context.

The application layer should require explicit handling of currently effective Resource Scope Affiliations and current Resource Responsibilities before retirement if leaving them active would create misleading current projections.

Exact retirement preconditions are closed together with I27 lifecycle command semantics before persistence mutation is opened.

### Hard deletion

Hard deletion is outside normal I27 product commands. Database/operator repair remains outside the product contract.

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

The migration must not infer Resource responsibility, ownership, company, organization or scope membership from addresses or naming conventions.

## Concurrency

Concurrent mutation must not silently overwrite Resource catalogue facts. The exact version/ETag/idempotency contract is decided in the I27 Stage 0 command semantics and then applied consistently to ACC and Resource Catalogue write APIs.

## Consequences

- Resources gain a safe user-facing write model without becoming generic CMDB assets;
- temporal realization/affiliation/responsibility remain historical facts rather than mutable columns;
- resource identity remains stable when addresses, scope membership or responsible people change;
- policy and authority boundaries remain independent;
- HTTP/Web mutation remains blocked until the shared I27 authority and command-concurrency decisions are closed.
