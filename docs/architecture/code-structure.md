# Code Structure

Status: `accepted current architecture`.

Date: 2026-09-11.

Decision: `docs/decisions/ADR-014-target-code-structure-taxonomy.md`.
Migration history: `docs/engineering/target-code-structure-migration-roadmap.md`.

## Purpose

Make path structure answer three questions without repository-wide search:
1. is this authoritative domain ownership, cross-context orchestration, or technical execution;
2. which semantic capability owns the change;
3. which Clean Architecture layer contains it.

## Repository structure

```text
napms/
  backend/
    pyproject.toml
    Dockerfile
    src/napms/
      contexts/
      workflows/
      platform/
    tests/
  web/
  e2e/
  deploy/
  tools/
  docs/
  .agents/
  .github/
  Makefile
  README.md
```

This is the current physical repository structure. The root Makefile is the stable repository-level command surface. Backend packaging and backend tests belong under `backend/`; cross-system E2E stays repository-level.

## Backend taxonomy

### `contexts/`

Contains bounded contexts and authoritative semantic owners.

```text
contexts/<context>/
  domain/
  application/
  infrastructure/
  presentation/
```

Create only layers that have actual responsibility.

- `domain/` — model, invariants, domain services/events/errors.
- `application/` — use cases, orchestration within the context, DTO/contracts and consumer-owned ports.
- `infrastructure/` — persistence and outbound/integration implementations.
- `presentation/` — inbound HTTP/CLI/other delivery adapters.

Large application layers are decomposed by capability/use case only when responsibility and change locality justify it.

Accepted contexts:
- `access_policy`;
- `access_policy_realization`;
- `application_catalogue`;
- `authority_management`;
- `connectivity_decision`;
- `connectivity_requirements`;
- `network_enforcement_placement`;
- `network_environment_operations`;
- `resource_catalogue`;
- `technical_access_evidence`.

### `workflows/`

Contains explicit cross-context application/read orchestration that owns no authoritative business truth.

```text
workflows/<workflow>/
  application/
  infrastructure/
  presentation/
```

Accepted workflows:
- `requirement_policy_alignment`;
- `policy_export`;
- `scoped_connectivity_inventory`;
- `network_operator_view`;
- `traffic_analysis`.

A workflow may own orchestration-specific projections/read models. It consumes bounded-context application contracts/ports rather than context-owned persistence internals. If a workflow acquires independent identity, lifecycle or invariants, reconsider its bounded-context classification explicitly.

There is no generic `composition/` package. Workflow-specific implementation lives with the workflow; pure executable wiring lives in `platform/bootstrap`.

### `platform/`

Contains technical process/execution concerns only:

```text
platform/
  bootstrap/
  auth/
  database/
  http/
  observability/   # only when concrete shared responsibility exists
```

Typical responsibilities:
- executable dependency wiring;
- process configuration;
- migrations/process-level database support;
- authentication/session infrastructure;
- generic HTTP shell/support;
- logging/metrics/tracing infrastructure.

`platform` never owns feature behavior or domain semantics.

## Dependency direction

```text
domain
  <- application
      <- infrastructure / presentation
          <- platform/bootstrap wiring
```

Rules:
- Domain has no framework, persistence, transport, configuration, logging or DI dependencies.
- Application depends on its Domain and explicit consumer-owned ports/contracts.
- Infrastructure and Presentation depend inward.
- Bootstrap may depend on concrete context/workflow outer layers to assemble the process.
- One context does not import another context's `domain`.
- Cross-context interaction uses explicit application contracts/ports.
- Workflows do not bypass semantic ownership through direct reads/writes of context-owned persistence.
- No service locator or global mutable dependency registry.

## Shared code rule

Do not create a general shared business-model/utilities package.

Technical reuse belongs in the narrow owning platform/library capability. Semantic reuse stays behind explicit owner contracts. A true DDD Shared Kernel requires a separate accepted architecture/domain decision.

## Frontend taxonomy

`web/` is a React outer adapter with feature-first locality:

```text
web/src/
  app/                    # application bootstrap/routing/shell
  features/<feature>/
    api/
    model/
    components/
    pages/
  components/ui/          # genuinely shared visual primitives
  lib/                    # genuinely shared technical helpers
```

Create only feature subdirectories that have actual contents. Feature DTOs, request mapping, session/auth operations and behavior stay with their explicit feature owner. `lib/` remains technical, including shared HTTP transport/error handling and other non-semantic helpers. `app/` owns bootstrap, routing and application shell composition.

Cross-feature semantic reuse imports from the explicit owning feature; do not recreate a root API barrel or generic `shared/model` package.

## Structural change rules

- Preserve accepted product/domain semantics unless a separate accepted change says otherwise.
- Put code directly under final ownership; do not create transitional architectural categories.
- Move matching tests with their implementation boundary.
- Add/update architecture tests whenever a boundary is mechanically enforceable.
- Structural compatibility facades, transitional import shims and generic ownership buckets are forbidden.
- File size alone is not a decomposition rule; use responsibility and change coupling.
- A physical move must not silently imply semantic ownership transfer.

## Enforcement

The production backend package contains only `contexts/`, `workflows/` and `platform/` at its semantic top level. Context and workflow roots admit only their applicable layers described above. `adapters/` and generic `composition/` directories are forbidden throughout `backend/src/napms/`.

Architecture tests enforce this taxonomy together with dependency direction, cross-context isolation, persistence ownership, platform HTTP neutrality, capability boundaries and feature-local Web ownership. Historical migration roadmaps provide provenance only and do not define current structure.

## Success condition

A normal change should be locatable as:

```text
business owner?
  -> contexts/<context>

cross-context scenario?
  -> workflows/<workflow>

process/runtime mechanics?
  -> platform/<capability>

then
  -> domain / application / infrastructure / presentation
  -> capability/use case when further decomposition is justified
```

No generic composition bucket, process feature ownership, cross-context domain imports or global technical-layer tree is accepted.
