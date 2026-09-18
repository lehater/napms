# NAPMS design documentation

Status: CANONICAL.

`docs/` is the sole current design/documentation authority. Current truth is organized by semantic ownership, not by historical migration phase.

## Start here

For non-trivial design/architecture/planning work:

1. read `../AGENTS.md`;
2. read `canonical-graph.yaml` to locate the owning artifact and direct dependencies;
3. read `meta/current-workstream.yaml`; if it points to an active workstream, follow that workstream's resume protocol;
4. load only the owning artifacts and affected dependencies needed by the task.

Do not reconstruct missing product/domain/architecture truth from product code, tests, old chat, or retired migration artifacts.

## Current canonical areas

- `discovery/` — evidence/problem discovery that still matters to current design.
- `model/strategic/` — capability, Bounded Context and relationship ownership.
- `model/contexts/` — context-owned tactical semantics.
- `model/use-cases/` — cross-context/application journeys and use cases.
- `architecture/structurizr/workspace.dsl` — canonical C4 structural/deployment model.
- `architecture/mvp-system-rules.yaml` — non-C4 system architecture rules.
- `architecture/persistence/mvp-persistence.yaml` — canonical first-MVP physical persistence model.
- `contracts/http/napms.openapi.yaml` — canonical first-MVP HTTP contract.
- `plans/` — implementation readiness and verification intent; these never authorize implementation by themselves.
- `canonical-graph.yaml` — routing/dependency metadata only; it does not duplicate semantic truth.

## Generated views

`docs-generated/` is disposable and non-canonical. Context maps, domain/process diagrams, journey views and ERD are generated from the owners above.

Use `make design-check` to validate current canonical truth and `make design-sync` to regenerate projections.

To inspect downstream impact: `python tools/check_canonical_graph.py --affected AP-DOMAIN`.

## Historical material

- `migration/revalidated/` — frozen evidence from the earlier anchor-shaped migration, not normal current-truth navigation.
- `horizontal/`, `review/`, `pilot/` — retained redesign/migration/pilot evidence where still useful.
- `docs-legacy/` — retired pre-cutover evidence only.

Historical material cannot override the current canonical owners.
