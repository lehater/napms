# ADR-007 — I27 Resource Catalogue Lifecycle

Status: `accepted`.

Date: 2026-09-10.

## Context

NAPMS already persists Resource identity, temporal endpoint realizations and Resource Scope Affiliations. I26 also established Resource Responsibility as a separate operational/contact relation.

I27 adds normal user-facing Resource curation. A generic mutable-row CRUD model would conflate identity with changing addresses, organizational scope and responsible contacts, and hard deletion would destroy historical references used by connectivity and realization explainability.

## Decision

Resource identity is stable and uses a minimal lifecycle:

```text
Active -> Retired
```

Endpoint/address changes remain temporal `ResourceRealizationVersion` facts. Responsibility-scope membership remains temporal `ResourceScopeAffiliation`. Operational ownership/contact remains temporal `ResourceResponsibility`.

Changing any of those relations does not create another Resource.

Normal product workflows do not hard-delete Resource identity or historical temporal facts. User-facing removal means ending a temporal relation or retiring a Resource as appropriate.

A retired Resource remains historically resolvable and may remain referenced by existing ACC bindings, Requirements, Decisions, Rules and realization evidence.

Retirement records a separate server-owned `retirementProvenanceReference`. Creation provenance remains unchanged. Newly persisted `Retired` state without a retirement provenance reference is invalid.

Likewise an explicit end/replace of a temporal realization, affiliation or responsibility preserves creation provenance and records a separate end-transition provenance reference rather than overwriting the original fact source.

## Retirement constraints

Before Resource retirement, the application layer must prevent a misleading current state. Currently effective scope affiliations and responsibility/contact assignments must be explicitly ended or otherwise handled by a later accepted retirement orchestration contract; I27 does not silently cascade these cross-record changes.

Retirement does not modify Authority Management assignments because authority is a separate bounded-context concern.

## Identity generation

Existing pre-I27 `resource_reference` values are preserved exactly.

For UI-created Resources, the server generates the stable reference from a repository-owned identity mechanism; clients do not provide authoritative stable identity.

The exact external string form is an implementation contract, not business meaning, and must not encode mutable display name, IP address, company, scope or owner.

## Consequences

- Resource endpoint, scope and responsibility changes stay temporal and explainable;
- lifecycle and temporal endings retain both creation and transition provenance;
- no catalogue mutation silently changes business/policy identity;
- user-facing delete semantics become explicit end/retire operations;
- HTTP and Web can present current state without losing historical truth;
- catalogue mutation authority remains independent and must be accepted separately before implementation opens.

## Owned detail

Detailed Resource curation invariants are maintained in `docs/domain/resource-catalogue/tactical-model.md` and strategic organizational distinctions remain owned by `docs/domain/resource-role-model.md`.
