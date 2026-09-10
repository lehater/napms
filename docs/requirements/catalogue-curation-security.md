# Catalogue Curation Security Requirements

Status: `accepted for I27`.

Date: 2026-09-10.

## Purpose

Define observable authorization behavior for catalogue mutation without conflating catalogue visibility, operational responsibility and mutation permission.

## Authority actions

I27 uses:

```text
CurateApplicationCatalogue
CurateResourceCatalogue
```

Authority Management remains the sole owner of actor/action admission.

## Observable behavior

For every catalogue mutation:

1. authenticated session supplies the Actor;
2. caller selects only an explicit curation Responsibility Scope where required by the workflow;
3. backend evaluates the corresponding `Curate*Catalogue` action for the Actor/scope/effective time;
4. command validates owner-domain invariants;
5. persistence occurs only after admission and invariant validation.

The client does not supply trusted `actorId`.

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

## Scope ambiguity

A mutation requiring a curation scope must fail closed when the effective authority context is missing or ambiguous. The backend must not guess a scope from display names, Resource address, Application hierarchy or currently visible UI selection.

For Resource Scope Affiliation commands the target affiliation scope is itself the authority scope.

For ACC curation the selected Responsibility Scope is an administrative action context and does not become part of Application/Component/Deployment identity.

## Read workspace

The UI may hide or disable create/edit actions when the session has no admitted curation scope. This is presentation only.

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

The supported local demo actor may be seeded with both curation actions for `local-demo` to exercise the workflow end to end.
