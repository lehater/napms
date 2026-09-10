# Catalogue Curation Security Requirements

Status: `accepted for I27`.

Date: 2026-09-10.

## Purpose

Define observable authorization behavior for catalogue mutation without conflating catalogue visibility, operational responsibility and mutation permission.

## Authority actions

I27 uses:

```text
CurateApplicationCatalogue @ application-catalogue
CurateResourceCatalogue    @ resource-catalogue
```

Authority Management remains the sole owner of actor/action admission. The administrative scope references above are server-owned command policy; callers do not select them.

## Observable behavior

For every catalogue mutation:

1. authenticated session supplies the Actor;
2. owning application use case selects its fixed catalogue administrative scope;
3. backend evaluates the corresponding `Curate*Catalogue` action for Actor/scope/effective time;
4. command validates owner-domain invariants;
5. persistence occurs only after admission and invariant validation.

The client does not supply trusted `actorId`, catalogue authority scope or server action time.

## Separation of concerns

The following facts do not by themselves grant curation permission:

- Resource Scope Affiliation;
- Resource Responsibility or owner/contact role;
- ability to read a catalogue object;
- ability to read Connectivity/Checker;
- `ProposeConnectivity`;
- `DecideConnectivity`;
- Access Rule read/mutation authority.

Likewise catalogue curation authority does not grant any of those protected policy actions.

A Responsibility Scope appearing inside a Resource Scope Affiliation command is business data for that relation. It is not substituted for the server-owned `resource-catalogue` authorization scope.

## Scope integrity

ACC and RC curation fail closed unless the actor has exactly one effective admitted assignment for the corresponding fixed administrative action/scope according to existing Authority Management ambiguity semantics.

The backend must not derive catalogue permission from display names, Resource addresses, Application hierarchy, Resource Scope Affiliation, Resource Responsibility or currently visible UI selection.

If a later requirement needs delegated per-team/per-company catalogue editing, the product must introduce an explicit catalogue stewardship/governance contract rather than reinterpret current membership/contact relations.

## Read workspace

The UI may hide or disable create/edit actions when the session lacks the corresponding catalogue curation capability. This is presentation only.

Direct HTTP invocation of the same mutation must still be rejected when authority is absent.

Read visibility continues to follow the existing catalogue visibility baseline until a separate accepted requirement changes it.

## Error behavior

Authorization denial is distinguishable from:

- structural/domain validation failure;
- optimistic concurrency conflict;
- idempotency-key conflict;
- persistence/transport uncertainty.

Protected internal authority/provenance details must not be leaked merely to explain a denial.

## Local demo

The supported local demo actor may be seeded with both curation actions on their fixed catalogue administrative scopes to exercise the workflow end to end.
