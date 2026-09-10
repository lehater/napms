# ADR-006 — I27 Catalogue Identity and Lifecycle

Status: `accepted`.

Date: 2026-09-10.

## Context

NAPMS Strategic DDD already assigns Application, Component, Component Deployment and DCS identity/structure to the Application Communication Catalogue. Before I27, the implementation persisted Component Deployments and DCS revisions but did not persist first-class Application/Component parents or expose normal catalogue curation workflows.

I27 must add the missing write model without changing stable identities already referenced by Connectivity Requirements, Connectivity Decisions and Access Rules.

The product also needs safe user-facing lifecycle semantics. Generic hard delete would be unsafe because catalogue identities are referenced by immutable/historical policy and decision facts.

## Decision

### Identity hierarchy

ACC uses the following stable hierarchy:

```text
Application
  -> Component
      -> Component Deployment
```

Application, Component and Component Deployment each have stable server-owned UUID identity.

A Component belongs to one Application for its lifetime. A Component Deployment belongs to one Component for its lifetime. Parent reassignment is not an in-place mutation; a changed structural meaning is represented by replacement plus retirement where appropriate.

Existing `component_deployment_id` values remain unchanged and continue to be the deployment identities consumed by downstream contexts.

### Lifecycle

Application, Component and Component Deployment use:

```text
Active -> Retired
```

Retirement is terminal in the I27 slice. Normal product commands do not hard-delete these identities.

Parent retirement is rejected while active children exist:

- Application with Active Components cannot be retired;
- Component with Active Component Deployments cannot be retired.

Component Deployment retirement may occur while historical DCS, binding or downstream policy references exist; those references remain valid historical truth.

DCS revisions remain immutable and are replaced by creating another revision when semantics change.

### Existing-data migration

I27 schema migration preserves every existing Component Deployment and DCS UUID.

Because pre-I27 state contains no trustworthy Application/Component grouping facts, migration creates:

```text
one deterministic compatibility Application: "Imported catalogue"

one deterministic compatibility Component per existing deployment

existing deployment -> its compatibility Component
```

Compatibility Component identity is derived deterministically from the existing deployment UUID using a repository-defined namespace/algorithm. Migration does not group by equal display names and does not infer ownership or business structure.

Migration provenance identifies the I27 compatibility migration explicitly.

## Alternatives rejected

### Group legacy deployments by display name

Rejected because display name is presentation metadata, not identity evidence. Equal names do not prove one logical Component.

### Put all legacy deployments directly under one Component

Rejected because it collapses distinctions and creates an unsupported shared Component identity.

### Mutable parent references

Rejected because moving Component/Deployment parents in place silently changes structural meaning around already referenced stable deployment identities.

### Hard delete when database foreign keys permit it

Rejected because downstream historical references and provenance are product truth even when a physical cascade could be made technically possible.

## Consequences

- ACC gains a complete structural write model without changing existing policy subject identities.
- User-facing deletion semantics become explicit retirement.
- Legacy data remains valid and receives conservative compatibility parents rather than guessed business grouping.
- PostgreSQL schema, repository ports, commands, HTTP and Web work may implement this decision after the remaining I27 Stage 0 authority, DCS-authoring and command-concurrency decisions are accepted.

## Owned detail

Detailed entity fields, invariants and migration constraints are maintained in `docs/domain/application-communication-catalogue/tactical-model.md`.
