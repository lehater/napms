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
- `harness-core.yaml` — NAPMS-owned ownership/capability/consumer-contract projection over the canonical graph.

## Documentation vertical

The first-MVP Harness pilot uses `harness-core.yaml` to make responsibility boundaries explicit without turning them into workflow state.

It defines:

- exactly one Authority for every current canonical-graph node;
- three explicit boundary checks for every Authority: semantic cohesion, independent change and stable public contract/Question routing;
- recursive decomposition of broad candidates until those checks pass;
- which capabilities each artifact provides;
- what each downstream responsibility requires;
- explicit `NOT_APPLICABLE` evidence for conditional needs;
- Questions as upstream semantic blockers;
- public-output closure: every capability in `provides` is either consumed downstream or explicitly declared as a terminal result with a reason.

A binding may have an empty `provides` list when the artifact is canonical and owned but its semantics are internal to the Authority's public contract. Do not expose language/process/decision fragments as public capabilities unless another Authority actually consumes them.

Run:

```sh
python tools/check_harness_vertical.py
python tools/test_harness_vertical.py
```

or `make design-check`.

A downstream gap is not repaired by editing another Authority's artifact. It becomes a Question for the semantic owner. An unresolved Question blocks affected downstream contracts through canonical dependency closure.

The repository has no runtime dependency on the separate `lehater/harness` project. This is an NAPMS-owned local application of the same ideas.

## Generated views

`docs-generated/` is disposable and non-canonical. Context maps, domain/process diagrams, journey views and ERD are generated from the owners above.

Use `make design-check` to validate current canonical truth and `make design-sync` to regenerate projections.

To inspect downstream impact: `python tools/check_canonical_graph.py --affected AP-DOMAIN`.

## Historical material

- `migration/revalidated/` — frozen evidence from the earlier anchor-shaped migration, not normal current-truth navigation.
- `horizontal/`, `review/`, `pilot/` — retained redesign/migration/pilot evidence where still useful.
- `docs-legacy/` — retired pre-cutover evidence only.

Historical material cannot override the current canonical owners.
