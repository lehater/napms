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

- `requirements/` — accepted product intent, behavior, scope boundaries and acceptance examples.
- `discovery/` — evidence/problem discovery that still matters to current design.
- `model/strategic/` — capability, Bounded Context and relationship ownership.
- `model/contexts/` — context-owned tactical semantics.
- `model/use-cases/` — cross-context/application flows derived from requirements and context-owned semantics.
- `architecture/structurizr/workspace.dsl` — canonical C4 structural/deployment model.
- `architecture/mvp-system-rules.yaml` — application/module coordination and integration-boundary rules.
- `architecture/mvp-security-architecture.yaml` — authentication/admission security architecture.
- `architecture/mvp-module-contracts.yaml` — in-process module/application contracts.
- `architecture/mvp-technical-representation.yaml` — shared technical representation conventions.
- `architecture/persistence/mvp-persistence.yaml` — canonical first-MVP physical persistence model.
- `architecture/mvp-quality-requirements.yaml` — architecture-significant first-MVP quality constraints.
- `architecture/mvp-threat-model.yaml` — first-MVP architecture threat model.
- `architecture/mvp-observability.yaml` — implementation-facing diagnostic requirements.
- `contracts/http/napms.openapi.yaml` — canonical first-MVP HTTP contract.
- `plans/` — implementation design/readiness and verification intent; these never authorize implementation by themselves.
- `canonical-graph.yaml` — routing/dependency metadata only; it does not duplicate semantic truth.
- `harness-engineering-graph.yaml` — NAPMS project Authority/Capability/Consumer topology.
- `harness-projection.yaml` — thin project mapping of canonical artifacts to Authorities/capabilities and Questions.
- `../.harness-version` — immutable canonical Harness runtime version used to interpret both.

## Engineering-knowledge vertical

NAPMS uses the pinned canonical Harness runtime to make engineering-decision boundaries explicit without turning them into workflow state. The project owns its graph/projection data; evaluator semantics live only in `lehater/harness`.

The model deliberately separates:

- **engineering Authority** — a kind of design knowledge/decision ownership;
- **canonical artifact** — where that knowledge is recorded;
- **projection artifact** — a generated view of canonical knowledge;
- **subject matter** — the contexts, aggregates, modules and interfaces described by those artifacts.

For example, Strategic Domain Design owns the strategic DDD artifacts. `CONTEXT-MAP` / `docs-generated/architecture/context-map.puml` is a projection artifact. Resource Catalogue, Access Policy and the other Bounded Contexts shown on it are subject matter, not separate Harness Authorities.

It defines:

- exactly one Authority for every current canonical-graph node;
- three explicit boundary checks for every Authority: semantic cohesion, independent change and stable public contract/Question routing;
- recursive decomposition of broad candidates until those checks pass;
- which capabilities each artifact provides;
- what each downstream responsibility requires;
- explicit `NOT_APPLICABLE` evidence for conditional needs;
- Questions as upstream semantic blockers;
- public-output closure: every capability in `provides` is either consumed downstream or explicitly declared as a terminal result with a reason;
- graph/contract closure: each non-root Authority's declared upstream owners exactly match the cross-Authority dependencies in the canonical graph.
- Authority-DAG closure: grouping canonical artifacts into engineering Authorities must not create an Authority dependency cycle.

A binding may have an empty `provides` list when the artifact is canonical and owned but its semantics are internal to the Authority's public contract. Do not expose language/process/decision fragments as public capabilities unless another Authority actually consumes them.

Run `make design-check` with the pinned Harness checked out at `.harness-tool` (CI does this automatically), or set `HARNESS_ROOT` to that exact pinned checkout.



To prepare the bounded input/output context for one engineering Authority:

```sh
make authority-context AUTHORITY=SYSTEM-ARCHITECTURE CAPABILITY=engineering.architecture.rules
```

This command does not create workflow state or a persistent task capsule. It deterministically resolves the Authority's declared input capabilities to canonical provider artifacts, adds only the provider's same-Authority dependency closure needed to understand that public capability, lists only the selected Authority's owned write paths/public outputs, and returns `BLOCKED` when a required input is missing or blocked. It never follows undeclared cross-Authority dependencies while building the execution context.

After artifact authoring, pass the changed canonical paths with `--check-write` to verify that the selected Authority did not modify another Authority's artifacts. A blocked Authority is forbidden from producing artifacts at all. `make design-check` remains the postcondition that validates the resulting canonical knowledge and downstream capability contracts.

A downstream gap is not repaired by editing another engineering Authority's artifact. It becomes a Question for the Authority that owns that kind of project decision. An unresolved Question blocks affected downstream contracts through canonical dependency closure.

The product has no runtime dependency on Harness. Engineering/design tooling has an explicit development-time dependency on the immutable Harness commit in `.harness-version`; NAPMS does not fork its evaluator.

## Generated views

`docs-generated/` is disposable and non-canonical. Context maps, domain/process diagrams, journey views and ERD are generated from the owners above.

Use `make design-check` to validate current canonical truth and `make design-sync` to regenerate projections.

To inspect downstream impact: `python tools/check_canonical_graph.py --affected AP-DOMAIN`.

## Historical material

- `migration/revalidated/` — frozen evidence from the earlier anchor-shaped migration, not normal current-truth navigation.
- `horizontal/`, `review/`, `pilot/` — retained redesign/migration/pilot evidence where still useful.
- `docs-legacy/` — retired pre-cutover evidence only.

Historical material cannot override the current canonical owners.
