# NAPMS architecture workspace

`workspace.dsl` is the canonical machine-readable S3 structural architecture model for the accepted first-MVP architecture. It materializes the accepted H18 architecture; it does not replace S1 requirements, S2 domain semantics, S3 persistence/contracts, or S4 implementation-readiness design.

Structurizr is also the common viewer for generated projections of other canonical design artifacts. Those projections are non-canonical and are rebuilt from their owning machine-readable sources.

The workspace currently provides:

- `SystemContext` — NAPMS and its user;
- `Containers` — browser application, modular-monolith backend, and PostgreSQL;
- `BackendComponents` — domain-aligned backend modules plus policy-export composition;
- `MVPDeployment` — deployment mapping of the browser frontend, backend runtime, and PostgreSQL runtime for the accepted MVP baseline;
- `DomainContextMap` — generated PlantUML projection of the accepted strategic S2 capability map and context relationships.

The deployment view deliberately stays at the accepted S3 baseline. It does not invent cloud provider, operating system, cluster, reverse proxy, load balancer, redundancy, or other infrastructure decisions that have not been made yet. The generic deployment nodes express runtime placement only; they are not claims about separate physical machines.

## Canonical source vs projection

The first projection pipeline is deliberately small:

```text
docs/migration/revalidated/h16-strategic/s2/strategic/capability-map.yaml
                                      +
docs/migration/revalidated/h16-strategic/s2/strategic/context-relationships.yaml
                                      |
                                      v
                    tools/generate_architecture_views.py
                                      |
                                      v
                 docs-generated/architecture/context-map.puml
                                      |
                                      v
                         Structurizr DomainContextMap
```

The two S2 YAML anchors are semantic authority. `context-map.puml` is generated output only. It is under the ignored `docs-generated/` root and must not be edited or searched as canonical knowledge.

The generator is intentionally not a general diagram framework. It performs a deterministic projection and fails if a relationship endpoint is not declared by the accepted capability map or if a configured source is not `ACCEPTED`.

## Refresh generated views

Run:

```sh
make architecture-sync
```

This regenerates all currently supported non-canonical architecture views from their canonical machine-readable sources. At present that is only the DDD Context Map.

`make architecture` invokes `architecture-sync` automatically, so normal viewing always starts from freshly generated projections.

## Local viewing and editing

Run:

```sh
make architecture
```

Then open `http://127.0.0.1:8080` or `http://localhost:8080`.

The command starts two disposable local containers:

- Structurizr Local bound to `127.0.0.1:8080` for C4 viewing/layout editing;
- PlantUML Server bound to `127.0.0.1:8081` for rendering generated `.puml` image views.

The PlantUML endpoint is intentionally browser-visible on loopback because Structurizr image views emit an SVG URL that the web browser loads directly. A Docker-only hostname such as `napms-plantuml` is therefore not sufficient for local browser rendering. Both services are bound to loopback only and are not exposed on external network interfaces.

No diagram source is sent to a public rendering service.

The Structurizr image is pinned to the non-hardened `2026.06.28-noble` variant. This allows Structurizr Local to persist C4 diagram layout next to `workspace.dsl`. The PlantUML renderer is presentation infrastructure only; semantic content remains in the canonical inputs.

Edit `workspace.dsl` and refresh the browser to see S3 structural changes. The native C4 views intentionally use manual layout rather than `autoLayout`, so their elements can be moved in the Structurizr diagram editor.

Use the pencil/editor action in Structurizr to position C4 elements and relationships. Saving the workspace creates or updates `workspace.json` next to `workspace.dsl`. The files have different roles:

- `workspace.dsl` is the canonical S3 structural architecture truth;
- `workspace.json` is the compiled workspace plus manual presentation/layout data and may be committed so that a reviewed C4 layout is shared by the team;
- `docs-generated/**` contains disposable projections from other canonical artifacts and is regenerated rather than hand-maintained.

Do not hand-edit coordinates in `workspace.json`. Keep the explicit stable C4 view keys (`SystemContext`, `Containers`, `BackendComponents`, `MVPDeployment`), because Structurizr uses them when retaining manual layout across DSL changes.

The workspace uses the conventional C4 visual hierarchy: darker software-system elements, lighter containers, lighter components, a person shape for people, a cylinder for the PostgreSQL container, and neutral deployment-node boundaries. Styling is presentation only; tags and model structure remain the semantic source.

The Structurizr image can be overridden when deliberately testing a newer release:

```sh
make architecture STRUCTURIZR_IMAGE=structurizr/structurizr:<version>-noble
```

## Validation

Run:

```sh
make architecture-check
```

The check first regenerates projections from canonical sources, then validates the Structurizr DSL with the pinned Structurizr image. A clean CI checkout therefore never depends on a committed generated diagram.

GitHub Actions runs the same check when the Structurizr workspace, projection generator, projection source anchors, Makefile, or architecture workflow changes.

## Future projections

The same pattern can be extended without changing authority rules:

- a canonical S3 persistence model can generate ERD PlantUML views;
- machine-readable tactical/domain artifacts can generate domain-model views where useful;
- code/class diagrams may use PlantUML when they have a defined canonical source.

ERD generation is intentionally not implemented yet because a canonical column/key/relationship-level persistence model has not been established. The generator must visualize decisions; it must not infer missing persistence decisions from domain semantics or product code.

## Authority boundary

The Structurizr DSL may express C4 structural elements, deployment/runtime containers, deployment nodes, components, and their architectural relationships. Domain invariants and bounded-context semantics remain owned by accepted S2 artifacts. Generated image views expose those artifacts for human inspection without acquiring semantic authority. Persistence/ERD concerns remain outside the generated projection set until explicitly designed as canonical S3 persistence truth.
