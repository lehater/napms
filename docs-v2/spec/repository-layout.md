# Repository layout specification

Status: M3 COMPLETE — canonical layout and locality rules defined; migration remains M6-owned.

## Purpose

Define physical ownership for canonical documentation artifacts so a human or agent can derive likely paths from artifact type and concept ownership without loading the repository broadly.

## Layout principles

1. Storage follows knowledge/concept ownership, not lifecycle gate numbers.
2. A canonical artifact has one physical owner. Indexes and projections reference it; they do not copy its truth.
3. S1 requirements do not depend on bounded contexts. Context-specific placement begins only for S2 domain knowledge.
4. Keep formal source close to the concept it describes.
5. Cross-cutting contracts and decisions have explicit global owners rather than being hidden in an arbitrary context.
6. Do not pre-create empty optional directory trees.
7. Generated output is not mixed with canonical source.
8. Names are stable semantic names; lifecycle status such as `g1`, `accepted`, `new` or `final` is not encoded in filenames.

## Cutover target tree

```text
docs/
├── README.md
├── problem/
│   ├── README.md
│   ├── evidence/
│   └── journeys/
├── requirements/
│   ├── README.md
│   ├── functional/
│   ├── quality/
│   ├── constraints.md
│   └── glossary.md
├── domain/
│   ├── README.md
│   ├── context-map.puml
│   ├── glossary.md
│   ├── traceability/
│   └── <bounded-context>/
│       ├── README.md
│       ├── domain-model.puml
│       └── state-machines/
├── architecture/
│   ├── README.md
│   ├── system-context.puml
│   ├── containers.puml
│   ├── flows/
│   ├── deployment/
│   └── persistence/
├── contracts/
│   ├── README.md
│   ├── http/
│   ├── events/
│   └── schemas/
├── decisions/
├── plans/
└── process/
```

Only paths required by actual artifacts exist. The tree above is a routing model, not a requirement to create every directory.

## Path rules by artifact type

| Artifact type | Canonical path pattern |
|---|---|
| `problem-statement` | `docs/problem/README.md` for the current product-level problem frame, or `docs/problem/<scope>.md` when independently owned problem scopes exist |
| `evidence` | `docs/problem/evidence/<stable-name>.md` or a durable external/native reference from that index |
| `user-journey` | `docs/problem/journeys/<journey>.md` unless executable acceptance ownership makes the executable scenario canonical elsewhere |
| `functional-requirement` | `docs/requirements/functional/<capability-or-behavior>.md` |
| `quality-requirement` | `docs/requirements/quality/<quality-attribute>.md` |
| `constraint` | `docs/requirements/constraints.md` unless a constraint has enough independent lifecycle to justify `constraints/<name>.md` |
| `acceptance-scenario` | near the requirement when Markdown; executable `.feature` in the repository test/spec location selected by implementation conventions, referenced from the requirement |
| `requirements-glossary` | `docs/requirements/glossary.md` |
| `context-map` | `docs/domain/context-map.puml` |
| `domain-model` | `docs/domain/<bounded-context>/domain-model.puml` |
| `domain-glossary` | `docs/domain/glossary.md` for shared domain language; context-local terms may live in `docs/domain/<bounded-context>/README.md` |
| `state-model` | `docs/domain/<bounded-context>/state-machines/<subject>.puml` |
| `requirement-domain-trace` | `docs/domain/traceability/<stable-name>.<machine-readable-ext>`; human indexes should be generated where practical |
| `system-context` | `docs/architecture/system-context.puml` |
| `container-view` | `docs/architecture/containers.puml` |
| `interaction-flow` | `docs/architecture/flows/<flow>.puml` |
| `deployment-model` | `docs/architecture/deployment/<scope>.puml` when documentation source is canonical; actual IaC remains with deployable source and is referenced |
| `persistence-model` | `docs/architecture/persistence/<bounded-context-or-store>.puml` by default; colocate under implementation only when executable schema tooling is the canonical model |
| `http-contract` | `docs/contracts/http/<api>.openapi.yaml` |
| `event-contract` | `docs/contracts/events/<channel-or-api>.asyncapi.yaml` |
| `data-schema` | `docs/contracts/schemas/<schema>.schema.json` or contract-native equivalent |
| `decision-record` | `docs/decisions/NNNN-<decision>.md` |
| `implementation-plan` | `docs/plans/active/<plan>.md`, then current durable truth is folded into owning artifacts and the plan is retired per plan lifecycle |
| `migration` | implementation-native migration directory; referenced by S4 plan/evidence rather than copied into docs |
| `test-intent` | S4 plan or test specification close to executable tests, referenced from the plan |
| `automated-test` | implementation/test tree, not `docs/` |
| `journey-e2e-test` | E2E/test tree, not `docs/` |

M4/M5 may refine routing metadata, but must not silently change these ownership rules.

## Requirements grouping

`docs/requirements/functional/` is grouped by stable product capability or observable behavior, never by a bounded context merely because one is currently known. For example:

```text
requirements/functional/application-management.md
requirements/functional/connectivity-management.md
```

is valid even if S2 later maps those behaviors across several bounded contexts. Context-centric requirement views are generated projections from traceability.

## Bounded-context locality

A bounded context owns its semantic model locally:

```text
docs/domain/<bounded-context>/
  README.md
  domain-model.puml
  state-machines/       # only if needed
```

The context README is intentionally small: responsibility, boundary summary, public semantic guarantees and links. It must not duplicate the domain model in prose.

Persistence does not automatically live under the context directory because it is a technical realization, not the domain model. The default persistence owner is architecture; an implementation-native schema may supersede a documentation ERD when it can serve as the authoritative model.

## Contracts

Contracts are first-class cross-boundary artifacts under `docs/contracts/`, not attachments to architecture prose and not owned by whichever bounded context happens to call another one. The contract filename represents the governed interface/API/event surface.

A context README or architecture flow references the contract. It does not copy operations or schemas into prose.

## Decisions

Significant decisions use repository-global sequential ADRs:

```text
docs/decisions/0001-<semantic-name>.md
```

An ADR references affected canonical artifacts. It does not own the resulting domain model, requirement, API contract or architecture view.

## Naming

Use lower-case kebab-case for semantic path segments and filenames except established tool conventions.

Prefer:

```text
access-governance/domain-model.puml
connectivity-management.md
request-policy-access.puml
```

Avoid:

```text
access-governance-g2.md
requirements-final-v3.md
new-domain-model.puml
architecture-approved.md
```

Stable identifiers inside artifacts are preferred for traceability; filenames should remain readable and may change only when concept ownership genuinely changes.

## Indexes and navigation

Each major area may have one small `README.md` that answers only:

- what this area owns;
- how artifacts are grouped;
- where canonical sources are found;
- links to the small number of cross-cutting entry points.

Do not create hand-maintained catalog pages that repeat titles/statuses already derivable from machine-readable metadata. Prefer generated indexes once M5 tooling exists.

## Generated output

Canonical source stays in the paths above. Generated renderings/reports must either:

1. be CI artifacts and remain outside Git; or
2. live under a clearly non-canonical generated root when a repository consumer requires committed output.

A future generated root, if required, is:

```text
docs-generated/
```

It must never be searched as canonical knowledge by agents. Generated files identify their source and generation mechanism. Default policy: do not commit reproducible renderings.

## Source-code locality exceptions

Executable truth remains with source code when moving it into `docs/` would make it less authoritative. Examples include database migrations, tests and infrastructure-as-code. Documentation references those paths rather than cloning their content.

This preserves the principle "artifact over prose" without forcing every artifact into the documentation directory.

## `docs-v2` design-period rule

Before cutover:

```text
docs/      = canonical current product/process knowledge
docs-v2/   = non-canonical design specification for the replacement system
```

Do not place migrated product artifacts in `docs-v2` until M6 defines migration batches and M7 selects a pilot. This prevents dual truth during design.

## Cutover rule

M6 must define the exact operation, but the intended terminal state is:

```text
current docs/       -> temporary docs-old/ safety copy if needed
validated docs-v2/  -> docs/
```

`docs-old/` is temporary and excluded from agent canonical search. After cutover verification it is removed; Git history is the long-term archive.

## M3 exit

M3 is complete when canonical physical ownership, path patterns, naming, locality, contract/ADR placement, generated-output policy and the target cutover tree are explicit without migrating current product documentation.
