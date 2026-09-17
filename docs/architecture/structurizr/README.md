# NAPMS architecture workspace

`workspace.dsl` is the canonical machine-readable S3 structural architecture model for the accepted first-MVP architecture. It materializes the accepted H18 architecture; it does not replace S1 requirements, S2 domain semantics, S3 persistence/contracts, or S4 implementation-readiness design.

Structurizr is also the common viewer for generated projections of other canonical design artifacts. Those projections are non-canonical and are rebuilt from their owning machine-readable sources.

The workspace currently provides native C4 views:

- `SystemContext` — NAPMS and its user;
- `Containers` — browser application, modular-monolith backend, and PostgreSQL;
- `BackendComponents` — domain-aligned backend modules plus policy-export composition;
- `MVPDeployment` — deployment mapping of the browser frontend, backend runtime, and PostgreSQL runtime for the accepted MVP baseline.

It also provides generated review projections:

| View | Canonical source | What it shows |
|---|---|---|
| `MVPJourney` | accepted H17 S1 product requirement | ordered first-MVP user/product journey |
| `DomainContextMap` | accepted H16 capability map + context relationships | peer Bounded Contexts and accepted peer relationships |
| `StrategicCollaborationMap` | accepted H16 capability map + context relationships | peer Bounded Contexts, non-peer compositions, and all accepted strategic collaborations |
| `ResourceCurationProcess` | accepted H12 S2 process model | declared Resource Catalogue policies, commands, domain events, sequences, and alternatives |
| `ResourceCatalogueDomainModel` | accepted H12 S2 tactical domain model | Resource aggregate root, owned entities, value objects, exact declared references, and invariants |
| `MVPTacticalDomainModel` | accepted H17 S2 tactical model | aggregate/entity semantics participating in the first MVP journey, grouped by owning context |
| `PersistenceOwnership` | accepted H19 S4 implementation-readiness design | PostgreSQL schema/table ownership only; deliberately not an ERD |

The two strategic S2 views deliberately answer different questions. `DomainContextMap` is not allowed to promote compositions to Bounded Contexts. `StrategicCollaborationMap` shows those compositions because they are useful to understand whole-domain collaboration, but it is not labeled as a DDD Context Map.

Generated diagrams never infer missing design decisions. For example, the Resource Catalogue domain-model projection creates ownership links only from explicit aggregate/entity references and links value objects only where the canonical model names them exactly as an identity or attribute. The persistence projection deliberately stops at schema/table ownership because no accepted column/key/cardinality-level persistence model exists yet.

The deployment view deliberately stays at the accepted S3 baseline. It does not invent cloud provider, operating system, cluster, reverse proxy, load balancer, redundancy, or other infrastructure decisions that have not been made yet. The generic deployment nodes express runtime placement only; they are not claims about separate physical machines.

## Canonical source vs projection

The projection layer is deliberately small and deterministic:

```text
accepted machine-readable design anchors
              |
              v
 tools/generate_architecture_views.py
              |
              v
 docs-generated/architecture/*.puml
              |
              v
         Structurizr
```

Current inputs are the accepted H12 Resource Catalogue process/domain anchors, H16 strategic anchors, H17 first-MVP requirement/tactical anchors, and the H19 implementation-readiness persistence-ownership section. The generated PlantUML files live under the ignored `docs-generated/` root and must not be edited or searched as canonical knowledge.

The generator is intentionally not a general diagram framework. Each renderer has a known canonical source shape, validates the source `status`/`type_id`, and fails on structural inconsistencies rather than guessing missing semantics.

## Refresh generated views

Run:

```sh
make architecture-sync
```

This regenerates all currently supported non-canonical architecture/design views from their canonical machine-readable sources.

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

GitHub Actions runs the same check when the Structurizr workspace, projection generator, any current canonical projection source, Makefile, or architecture workflow changes.

## ERD boundary

`PersistenceOwnership` is intentionally not an ERD. H19 currently owns only the accepted implementation-readiness facts that the MVP uses one PostgreSQL database and which tables belong to each module/schema. That is enough for a useful ownership projection but not enough to draw columns, primary/foreign keys, indexes, or cardinalities honestly.

When an accepted machine-readable S3 persistence model contains those decisions, the same projection mechanism should generate one or more ERD PlantUML views from it. The generated ERD will remain a projection; the structured persistence model will own the design truth.

## Authority boundary

The Structurizr DSL may express C4 structural elements, deployment/runtime containers, deployment nodes, components, and their architectural relationships. Domain invariants and bounded-context semantics remain owned by accepted S2 artifacts. Generated image views expose accepted S1/S2/S4 artifacts for human inspection without acquiring semantic authority. A future persistence/ERD projection must follow the same rule.
