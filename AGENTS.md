# NAPMS repository rules

## Scope

This repository is the source of truth for the new NAPMS product. Legacy code and reconstruction evidence are external evidence only and must not define target behavior.

## Change discipline

- Do not commit directly to `main`; use a branch and a PR.
- Prefer squash merge for one coherent semantic change.
- Keep accepted product/domain/architecture meaning explicit in `docs/`.
- When code and documentation disagree, resolve the semantic conflict rather than silently choosing the implementation.
- Do not import or copy Legacy models merely to accelerate implementation.

## Architecture

- Modular application; a Bounded Context is not automatically a service/deployment unit.
- Dependencies point inward: Domain <- Application/Ports <- Adapters/Composition.
- Domain has no framework, database, transport, configuration, logging or DI-container dependencies.
- Application consumes explicit ports owned by the consuming module.
- Use constructor injection; no service locator/global mutable dependency registry.
- Business audit/provenance is domain truth; operational logs do not replace it.

## Implementation order

For every behavior:
1. accepted requirement/semantic contract;
2. Domain + Application + Ports;
3. core/architecture tests;
4. only then infrastructure adapters and integration tests.

The current infrastructure gate remains closed until I1 core tests and architecture review are green with no open P0/P1 issue.

## Documents

- `docs/domain/`: living Strategic/Tactical DDD.
- `docs/requirements/`: accepted product behavior and quality requirements.
- `docs/architecture/`: current target architecture.
- `docs/decisions/`: durable ADRs.
- `docs/engineering/`: error, observability, configuration, DI and implementation rules.
- `docs/baseline/`: accepted baseline/readiness snapshots; not the primary place to edit current semantics.
