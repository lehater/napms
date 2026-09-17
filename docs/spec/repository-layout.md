# Repository layout specification

Status: M3 REVISED — canonical layout includes strategic DDD discovery/distillation artifacts.

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
│   ├── capability-map.md
│   ├── distillation.md
│   ├── context-relationships.yaml
│   ├── glossary.md
│   ├── traceability/
│   └── <bounded-context>/
│       ├── README.md
│       ├── domain-model.puml
│       └── state-machines/
├── architecture/
│   ├── README.md
│   ├── structurizr/
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
| `capability-map` | `docs/domain/capability-map.md` or machine-readable equivalent when the mapping is generated/viewed in several forms |
| `domain-distillation` | `docs/domain/distillation.md` |
| `context-map` | generated projection under `docs-generated/`; never a canonical source path |
| `context-relationship-map` | `docs/domain/context-relationships.yaml` or the accepted machine-readable S2 anchor selected by migration/cutover; generated context/collaboration views project this truth rather than duplicating it |
| `domain-model` | `docs/domain/<bounded-context>/domain-model.puml` when PlantUML itself is the canonical semantic source; use a generated projection when a machine-readable semantic owner exists |
| `domain-glossary` | `docs/domain/glossary.md` for shared domain language; context-local terms may live in `docs/domain/<bounded-context>/README.md` |
| `state-model` | `docs/domain/<bounded-context>/state-machines/<subject>.puml` unless generated from a stronger machine-readable owner |
| `requirement-domain-trace` | `docs/domain/traceability/<stable-name>.<machine-readable-ext>`; human indexes should be generated where practical |
| `system-context` | `docs/architecture/structurizr/workspace.dsl` when Structurizr is the selected canonical S3 structural model |
| `container-view` | `docs/architecture/structurizr/workspace.dsl` when Structurizr is the selected canonical S3 structural model |
| `interaction-flow` | `docs/architecture/flows/<flow>.puml` |
| `deployment-model` | `docs/architecture/structurizr/workspace.dsl` when represented by the canonical deployment model there; actual IaC remains with deployable source and is referenced |
| `persistence-model` | `docs/architecture/persistence/<bounded-context-or-store>.<machine-readable-ext>` by default; generated ERD is a projection; colocate under implementation only when executable schema tooling is the canonical model |
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

## Strategic domain locality

Cross-context strategic discovery lives directly under `docs/domain/` because it precedes and explains context-local tactical ownership:

```text
docs/domain/
  capability-map.md
  distillation.md              # only when applicable
  context-relationships.yaml   # only when multiple BC relationships require classification
```

The capability map records capability clustering and disposition into candidate/accepted Bounded Context, composition, integration capability or unresolved strategic ownership. Distillation records strategic importance without changing semantic ownership. Context relationships record DDD relationship semantics. Visual Context Maps and broader collaboration maps are generated projections under `docs-generated/` and may be surfaced through Structurizr; they do not become canonical by being easier to inspect.

## Bounded-context locality

A bounded context owns its semantic model locally:

```text
docs/domain/<bounded-context>/
  README.md
  domain-model.puml
  state-machines/       # only if needed
```

The context README is intentionally small: responsibility, boundary summary, public semantic guarantees and links. It must not duplicate the domain model in prose.

Persistence does not automatically live under the context directory because it is a technical realization, not the domain model. The default persistence owner is architecture; an implementation-native schema may supersede a documentation persistence model when it can serve as the authoritative model. ERDs derived from another canonical persistence source remain generated projections.

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

Use lower-case kebab-case for semantic path segments and filenames except established tool conventions. Stable identifiers inside artifacts are preferred for traceability; filenames should remain readable and may change only when concept ownership genuinely changes.

## Indexes and navigation

Each major area may have one small `README.md` that answers only what the area owns, how artifacts are grouped, where canonical sources are found, and links to the small number of cross-cutting entry points. Do not create hand-maintained catalog pages that repeat titles/statuses already derivable from machine-readable metadata.

## Generated output

Canonical source stays in the paths above. Generated renderings/reports must either be CI artifacts outside Git or live under a clearly non-canonical generated root when a repository consumer requires them. The generated root is `docs-generated/`; it must never be searched as canonical knowledge by agents.

## Source-code locality exceptions

Executable truth remains with source code when moving it into `docs/` would make it less authoritative. Examples include database migrations, tests and infrastructure-as-code. Documentation references those paths rather than cloning their content.

## `docs-v2` design-period rule

Before cutover:

```text
docs/      = canonical current product/process knowledge
docs-v2/   = non-canonical design specification for the replacement system
```

Pilot/migration candidate artifacts may live under `docs-v2/**` only under the migration/pilot rules; they do not become canonical merely by existing there.

## Cutover rule

M6 must define the exact operation, but the intended terminal state is:

```text
current docs/       -> temporary docs-old/ safety copy if needed
validated docs-v2/  -> docs/
```

`docs-old/` is temporary and excluded from agent canonical search. After cutover verification it is removed; Git history is the long-term archive.

## M3 revision note

The strategic-pilot audit added physical ownership for `capability-map`, `domain-distillation` and `context-relationship-map`. The current projection rule keeps those semantic owners durable while allowing Context Maps and wider collaboration views to be regenerated for review instead of hand-maintained as competing truth.
