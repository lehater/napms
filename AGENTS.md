# NAPMS repository agent map

## Start

For non-trivial design, architecture or implementation-planning work:

1. read this file;
2. read `docs/canonical-graph.yaml` to find the current semantic owner and direct dependencies;
3. read `docs/meta/current-workstream.yaml`; if active, follow the referenced workstream state/resume protocol;
4. load only affected canonical artifacts.

Repository state, not chat history, determines where work resumes.

## Current design authority

- `docs/model/**` — strategic/tactical/domain/use-case truth.
- `docs/architecture/structurizr/workspace.dsl` — structural C4/deployment architecture.
- `docs/architecture/mvp-system-rules.yaml` — non-C4 architecture constraints.
- `docs/architecture/persistence/mvp-persistence.yaml` — physical persistence design.
- `docs/contracts/http/napms.openapi.yaml` — HTTP contract.
- `docs/plans/**` — implementation-readiness and verification intent.
- `docs/canonical-graph.yaml` — routing/dependency metadata only.
- `docs-generated/**` — generated non-canonical views.
- `docs/migration/revalidated/**` and `docs-legacy/**` — historical migration evidence.

Product code/tests are implementation/evidence. Never use them to invent or reconstruct missing product/domain/architecture semantics.

## Work

Change the smallest owning artifact set. Follow graph dependencies for downstream impact. Regenerate projections rather than editing generated diagrams.

Use `make design-check`, `make design-sync`, and `python tools/check_canonical_graph.py --affected <NODE-ID>`.

A Bounded Context is not automatically a service, process, database, team or deployment unit. Current MVP remains one browser frontend, one modular-monolith backend and one PostgreSQL database with module-owned persistence and in-process owner contracts.

Implementation readiness is not implementation authorization. Product implementation/product-test changes require separate explicit authorization. Never commit directly to `main`; use a branch and PR. Merge remains separately authorized.

Historical H/CM records are provenance/resume material, not the normal workflow. Do not invent H21 or extra CM phases outside an explicit workstream.
