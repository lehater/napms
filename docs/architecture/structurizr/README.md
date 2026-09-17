# NAPMS C4 architecture workspace

`workspace.dsl` is the canonical machine-readable S3 structural architecture model for the accepted first-MVP architecture. It materializes the accepted H18 architecture; it does not replace S1 requirements, S2 domain semantics, OpenAPI contracts, or S4 persistence/implementation design.

The workspace currently provides four generated views:

- `SystemContext` — NAPMS and its user;
- `Containers` — browser application, modular-monolith backend, and PostgreSQL;
- `BackendComponents` — domain-aligned backend modules plus policy-export composition;
- `MVPDeployment` — deployment mapping of the browser frontend, backend runtime, and PostgreSQL runtime for the accepted MVP baseline.

The deployment view deliberately stays at the accepted S3 baseline. It does not invent cloud provider, operating system, cluster, reverse proxy, load balancer, redundancy, or other infrastructure decisions that have not been made yet. The generic deployment nodes express runtime placement only; they are not claims about separate physical machines.

## Local viewing and editing

Run:

```sh
make architecture
```

Then open `http://localhost:8080`. The command uses the official Structurizr image pinned to the non-hardened `2026.06.28-noble` variant. This avoids host bind-mount write failures caused by the hardened image's container user while still allowing Structurizr Local to persist diagram layout next to `workspace.dsl`.

Edit `workspace.dsl` in the repository and refresh the browser to see structural changes. The C4 views intentionally use manual layout rather than `autoLayout`, so their elements can be moved in the Structurizr diagram editor.

Use the pencil/editor action in Structurizr to position elements and relationships. Saving the workspace creates or updates `workspace.json` next to `workspace.dsl`. The two files have different roles:

- `workspace.dsl` is the canonical S3 structural architecture truth;
- `workspace.json` is the compiled workspace plus manual presentation/layout data and may be committed so that a reviewed layout is shared by the team.

Do not hand-edit coordinates in `workspace.json`. Keep the explicit stable view keys (`SystemContext`, `Containers`, `BackendComponents`, `MVPDeployment`), because Structurizr uses them when retaining manual layout across DSL changes.

The workspace uses the conventional C4 visual hierarchy: darker software-system elements, lighter containers, lighter components, a person shape for people, a cylinder for the PostgreSQL container, and neutral deployment-node boundaries. Styling is presentation only; tags and model structure remain the semantic source.

The image can be overridden when deliberately testing a newer Structurizr release:

```sh
make architecture STRUCTURIZR_IMAGE=structurizr/structurizr:<version>-noble
```

## Validation

Run:

```sh
make architecture-check
```

This validates the DSL with the same pinned Structurizr image. Validation mounts the architecture directory read-only because it must not mutate canonical documentation.

GitHub Actions runs the same `make architecture-check` for pull requests and `main` changes affecting the Structurizr workspace, Makefile, or the architecture workflow. This makes parser/runtime compatibility part of CI rather than relying on a developer discovering it manually.

## Code/class diagrams

Structurizr remains the native source for C4 System Context, Container, Component, and Deployment views. Lower-level code/class diagrams are optional supporting projections and should not be modeled as additional C4 components merely to obtain UML notation.

When a class diagram becomes useful, keep its source as PlantUML under `docs/architecture/code/` and expose it from the Structurizr workspace through an `image` view. This provides one architecture viewer without making PlantUML a competing source for C4 structure. No class diagrams are created yet; they should be added only where they answer a concrete implementation/design question.

## Authority boundary

The workspace may express C4 structural elements, deployment/runtime containers, deployment nodes, components, and their architectural relationships. Domain invariants and bounded-context semantics remain owned by accepted S2 artifacts. Persistence/ERD concerns remain outside this workspace until explicitly designed at S4.
