# Code Structure

Status: `accepted target for I32 structural refactoring; no product/domain semantic change`.

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

A router may be split further by use case when size or change locality demonstrates the need. File size alone is not a reason to introduce abstractions.

`runtime`/bootstrap must not become the owner of feature DTOs, endpoint logic, feature error mapping or feature-specific router implementations.

## Cross-context read/application compositions

Existing non-peer compositions remain explicit compositions rather than being moved into a bounded-context adapter for cosmetic locality.

A composition may consume multiple owner/application ports and may implement query-only technical composition where accepted architecture explicitly permits it, but it does not acquire authoritative business ownership.

I32 must inventory current `src/napms/composition/*` responsibilities before deciding their final package locations. In particular, accepted cross-schema query composition must not be moved into an owner-specific PostgreSQL adapter if that would imply false ownership or violate schema-boundary rules.

## Process composition

The target process boundary is a small bootstrap surface responsible only for executable assembly and runtime configuration, conceptually:

```text
src/napms/bootstrap/
  app.py
  config.py
  auth.py          # process authentication/session implementation when applicable
  migrations.py
  local_seed.py
  wiring/          # only when decomposition is justified by concrete wiring size
```

Migration from current `runtime/` and `composition/` is staged. The exact final location of each composition helper is determined by responsibility, not by a bulk directory rename.

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

## Migration constraints

- No big-bang package relocation.
- One coherent ownership slice per stage/PR.
- Structural moves must preserve public behavior and historical semantics.
- Prefer move/import cleanup before opportunistic redesign.
- Add architecture tests when a migrated boundary can be expressed as an executable rule.
- Keep compatibility shims only when they reduce migration risk; remove them once no longer needed.
- Do not introduce `src/napms/modules/`; existing top-level semantic modules are already sufficiently explicit and another nesting level would add import churn without ownership value.

## Current hotspots driving I32

The initial migration is justified by current structure, notably:

- `src/napms/runtime/http_api.py` aggregating HTTP concerns across multiple contexts;
- feature-specific `runtime/*_http.py`, including large Catalogue routers;
- overlapping responsibilities between `src/napms/runtime/composition.py` and `src/napms/composition/*`;
- separate runtime/composition configuration surfaces;
- large backend/Web files where change locality should be evaluated after ownership boundaries are corrected.

These are engineering structure concerns, not evidence that the accepted DDD model or modular-monolith topology is wrong.

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
