# Target Code Structure Migration Roadmap

Status: `active long-range roadmap`.

Date: 2026-09-11.

Architecture decision: `docs/decisions/ADR-014-target-code-structure-taxonomy.md`.
Canonical target structure: `docs/architecture/code-structure.md`.

## Goal

Migrate the repository to the final structure without changing product/domain semantics:

```text
backend/src/napms/
  contexts/
  workflows/
  platform/
```

with context-local Clean Architecture:

```text
contexts/<context>/
  domain/
  application/
  infrastructure/
  presentation/
```

The migration is allowed to be large, but every integrated stage must leave `main` working and architecture-testable.

## AS-IS -> TO-BE classification

### Contexts

```text
src/napms/access_policy
  -> backend/src/napms/contexts/access_policy
src/napms/access_policy_realization
  -> backend/src/napms/contexts/access_policy_realization
src/napms/application_catalogue
  -> backend/src/napms/contexts/application_catalogue
src/napms/authority_management
  -> backend/src/napms/contexts/authority_management
src/napms/connectivity_decision
  -> backend/src/napms/contexts/connectivity_decision
src/napms/connectivity_requirements
  -> backend/src/napms/contexts/connectivity_requirements
src/napms/network_enforcement_placement
  -> backend/src/napms/contexts/network_enforcement_placement
src/napms/network_environment_operations
  -> backend/src/napms/contexts/network_environment_operations
src/napms/resource_catalogue
  -> backend/src/napms/contexts/resource_catalogue
src/napms/technical_access_evidence
  -> backend/src/napms/contexts/technical_access_evidence
```

Layer mapping inside each context:

```text
domain/          -> domain/
application/     -> application/
adapters/http/   -> presentation/http/
adapters/postgres/ and outbound adapters
                 -> infrastructure/
```

Adapter files that mix inbound and outbound responsibility must be split by responsibility during the move, not copied into a generic target bucket.

### Workflows

```text
src/napms/requirement_policy_alignment
  -> backend/src/napms/workflows/requirement_policy_alignment
src/napms/policy_export
  -> backend/src/napms/workflows/policy_export
src/napms/scoped_connectivity_inventory
  -> backend/src/napms/workflows/scoped_connectivity_inventory
src/napms/network_operator_view
  -> backend/src/napms/workflows/network_operator_view
src/napms/traffic_analysis
  -> backend/src/napms/workflows/traffic_analysis
```

Cross-context implementations currently under `src/napms/composition/` are classified file-by-file:
- workflow-specific query/orchestration implementation -> owning workflow `infrastructure/`;
- context-specific outbound/persistence implementation -> owning context `infrastructure/` only when semantic ownership is true;
- pure executable dependency wiring -> `platform/bootstrap/`.

No target file remains under a generic `composition/` package.

### Platform

Current `bootstrap/`, `runtime/` and remaining process mechanics become explicit platform capabilities:

```text
backend/src/napms/platform/
  bootstrap/
  auth/
  database/
  http/
  observability/    # when/where actual responsibility exists
```

`platform` owns no feature/domain behavior.

## Migration strategy

### M0 — Canonical target and execution state

Deliverables:
- ADR-014 accepted;
- `docs/architecture/code-structure.md` changed from current-layout policy to target-layout contract;
- this roadmap created;
- active plan/capsule created.

Exit gate:
- documentation/harness/knowledge checks applicable to architecture planning pass;
- no production code moved yet.

### M1 — Repository backend boundary

Mechanically create the final backend workspace first:

```text
pyproject.toml        -> backend/pyproject.toml
Dockerfile            -> backend/Dockerfile
src/                  -> backend/src/
tests/                -> backend/tests/
```

Update root Makefile, CI paths/commands, Compose/build references and developer tooling in the same stage. Root Makefile remains the stable repository command surface.

Rules:
- no semantic/module refactor in M1;
- preserve all existing import paths inside the Python package;
- `make test`, `make check` and required hosted gates must still represent the same checks.

Exit gate: backend/core + harness + knowledge + Docker/integration gates affected by path changes pass.

### M2 — Bounded contexts to final paths

Move each bounded context directly to `backend/src/napms/contexts/<context>/` and normalize its outer layers in the same slice:

```text
adapters/http        -> presentation/http
adapters/postgres    -> infrastructure/persistence/postgres (when useful)
other outbound adapters -> infrastructure/integrations or capability-named infrastructure package
```

Execution order:
1. least-coupled/small contexts first;
2. then contexts with moderate cross-context consumers;
3. Application Communication Catalogue and Access Policy last because they have the broadest integration surface.

For each context slice:
- move code and matching tests together;
- update all imports/consumer ports in the repository;
- add/update architecture tests for the new boundary;
- use a temporary compatibility shim only when it materially reduces integration risk;
- remove the shim before M7.

Exit gate per slice: relevant unit, architecture and integration tests pass; no old implementation remains duplicated.

### M3 — Workflows and elimination of generic composition

Move the five accepted cross-context compositions under `workflows/`.

For each workflow:
- application orchestration stays under `application/`;
- HTTP becomes `presentation/http/`;
- PostgreSQL/query/external composition becomes `infrastructure/`;
- dependencies on contexts use explicit application contracts/ports only.

Then drain `src/napms/composition/` by classifying every file against the rules above. `composition/` is deleted when empty.

Exit gate:
- no generic cross-context composition package remains;
- architecture tests prohibit direct workflow access to context-owned persistence internals.

### M4 — Platform consolidation

Move genuine process concerns from `bootstrap/` and `runtime/` into `platform/`.

Target responsibilities:
- `platform/bootstrap` — executable assembly and wiring;
- `platform/auth` — authentication/session and enterprise identity mechanics;
- `platform/database` — process-level database/migration support;
- `platform/http` — generic process HTTP shell/support only;
- `platform/observability` — only when concrete shared logging/metrics/tracing responsibility exists.

Delete legacy top-level `bootstrap/` and `runtime/` after imports and tests are migrated.

Exit gate: process shell contains no feature ownership; bootstrap depends outward on concrete context/workflow adapters and no core code imports platform.

### M5 — Capability-oriented internals

Refine only contexts/workflows whose application layer has multiple independent change axes.

Preferred shape:

```text
application/
  <capability>/
    commands.py / queries.py / handlers.py / dto.py as justified
  ports/
```

Use change locality/cohesion as the split criterion. Do not create empty symmetric folders or split solely by file size.

Primary candidate: Application Communication Catalogue. Re-evaluate others from actual coupling after M2-M4; do not pre-invent slices.

Exit gate: architecture/locality tests protect any newly explicit capability boundary.

### M6 — Web final locality

Converge Web UI to:

```text
web/src/
  app/
  features/<feature>/
    api/
    model/
    components/
    pages/
  components/ui/
  lib/
```

Move root application bootstrap/routing from the current large application surface into `app/`. Keep feature DTO/request mapping feature-local. Shared transport/auth/session mechanics remain shared only when genuinely cross-feature.

Exit gate: `make web-check` and affected browser journeys pass; root API/application files no longer own feature behavior.

### M7 — Compatibility purge and final enforcement

Remove:
- old import shims;
- old top-level semantic/workflow/platform package paths;
- obsolete structural documentation;
- transitional architecture-test allowlists.

Strengthen executable rules so new code cannot reintroduce:
- semantic modules directly under `napms/`;
- generic `composition/`;
- feature code in `platform`;
- cross-context domain imports;
- context persistence bypass from workflows.

Final backend top-level package must contain only the target architectural categories plus package metadata.

Exit gate: full repository checks and required hosted PR gates pass; canonical docs describe actual code, not future state.

## Integration policy

- One coherent stage or context migration per PR; squash merge.
- Keep each PR behavior-preserving unless a separately accepted product/domain change is explicitly bundled.
- Never leave `main` in a half-moved state that requires a future PR to import/run.
- Prefer mechanical move/import changes before local refactoring inside the same slice; keep semantic redesign out of this roadmap.
- If a move reveals an ownership conflict, stop that slice and resolve the canonical domain/architecture owner before continuing.

## Done definition

The migration is complete when:

```text
backend/src/napms/
  contexts/
  workflows/
  platform/
```

is the actual backend package taxonomy; each context is locally Clean-Architecture-shaped; generic `composition`, top-level `runtime/bootstrap`, direct context-domain coupling and obsolete compatibility paths are absent; Web and repository root match the target structure; architecture tests enforce the result.
