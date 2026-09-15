# ADR-014 — Target code structure taxonomy

Status: `accepted current target decision`.

Date: 2026-09-11; target semantic classification aligned 2026-09-15.

## Context

The semantic-module-first layout preserves DDD ownership, but top-level backend paths can mix three different architectural kinds: bounded contexts, cross-context application/read compositions, and process/runtime mechanics. Generic `composition`, `runtime` and `adapters` paths also hide responsibility.

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

## Target semantic classification

Target bounded contexts are:
- Business Connectivity;
- Access Governance;
- Access Policy;
- Authority Management;
- Resource Catalogue;
- Application Communication Catalogue;
- Application Deployment;
- Network Enforcement Placement;
- Technical Access Evidence;
- Access Policy Realization;
- Network Environment Operations.

Provider Policy Interpreter, Provider Policy Renderer and Technical Evidence Acquisition/Collectors are integration/application capabilities rather than peer bounded contexts. Required Policy Materialization is a derived composition, not a bounded context.

Current runtime packages such as `connectivity_requirements`, `connectivity_decision` and legacy APR/operator structures may remain as as-built compatibility or migration inputs while the target is not fully realized. Their physical presence does not make them target semantic owners.

Target cross-context workflows/compositions include, where still applicable under current contracts:
- Required Access Matrix composition for the selected first implementation slice;
- Required Policy Materialization / policy-realization orchestration;
- Policy Export / snapshot normalization;
- Scoped Connectivity Inventory;
- Traffic Analysis Checker;
- retained Requirement-to-Policy Alignment only while its as-built compatibility path remains required.

The physical `network_operator_view` workflow is legacy runtime code tied to a superseded APR model. It is as-built/migration material, not a target workflow contract. Any replacement operator workflow must be derived from the current APR contracts.

This classification follows `docs/domain/strategic-model.md`, `docs/domain/context-map.md` and `docs/architecture/code-structure.md`. Reclassification requires domain/architecture evidence, not folder convenience.

## Alternatives

- Keep semantic modules directly under `backend/src/napms/`: rejected as final target because bounded contexts, workflows and process mechanics remain visually peer-level.
- Global `domain/application/infrastructure` directories: rejected because they scatter bounded contexts across technical layers and weaken semantic ownership.
- Service per bounded context: rejected; no accepted topology driver requires distributed deployment.

## Consequences

Positive:
- path answers both "who owns this?" and "what architectural role is this?";
- cross-context orchestration is explicit rather than hidden in generic composition code;
- process mechanics cannot visually masquerade as semantic modules;
- Clean Architecture remains local to each semantic owner;
- target ownership remains explicit even while compatibility runtime packages still exist.

Costs:
- substantial import/test/CI/Docker path churn can occur when physical migration is required;
- architecture tests and agent guidance must evolve with accepted target structure;
- as-built compatibility packages must be labelled rather than inferred as target ownership.

## Reconstruction rule

This ADR defines target physical taxonomy. `docs/architecture/current-architecture.md` and current engineering/API contracts define the as-built runtime that must remain reconstructable during migration. Completed migration roadmaps are execution history and are not required as authority once their durable structural constraints are represented by this ADR and `docs/architecture/code-structure.md`.
