# Canonical repository layout

Status: CURRENT.

Storage follows semantic ownership. Lifecycle stages and historical migration phases are not directory structure.

```text
docs/
├── README.md
├── canonical-graph.yaml
├── harness-engineering-graph.yaml    # project producer/consumer policy for pinned Harness
├── harness-projection.yaml           # thin artifact/Authority/capability mapping
├── discovery/
├── model/
│   ├── strategic/
│   ├── contexts/
│   └── use-cases/
├── architecture/
│   ├── structurizr/
│   └── persistence/
├── contracts/
│   └── http/
├── plans/
├── decisions/                 # only when a durable ADR is needed
├── spec/
├── meta/
└── migration/                # historical migration evidence, not normal authority

docs-generated/                # disposable non-canonical projections
```

## Ownership

| Knowledge | Canonical owner |
|---|---|
| capability/BC/relationship semantics | `docs/model/strategic/*.yaml` |
| context tactical semantics | `docs/model/contexts/<context>/*.yaml` |
| cross-context use case/journey | `docs/model/use-cases/*.yaml` |
| structural C4/deployment architecture | `docs/architecture/structurizr/workspace.dsl` |
| non-C4 system rules | `docs/architecture/*.yaml` |
| physical persistence | `docs/architecture/persistence/*.yaml` |
| HTTP contract | `docs/contracts/http/*.openapi.yaml` |
| implementation readiness/test intent | `docs/plans/*.yaml` |
| durable design decision | `docs/decisions/*` when needed |
| dependency/routing metadata | `docs/canonical-graph.yaml` |
| engineering producer/consumer policy | `docs/harness-engineering-graph.yaml` |
| canonical-artifact Harness projection | `docs/harness-projection.yaml` |
| rendered diagrams | `docs-generated/**`, never authority |

A file is created only when its knowledge has an independent owner. Small contexts do not need mandatory file templates.

## Projections and formats

Projection code is explicit and repository-local. It reads canonical owners and writes only under `docs-generated/`. A generator may format or select already-owned semantics; it may not infer missing semantics.

Structurizr owns C4 structure, OpenAPI owns HTTP representation, and the physical persistence YAML owns relational design. PlantUML is a generated view unless explicitly declared otherwise. AsyncAPI and Context Mapper/CML are not default dependencies.

Agents navigate through `docs/canonical-graph.yaml`, not `docs/migration/revalidated/**`. Active workstream state is reached through `docs/meta/current-workstream.yaml`.
