# NAPMS C4 architecture workspace

`workspace.dsl` is the canonical machine-readable S3 structural architecture model for the accepted first-MVP architecture. It materializes the accepted H18 architecture; it does not replace S1 requirements, S2 domain semantics, OpenAPI contracts, or S4 persistence/implementation design.

The workspace currently provides three generated views:

- `SystemContext` — NAPMS and its user;
- `Containers` — browser application, modular-monolith backend, and PostgreSQL;
- `BackendComponents` — domain-aligned backend modules plus policy-export composition.

## Local viewing and editing

Run:

```sh
make architecture
```

Then open `http://localhost:8080`. The command uses the official Structurizr image pinned to the non-hardened `2026.06.28-noble` variant. This avoids host bind-mount write failures caused by the hardened image's container user while still allowing Structurizr Local to persist diagram layout next to `workspace.dsl`.

Edit `workspace.dsl` in the repository and refresh the browser to see changes. The DSL is the source of truth. Generated/rendered diagrams are projections and should not be edited as independent architecture truth.

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

## Authority boundary

The workspace may express C4 structural elements, deployment/runtime containers, components, and their architectural relationships. Domain invariants and bounded-context semantics remain owned by accepted S2 artifacts. Persistence/ERD concerns remain outside this workspace until explicitly designed at S4.
