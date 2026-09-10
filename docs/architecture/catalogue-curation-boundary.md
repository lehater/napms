# Catalogue Curation Boundary

Status: `accepted for I27 Stage 0`.

Date: 2026-09-10.

## Purpose

Define the structural boundary for user-facing catalogue curation while preserving existing bounded-context ownership and Clean Architecture dependency direction.

## Owning modules

```text
Application Communication Catalogue
    owns Application / Component / Component Deployment / DCS / Deployment Resource Binding

Resource Catalogue
    owns Resource / Endpoint realization / Resource Scope Affiliation / Resource Responsibility

Authority Management
    owns actor/action admission for catalogue mutations

Web / HTTP
    outer adapters only
```

The curation workspace is not a new bounded context and owns no independent persistence truth.

## Write path

The supported write path is:

```text
Web form
  -> authenticated HTTP command DTO
  -> catalogue application command/use case
  -> Authority Management admission port
  -> owning catalogue domain invariants
  -> owning PostgreSQL repository
  -> command result/read projection
```

The Web client does not call repositories, compose database identities or make permission decisions.

## Read path

Catalogue workspaces may use dedicated owner-preserving read compositions optimized for curation:

```text
Applications workspace
  -> ACC hierarchy/read model
  -> Resource binding presentation from ACC
  -> Resource display projection from RC when needed

Resources workspace
  -> RC resource/current temporal facts
  -> optional ACC deployment-binding projection for impact/explainability
```

Cross-context composition is read-only. It does not move semantic ownership into a UI/query module.

## Dependency direction

For each owning bounded context:

```text
Domain
  <- Application / consuming Ports
      <- PostgreSQL / HTTP composition adapters
```

Authority checks are consumed through an application-owned port. Domain models do not depend on Authority Management implementation or transport concepts.

## Transaction boundaries

One command mutates one semantic owner at a time.

ACC commands that create/change ACC-owned entities transact inside the ACC repository boundary. RC commands transact inside the RC repository boundary.

I27 does not introduce distributed transactions between ACC and RC.

A Deployment Resource Binding command may validate an RC Resource through a consuming port before committing the ACC-owned binding. Failure/uncertainty fails closed; no RC record is mutated by that ACC command.

## Identity boundary

Server-side application/domain code creates authoritative identities and provenance according to the accepted command contract.

Clients may supply user-editable labels, semantic fields and expected-version/idempotency metadata, but do not supply trusted actor identity or authoritative provenance.

Existing stable IDs are preserved across migration.

## Lifecycle boundary

Retirement/end operations are explicit commands. Generic HTTP `DELETE` semantics are not the product model for entities/facts carrying historical references.

A transport may use conventional verbs internally, but the API contract must preserve the semantic distinction between:

```text
retire identity
end temporal relation
create immutable revision
rename presentation metadata
```

## DCS authoring boundary

The HTTP/Web authoring model exposes accepted communication semantics, not encoded persistence payload and not vendor ACL syntax.

The ACC application layer validates/canonicalizes the request and produces the immutable DCS projection consumed by existing read/export paths.

## Concurrency boundary

Catalogue mutations must carry an accepted concurrency precondition. Stale writes fail explicitly.

Idempotent retry and lost-update prevention are separate concerns:

- idempotency prevents duplicate command effect after retry;
- expected version prevents overwriting a newer state.

The exact shared command contract remains a Stage 0 decision before implementation.

## Security boundary

Authentication identifies the Actor. Authority Management admits the requested catalogue action for the relevant scope/action contract.

UI visibility and disabled buttons are convenience only. Every HTTP mutation re-checks authority server-side.

Catalogue visibility, Resource Responsibility and Resource Scope Affiliation do not imply catalogue mutation permission.

## Migration boundary

Schema changes are additive/conservative first:

- add missing ACC Application/Component structure and lifecycle/version metadata;
- add required RC lifecycle/display/version metadata;
- backfill deterministic compatibility structure without changing existing deployment/resource/DCS identities;
- keep existing read consumers operational during the migration stage.

Migration code may manufacture compatibility metadata only where the Tactical DDD explicitly defines deterministic fallback semantics and provenance.

## Non-goals

- generic repository CRUD endpoints;
- one cross-context catalogue aggregate;
- CMDB synchronization;
- organization/company hierarchy;
- automatic ownership-to-authority mapping;
- distributed ACC+RC transaction;
- vendor firewall configuration authoring inside catalogue forms.

## Consequences

- implementation can proceed module-by-module after remaining Stage 0 decisions close;
- UI remains a task-oriented adapter rather than a source of business truth;
- existing Connectivity/Checker/read paths can continue consuming owner APIs without depending on curation projections;
- concurrency, authorization and immutable-history semantics remain server-enforced.
