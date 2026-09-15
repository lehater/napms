# Code structure

Status: `current target structure with explicit as-built compatibility boundaries`.

Decision: `docs/decisions/ADR-014-target-code-structure-taxonomy.md`.

## Purpose

Repository paths should make ownership and dependency direction visible without requiring code archaeology. A developer should be able to determine whether a change belongs to an authoritative semantic owner, a cross-context workflow, or technical process/runtime composition.

The exact current implemented runtime structure is documented by `docs/architecture/current-architecture.md` and `docs/engineering/current-state.md`. This document defines the structural target and the rules that current/as-built compatibility code must respect.

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

The root Makefile is the stable repository-level command surface. Backend packaging and backend tests belong under `backend/`; cross-system E2E remains repository-level.

## Backend taxonomy

### `contexts/`

Authoritative semantic owners live under:

```text
contexts/<context>/
  domain/
  application/
  infrastructure/
  presentation/
```

Create only layers that have real responsibility.

- `domain/` — identities, invariants, domain values/services/events/errors;
- `application/` — use cases, within-context orchestration, DTO/contracts and consumer-owned ports;
- `infrastructure/` — persistence and outbound/integration implementations;
- `presentation/` — inbound HTTP/CLI/other delivery adapters.

Current target context owners are:

- `access_governance`;
- `access_policy`;
- `access_policy_realization`;
- `application_catalogue`;
- `application_deployment`;
- `authority_management`;
- `business_connectivity`;
- `network_enforcement_placement`;
- `network_environment_operations`;
- `resource_catalogue`;
- `technical_access_evidence`.

The physical runtime may still contain as-built compatibility modules such as `connectivity_requirements`, `connectivity_decision` or implementation derived from an older APR model. Their presence is part of the reconstructable current implementation, documented in the as-built architecture/contracts, but it does not make those packages target semantic owners.

One context never imports another context's private `domain` model merely for convenience. Cross-context interaction uses explicit application contracts/ports and opaque semantic references.

### `workflows/`

`workflows/` contains explicit cross-context application/read orchestration that owns no authoritative business truth.

```text
workflows/<workflow>/
  application/
  infrastructure/
  presentation/
```

Current as-built workflows include owner-preserving compositions such as policy export, scoped connectivity inventory and traffic analysis where documented by their architecture/engineering contracts.

A workflow may own orchestration-specific read models or rebuildable projections. It does not acquire independent identity/lifecycle/invariants merely because it combines several contexts, and it does not read or mutate peer-private tables.

The selected Required Access Matrix MVP is also cross-context composition over ACC + AD + RC. Its exact physical workflow/package name, API boundary, snapshot/consistency mechanism and export/UI adapter remain S3 decisions; no package name is canonical until that architecture is accepted.

### Compatibility and migration adapters

A compatibility adapter is permitted when current as-built data/contracts must be translated into an accepted target contract without a big-bang rewrite.

Rules:

- it lives in the consumer's or semantic owner's outer/infrastructure layer, not in a new semantic top-level bucket;
- it consumes public owner contracts where available, never peer-private persistence;
- it may only translate/narrow to accepted meaning; ambiguous or unrepresentable state remains explicit/fail-closed where required;
- it does not establish independent business identity/lifecycle;
- it does not make compatibility vocabulary authoritative for new target contracts;
- its existence and semantics must be documented while the current system depends on it.

Compatibility code is not historical while it remains required to reconstruct the current product.

### `platform/`

`platform/` contains process/execution concerns only:

```text
platform/
  bootstrap/
  auth/
  database/
  http/
  observability/   # when concrete shared responsibility exists
```

Typical responsibilities are executable dependency wiring, process configuration, migrations/process-level database support, authentication/session infrastructure, generic HTTP support and logging/metrics/tracing infrastructure.

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
- Application depends on its own Domain and explicit consumer-owned ports/contracts.
- Infrastructure and Presentation depend inward.
- Bootstrap may depend on concrete context/workflow outer layers to assemble the process.
- Cross-context interaction uses explicit application contracts/ports.
- Workflows do not bypass semantic ownership through direct reads/writes of context-owned persistence.
- Physical PostgreSQL colocation does not create cross-context table ownership.
- A cross-context transaction or coherent snapshot exists only when explicitly accepted by Architecture.
- No service locator or global mutable dependency registry is allowed.

## Shared-code rule

Do not create a generic shared business-model/utilities package.

Technical reuse belongs in a narrow platform/library capability. Semantic reuse stays behind explicit owner contracts. A true DDD Shared Kernel requires an explicit accepted domain/architecture decision.

## Provider integration capabilities

Provider Policy Interpreter and Provider Policy Renderer are integration capabilities, not peer Bounded Contexts. Provider-specific parsing/rendering remains outside APR domain/application semantics.

A provider adapter belongs at the narrow consuming workflow/infrastructure boundary unless a demonstrated technical responsibility justifies a dedicated integration package. Such a package still follows inward dependency rules and does not acquire policy-semantic ownership.

## Frontend taxonomy

The React Web adapter uses feature-first locality and one durable generic UI owner:

```text
web/src/
  app/                         # bootstrap, routing, shell
  design-system/
    primitives/
    components/
    layout/
    patterns/
  features/<feature>/
    api/
    model/
    components/
    pages/
  components/                  # reusable non-domain composition where justified
  lib/                         # genuinely shared technical helpers
```

Feature DTOs, request mapping and product presentation stay with the explicit feature owner. `lib/` remains technical. `app/` owns bootstrap/routing/application shell.

`design-system/` owns generic visual primitives, reusable controls, application/page geometry and reusable UI patterns. It must not encode NAPMS domain states or feature vocabulary. Domain-to-visual mapping belongs to the owning feature.

Feature pages are screen/use-case orchestration roots. They compose design-system patterns and feature components rather than reimplementing generic controls or creating parallel styling systems. Detailed ownership/extraction rules live in `docs/ui/component-composition.md`.

## Structural change rules

- Preserve accepted product/domain semantics unless the owning layer changes first.
- Put new authoritative code directly under its final semantic owner.
- Do not create transitional semantic top-level categories.
- Keep as-built compatibility adapters only where the current design requires them and document their boundary.
- Move matching tests with their implementation boundary when structure changes.
- Add/update architecture tests for mechanically enforceable boundaries.
- File size alone is not a decomposition rule; use responsibility and change coupling.
- A physical move never silently transfers semantic ownership.

## Mechanical enforcement

Architecture checks should protect at least:

- allowed semantic top-level package taxonomy;
- Domain framework/persistence independence;
- cross-context domain isolation;
- consumer-owned port direction;
- no peer-private persistence access;
- provider-specific code outside source-neutral domain models;
- design-system independence from feature/domain semantics;
- feature-local Web ownership where applicable.

For the Required Access Matrix slice, S3 should add checks for whatever concrete ownership/package boundaries it accepts, especially preventing direct ACC/AD/RC private persistence access and accidental introduction of a new semantic `RequiredAccessMatrix` bounded context unless S2 explicitly changes.

## Reconstruction rule

The combination of this target structure, `current-architecture.md`, current ADRs and engineering contracts must be sufficient to recreate both the designed as-built topology and the accepted target ownership boundaries. Do not delete structural documentation merely because the corresponding structure is already implemented.
