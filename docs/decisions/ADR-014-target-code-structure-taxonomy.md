# ADR-014 — Target code structure taxonomy

Status: `accepted`.

Date: 2026-09-11.

## Context

The current semantic-module-first layout preserves DDD ownership, but top-level backend paths still mix three different architectural kinds: bounded contexts, cross-context application/read compositions, and process/runtime mechanics. Generic `composition`, `runtime` and `adapters` paths also hide responsibility.

The target is optimized for long-term readability and boundary enforcement rather than migration cost.

## Decision

Keep NAPMS as a modular monolith, but make architectural kind explicit in the physical tree.

```text
backend/src/napms/
  contexts/       # bounded contexts / authoritative semantic owners
  workflows/      # cross-context application/read orchestration; no authoritative business truth
  platform/       # process/runtime/bootstrap/technical execution concerns
```

A bounded context uses Clean Architecture internally:

```text
contexts/<context>/
  domain/
  application/
  infrastructure/
  presentation/
```

Only layers with real responsibility are created.

- `domain` owns business model and invariants.
- `application` owns use cases and consumer-owned ports.
- `infrastructure` implements persistence and external/integration adapters.
- `presentation` owns HTTP/CLI/other inbound delivery adapters.

Large application layers are further decomposed by capability/use case, not by generic technical buckets or numeric file-size thresholds.

A workflow normally has:

```text
workflows/<workflow>/
  application/
  infrastructure/
  presentation/
```

A workflow coordinates explicit contracts from multiple contexts and may own projections/read models required by that workflow. It does not own or copy authoritative domain state. If a workflow acquires independent business identity, lifecycle or invariants, that is evidence to reconsider it as a bounded context.

`platform` contains only technical execution concerns such as bootstrap/wiring, configuration, database process support/migrations, authentication/session infrastructure, generic HTTP shell/support and observability. Product feature behavior does not live there.

There is no generic top-level `composition/` in the target. A concrete cross-context composition lives with the workflow that owns the orchestration; pure executable wiring lives in `platform/bootstrap`.

There is no general-purpose shared business-model package. Cross-context reuse occurs through explicit application contracts/ports. A true DDD Shared Kernel requires a separate explicit decision.

Repository target:

```text
napms/
  backend/
    pyproject.toml
    Dockerfile
    src/napms/
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

The root Makefile remains the repository-level orchestration entry point. Backend-specific packaging and tests belong under `backend/`; system E2E remains repository-level.

## Dependency rules

```text
domain
  <- application
      <- infrastructure / presentation
          <- platform/bootstrap wiring
```

Additional rules:
- one context does not import another context's `domain`;
- cross-context use goes through explicit application contracts/ports;
- workflow application code may consume multiple context contracts but cannot bypass context ownership through direct persistence access;
- `platform` cannot become a product-feature owner;
- `infrastructure` and `presentation` never define authoritative business semantics.

## Current module classification

Bounded contexts:
- Access Policy;
- Access Policy Realization;
- Application Communication Catalogue;
- Authority Management;
- Connectivity Decision;
- Connectivity Requirements;
- Network Enforcement Placement;
- Network Environment Operations;
- Resource Catalogue;
- Technical Access Evidence.

Cross-context workflows:
- Requirement-to-Policy Alignment;
- Policy Export / snapshot normalization;
- Scoped Connectivity Inventory;
- Network Operator Realization View;
- Traffic Analysis Checker.

This classification preserves current semantic ownership. Reclassification requires domain/architecture evidence, not folder convenience.

## Alternatives

- Keep semantic modules directly under `backend/src/napms/`: rejected as final target because bounded contexts, workflows and process mechanics remain visually peer-level.
- Global `domain/application/infrastructure` directories: rejected because they scatter bounded contexts across technical layers and weaken semantic ownership.
- Service per bounded context: rejected; no accepted topology driver requires distributed deployment.

## Consequences

Positive:
- path answers both "who owns this?" and "what architectural role is this?";
- cross-context orchestration is explicit rather than hidden in generic composition code;
- process mechanics cannot visually masquerade as semantic modules;
- Clean Architecture remains local to each semantic owner.

Costs:
- substantial import/test/CI/Docker path churn during migration;
- temporary compatibility shims may be required;
- architecture tests and agent guidance must evolve with each migration stage.

## Migration

The ordered migration and stage gates are defined in `docs/engineering/target-code-structure-migration-roadmap.md`. Active execution state is kept only under `docs/plans/active/`.
