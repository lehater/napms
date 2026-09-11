# Code Structure

Status: `accepted target architecture; migration in progress`.

Date: 2026-09-11.

Decision: `docs/decisions/ADR-014-target-code-structure-taxonomy.md`.
Migration: `docs/engineering/target-code-structure-migration-roadmap.md`.

## Purpose

Make path structure answer three questions without repository-wide search:
1. is this authoritative domain ownership, cross-context orchestration, or technical execution;
2. which semantic capability owns the change;
3. which Clean Architecture layer contains it.

## Repository target

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

The root Makefile remains the stable repository-level command surface. Backend packaging and backend tests belong under `backend/`; cross-system E2E stays repository-level.

## Backend taxonomy

### `contexts/`

Contains bounded contexts / authoritative semantic owners.

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

Large application layers are decomposed by capability/use case when change locality demonstrates separate responsibilities.

Accepted context classification:
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

Accepted workflow classification:
- `requirement_policy_alignment`;
- `policy_export`;
- `scoped_connectivity_inventory`;
- `network_operator_view`;
- `traffic_analysis`.

A workflow may own orchestration-specific projections/read models. It must consume bounded-context contracts/ports rather than context-owned persistence internals. If it acquires independent identity, lifecycle or invariants, reconsider its classification explicitly.

There is no generic target `composition/` package. Workflow-specific composition lives with the workflow; pure executable wiring lives in `platform/bootstrap`.

### `platform/`

Contains only technical process/execution concerns:

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
- Workflows do not bypass semantic ownership through direct writes/reads of context-owned persistence.
- No service locator or global mutable dependency registry.

## Shared code rule

Do not create a general shared business-model/utilities package.

Technical reuse belongs in the narrow owning platform/library capability. Semantic reuse stays behind explicit owner contracts. A true DDD Shared Kernel requires a separate accepted architecture/domain decision.

## Frontend target

`web/` remains a React outer adapter with feature-first locality:

```text
web/src/
  app/                    # application bootstrap/routing/providers
  features/<feature>/
    api/
    model/
    components/
    pages/
  components/ui/          # reusable visual primitives
  lib/                    # genuinely shared technical helpers
```

Feature DTO/request mapping and behavior stay feature-local. Root/shared API code contains only genuinely cross-feature transport/auth/session mechanics.

## Structural change rules

- Preserve accepted product/domain semantics unless a separate accepted change says otherwise.
- Move code directly toward final ownership; do not create new transitional architectural categories.
- Move matching tests with their implementation boundary.
- Add/update architecture tests whenever a migrated boundary is mechanically enforceable.
- Temporary compatibility shims are allowed only to keep integrated stages working and must be removed by the final migration stage.
- File size alone is not a decomposition rule; use responsibility and change coupling.
- A physical move must not silently imply semantic ownership transfer.

## Migration state

The current implementation still contains legacy top-level semantic modules plus `composition/`, `runtime/` and `bootstrap/`. Those are migration inputs, not the final target.

The ordered `AS-IS -> TO-BE` map, stage sequence and gates are owned by `docs/engineering/target-code-structure-migration-roadmap.md`. The currently selected stage is owned by `docs/plans/active/`.

## Success condition

A developer or agent can locate a normal change as:

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

No generic composition bucket, process feature ownership, cross-context domain imports or global technical-layer tree remains.
