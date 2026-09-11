# Code Structure

Status: `accepted current architecture; no product/domain semantic change`.

Date: 2026-09-11.

## Purpose

Make repository ownership and dependency direction visible from paths so a developer or agent can locate one change without first scanning cross-context runtime files.

This structure refactoring preserves the accepted modular-monolith topology and all current domain, API, persistence and Web semantics. It does not introduce services, new bounded contexts or shared business models.

## Structural axis

NAPMS remains **semantic module / bounded context first, Clean/Hexagonal layers second**.

Do not reorganize the backend into global `domain/`, `application/` and `infrastructure/` directories. That would mix bounded contexts inside technical layers and weaken the ownership boundaries already enforced by architecture tests.

First-class semantic modules remain directly visible under `src/napms/`.

Within a semantic module use only layers that have real responsibility:

```text
src/napms/<semantic-module>/
  domain/
  application/
  adapters/
    postgres/      # when the module owns persistence
    http/          # when the module exposes HTTP
    ...            # other concrete outer adapters when required
```

Do not create empty `domain/`, `application/` or `adapters/` directories merely to make packages look uniform.

## Dependency direction

The existing dependency rule remains authoritative:

```text
Domain
  <- Application / consuming Ports
      <- Adapters
          <- Bootstrap / process composition
```

- Domain contains no framework, persistence, transport, configuration, logging or DI concerns.
- Application depends on its Domain and consumer-owned ports.
- Adapters depend inward and implement/invoke those ports.
- Process/bootstrap code may depend on modules and adapters to assemble the executable application.
- Domain/Application never import bootstrap/runtime code.

## HTTP ownership

Feature HTTP is an outer adapter and belongs next to the semantic owner or explicit read/application composition it exposes.

For example:

```text
application_catalogue/
  domain/
  application/
  adapters/
    postgres/
    http/
      router.py
      requests.py
      responses.py
      mapping.py
```

A router may be split further by use case when change locality demonstrates the need. File size alone is not a reason to introduce abstractions.

Feature routers, DTO and error mappings, and feature serializers belong to their semantic owners. `runtime` and `bootstrap` must not become their owner.

## Cross-context read/application compositions

Existing non-peer compositions remain explicit under `src/napms/composition/` rather than being moved into a bounded-context adapter for cosmetic locality.

A composition may consume multiple owner/application ports and may implement query-only technical composition where accepted architecture explicitly permits it, but it does not acquire authoritative business ownership.

Accepted cross-schema query composition must not be moved into an owner-specific PostgreSQL adapter if that would imply false ownership or violate schema-boundary rules.

## Runtime and bootstrap ownership

`runtime/` is limited to genuine process/runtime concerns:

- authentication and session support;
- the process HTTP shell;
- generic transport support;
- the accepted enterprise identity seam.

`bootstrap/` owns executable assembly, configuration, migrations and local seed:

```text
src/napms/bootstrap/
  app.py
  config.py
  migrations.py
  local_seed.py
  wiring/          # only when decomposition is justified by concrete wiring size
```

Legacy runtime feature facades and `legacy_http_api.py` are absent. Feature code is registered by executable composition without making the process shell its semantic owner.

## Frontend

`web/` remains a React outer adapter and keeps the existing feature/use-case-first direction.

Target shape is incremental:

```text
web/src/
  app/             # application bootstrap/routing/providers
  features/
    <feature>/
      api/
      model/
      components/
      pages/
  components/ui/   # genuinely reusable visual primitives
  lib/             # genuinely shared technical helpers
```

Feature-local code stays local until reuse is demonstrated. Global `api.ts` is limited over time to shared transport mechanics; feature DTO/request mapping belongs at the feature API boundary.

## Structural change constraints

- Structural moves must preserve public behavior and historical semantics.
- Prefer move/import cleanup before opportunistic redesign.
- Add architecture tests when a migrated boundary can be expressed as an executable rule.
- Keep compatibility shims only when they reduce migration risk; remove them once no longer needed.
- Do not introduce `src/napms/modules/`; existing top-level semantic modules are already sufficiently explicit and another nesting level would add import churn without ownership value.
- Further structural work requires new, concrete ownership or change-locality evidence; completed cleanup is not a reason for automatic continuation.

## Current structural baseline

The semantic-module-first structure, owner-local feature adapters, explicit cross-context compositions, small runtime process surface and bootstrap-owned executable assembly are the accepted baseline. Architecture tests protect boundaries that can be expressed mechanically.

## Success condition

A normal change should be discoverable primarily from its semantic owner:

```text
feature/use case
  -> semantic module
  -> HTTP adapter or application use case
  -> consuming port
  -> concrete adapter
  -> bootstrap only when wiring changes
```

The refactoring is successful when this path is reliable and architecture tests prevent feature concerns from accumulating again in the process/bootstrap surface.
