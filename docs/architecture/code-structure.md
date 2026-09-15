# Code Structure

Status: `accepted target architecture; first MVP vertical additions aligned 2026-09-15; physical migration pending`.

Date: 2026-09-15.

Decision: `docs/decisions/ADR-014-target-code-structure-taxonomy.md`.
First MVP vertical architecture: `docs/architecture/first-mvp-vertical.md`.
Migration history: `docs/engineering/target-code-structure-migration-roadmap.md`.
Web UI composition guidance: `docs/ui/component-composition.md`.

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

This is the repository-level structure. The root Makefile is the stable repository-level command surface. Backend packaging and backend tests belong under `backend/`; cross-system E2E stays repository-level.

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

Accepted target contexts:
- `access_governance`;
- `access_policy`;
- `access_policy_realization`;
- `application_catalogue`;
- `application_deployment`;
- `authority_management`;
- `business_connectivity` when its target runtime replaces legacy Connectivity Requirements;
- `network_enforcement_placement`;
- `network_environment_operations`;
- `resource_catalogue`;
- `technical_access_evidence`.

Legacy/current runtime packages `connectivity_decision` and `connectivity_requirements` remain migration sources only and are not target semantic owners.

The physical repository does not yet contain all target context packages. In particular, `access_governance` and `application_deployment` are accepted semantic owners whose runtime migration is still pending. Their absence from the current tree must not be used to infer that legacy/current packages own the target semantics.

The physical `access_policy_realization` package currently contains implementation from the superseded APR model. Its current classes/use cases are migration input only; target ownership and MVP contracts are defined by `docs/domain/access-policy-realization/README.md` and `docs/requirements/access-policy-realization-mvp.md`.

### `workflows/`

Contains explicit cross-context application/read orchestration that owns no authoritative business truth.

```text
workflows/<workflow>/
  application/
  infrastructure/
  presentation/
```

Accepted target workflows include:
- `policy_realization` — first MVP technical realization orchestration from current AP Rule through RPM/PPI/APR/rendering/NEO;
- `requirement_policy_alignment` where still applicable to retained runtime journeys;
- `policy_export`;
- `scoped_connectivity_inventory`;
- `traffic_analysis`.

The physical `network_operator_view` workflow remains legacy APR-dependent implementation pending migration. It is not a target workflow contract and must not be used to infer redesigned APR stages, statuses or inputs.

A workflow may own orchestration-specific projections/read models. It consumes bounded-context application contracts/ports rather than context-owned persistence internals. If a workflow acquires independent identity, lifecycle or invariants, reconsider its bounded-context classification explicitly.

There is no generic `composition/` package. Workflow-specific implementation lives with the workflow; pure executable wiring lives in `platform/bootstrap`.

### Migration adapters

A migration adapter is allowed only when an accepted target contract must temporarily consume a superseded/current runtime representation and immediate big-bang migration would add unnecessary scope.

Rules:

- it lives in the final consumer's `infrastructure/` layer or the current semantic owner's infrastructure layer, not in a new transitional top-level package;
- it consumes the source owner's public application/read contract when available and never peer-private tables;
- it may only narrow current data to accepted target meaning; ambiguous or unrepresentable state fails closed;
- it must not establish independent business identity/lifecycle or become a second semantic owner;
- it has an explicit removal trigger tied to the target owner/runtime becoming available;
- it is not an import shim, compatibility façade for old callers, generic anti-corruption bucket or excuse to preserve superseded vocabulary in new target contracts.

The first MVP vertical currently permits bounded migration adapters for ACC-backed deployment evidence and legacy RC realization only under the constraints in `docs/architecture/first-mvp-vertical.md`. NEP requires a real target query when current runtime cannot publish the accepted target result faithfully.

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
- A cross-context local transaction, when explicitly accepted for a modular-monolith invariant, coordinates public application/repository operations without transferring table ownership or allowing peer SQL.
- No service locator or global mutable dependency registry.

## Shared code rule

Do not create a general shared business-model/utilities package.

Technical reuse belongs in the narrow owning platform/library capability. Semantic reuse stays behind explicit owner contracts. A true DDD Shared Kernel requires a separate accepted architecture/domain decision.

## Provider integration capabilities

Provider Policy Interpreter and Provider Policy Renderer are integration capabilities, not Bounded Contexts.

For the first MVP vertical their concrete adapters belong with the consuming workflow/infrastructure boundary or another narrow accepted integration owner; they must not create a new peer context merely to host provider syntax.

Provider-specific parsing/rendering must remain outside APR domain/application semantics. If provider integration later becomes large enough to justify a dedicated technical package, that package remains an integration capability and still follows inward dependency rules.

## Frontend taxonomy

`web/` is a React outer adapter with feature-first locality and one explicit generic UI owner:

```text
web/src/
  app/                         # application bootstrap/routing/shell
  design-system/
    primitives/                # smallest stable visual/layout building blocks
    components/                # generic reusable controls and focused visuals
    layout/                    # application/page geometry
    patterns/                  # reusable generic/product UI compositions
  features/<feature>/
    api/
    model/
    components/                # feature-owned presentation/domain-to-visual mapping
    pages/                     # screen/use-case orchestration roots
  components/ui/               # transitional existing generic controls; migrate when touched
  lib/                         # genuinely shared technical helpers
```

Create only feature subdirectories that have actual contents. Feature DTOs, request mapping, session/auth operations and behavior stay with their explicit feature owner. `lib/` remains technical, including shared HTTP transport/error handling and other non-semantic helpers. `app/` owns bootstrap, routing and application shell composition.

`design-system/` is the durable owner of generic visual primitives, reusable controls, application/page geometry and reusable product UI patterns. Generic design-system code must not encode NAPMS domain states or feature vocabulary. Domain-to-visual mapping and reusable domain presentation stay under the owning feature's `components/`.

`components/ui/` is transitional current structure rather than a second permanent generic-component ownership model. When a generic control is touched by the component-composition migration and its ownership is clear, move it to `design-system/components/`, migrate callers directly and remove the old owner without compatibility facades.

Feature pages are screen composition/use-case orchestration roots. They compose design-system patterns and feature components rather than defining local copies of generic controls, status visuals, dialog geometry or repeated feature presentation.

Cross-feature semantic reuse imports from the explicit owning feature; do not recreate a root API barrel or generic `shared/model` package. Detailed extraction/ownership rules live in `docs/ui/component-composition.md`.

## Structural change rules

- Preserve accepted product/domain semantics unless a separate accepted change says otherwise.
- Put new authoritative code directly under final ownership; do not create transitional semantic categories.
- Migration adapters are permitted only under the bounded rule above and never become alternate semantic owners.
- Move matching tests with their implementation boundary.
- Add/update architecture tests whenever a boundary is mechanically enforceable.
- Structural compatibility facades, transitional import shims and generic ownership buckets are forbidden.
- File size alone is not a decomposition rule; use responsibility and change coupling.
- A physical move must not silently imply semantic ownership transfer.
- Existing runtime packages explicitly marked migration-only are exceptions to target-semantic inference: their presence does not make their old vocabulary current architecture.

## Enforcement

The production backend package contains only `contexts/`, `workflows` and `platform/` at its semantic top level. Context and workflow roots admit only their applicable layers described above. `adapters/` and generic `composition/` directories are forbidden throughout `backend/src/napms/`.

Architecture tests enforce this taxonomy together with dependency direction, cross-context isolation, persistence ownership, platform HTTP neutrality, capability boundaries and feature-local Web ownership. Historical migration roadmaps provide provenance only and do not define current target structure.

When the first MVP vertical is implemented, architecture checks must also prevent:

- workflow imports from peer `domain` packages;
- direct workflow/peer SQL against ACC/AD/RC/AP/NEP-owned schemas;
- provider renderer code under APR domain;
- target contracts containing legacy ComponentDeployment, ResourceEndpoint, EnforcementAttachment or ManagedReconciliationScope identities;
- a new RPM context/repository package.

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

For Web UI changes:

```text
generic visual/control/layout behavior?
  -> design-system

feature/domain presentation?
  -> features/<owner>/components

screen/use-case orchestration?
  -> features/<owner>/pages

pure shared technical helper?
  -> lib
```

No generic composition bucket, process feature ownership, cross-context domain imports or global technical-layer tree is accepted.
