# Canonical artifact model

Status: CURRENT.

NAPMS keeps the smallest durable artifact set that gives each material kind of knowledge one semantic owner. Artifact types are not mandatory lifecycle paperwork. S0-S4 remain useful maturity vocabulary, but do not determine physical paths or require gate transactions.

| Family | Typical source | What it owns |
|---|---|---|
| discovery | YAML/Markdown/evidence reference | problem/evidence that materially constrains design |
| strategic domain model | YAML | capabilities, Bounded Contexts, relationships, non-peer composition classification |
| context domain model | YAML | context-owned aggregates/entities/value objects/invariants/public semantics |
| domain process | YAML | commands/events/policies/flows when material |
| cross-context use case | YAML | ordered application/journey semantics spanning owners |
| structural architecture | Structurizr DSL | system/container/component/deployment structure |
| architecture rules | YAML | non-C4 technical constraints |
| HTTP contract | OpenAPI | HTTP operations, schemas, outcomes and security representation |
| physical persistence | YAML | schemas/tables/columns/keys/relations/indexes/checks |
| implementation readiness | YAML/Markdown | implementation sequence/readiness, never authorization |
| test intent | YAML/Markdown | verification obligations |
| decision record | ADR when needed | durable rationale not adequately carried by an owner |

Rules: one semantic fact has one owner; prefer standard machine-readable notation when it naturally expresses the concern; do not add a second DSL only to draw a diagram; product code/tests do not backfill missing design truth; generated files under `docs-generated/**` are never canonical; historical fingerprints/gates/receipts are not semantic fields unless independently meaningful.

Create an artifact only when its knowledge exists. No process model without material process semantics; no AsyncAPI without async boundary; no ERD before physical persistence; no context-local copy of a cross-context use case; no per-BC topology when Structurizr already owns system topology.
