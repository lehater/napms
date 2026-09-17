# Canonical model migration strategy

Status: active migration workstream.

This workstream restructures the current NAPMS design truth from migration/stage-shaped accepted anchors into a smaller graph of semantic models, architecture models, contracts, and generated review projections.

The completed H0-H20 Documentation System / Harness program remains historical context. This is a new workstream; it does not invent H21.

## Why this migration exists

The current `docs/migration/revalidated/**` anchors successfully established accepted S1-S4 truth, but the working representation mixes two concerns:

- semantic/project-design truth;
- lifecycle, migration, provenance, fingerprint, validation and stage bookkeeping.

That shape is useful as migration evidence, but it is too heavy as the permanent working model.

The target is to make each important kind of knowledge have one obvious semantic owner and to generate human review views from those owners.

## Target model

```text
Discovery / evidence
        |
        v
Strategic domain model
        |
        v
Bounded-context semantic models
        |
        +-------------> system architecture / contracts / persistence
        |                         |
        v                         v
generated DDD views       generated C4/API/ERD views
        \_______________________/
                    |
                    v
            common review surface

implementation later realizes the accepted models and is checked for conformance
```

Target repository shape, refined only when a real slice requires it:

```text
docs/
├── discovery/
├── model/
│   ├── strategic/
│   ├── contexts/
│   └── use-cases/
├── architecture/
│   ├── structurizr/
│   └── persistence/
├── contracts/
└── decisions/

docs-generated/
└── architecture/
```

The physical layout is subordinate to semantic ownership. Do not create empty directories or mandatory per-context files merely to satisfy this sketch.

## Adopted decisions

1. `docs/` remains the sole project/design authority namespace.
2. The migration is not a big-bang rewrite and is not a full layer-by-layer copy.
3. A small strategic spine is migrated early; tactical/domain truth then moves by vertical semantic-ownership slices, normally one Bounded Context at a time.
4. A slice is migrated by semantic equivalence first, then explicit cutover. It is never kept indefinitely as two editable sources of truth.
5. During this workstream, `migration-ledger.yaml` resolves authority per slice:
   - `authority: legacy` means the listed accepted anchor(s) remain current truth;
   - `authority: target` means the new target path(s) are current truth and the old anchors are migration evidence for that slice.
6. Generated PlantUML/SVG/other diagrams are disposable projections and never semantic authority.
7. Structurizr DSL remains the canonical S3 structural/C4 model. It is not generated from domain YAML.
8. OpenAPI remains the canonical HTTP application contract.
9. AsyncAPI is introduced only if a real asynchronous integration boundary exists.
10. A physical persistence model becomes a separate canonical architecture model; ERD is generated from it. Domain entities are not automatically database tables.
11. Context Mapper/CML is not a required Harness dependency. The pilot showed good coverage of standard DDD structure but incomplete coverage of NAPMS invariants, policies and non-peer compositions.
12. Small deterministic repository-local generators are preferred over a general diagram framework.
13. Import Linter or equivalent implementation conformance checks are considered only when product implementation is separately authorized.
14. arc42, if used, is a human-readable composition/narrative surface, not an additional truth store.
15. Product code/tests are not sources for reconstructing domain or architecture truth during this migration.

## Migration unit

The normal migration unit is a semantic ownership slice, not a stage directory.

For a Bounded Context this usually means:

```text
strategic placement/relationships
        ↓
context purpose/language/boundary
        ↓
tactical domain model
        ↓
process model when materially needed
        ↓
links to separately owned S3/contracts/persistence
        ↓
generated review projections
```

Cross-context journeys/use cases and system-level S3 artifacts are migrated as their own units because they do not belong to one BC.

## Cutover protocol

For each unit in `migration-ledger.yaml`:

1. Read only its listed accepted source anchors plus directly required dependencies.
2. Create the smallest target semantic artifact set that preserves accepted meaning.
3. Do not carry stage/gate/migration bookkeeping into the semantic payload unless it is independently meaningful.
4. Validate semantic equivalence and explicit omissions/deferrals.
5. Regenerate affected projections.
6. Confirm dependency references and downstream impact.
7. Change the ledger unit to `authority: target` only after the equivalence/cutover check passes.
8. From that point, edits go only to the target model; legacy anchors for that unit are evidence, not an editable mirror.
9. Never reverse-sync target changes into the retired source representation.

If the target representation cannot preserve an accepted semantic fact without awkward duplication, stop the cutover and record the gap rather than weakening the model.

## Migration order

The workstream deliberately combines an early horizontal spine with vertical slices:

```text
CM0  repository control records
CM1  strategic spine
CM2  Resource Catalogue
CM3  remaining MVP/domain BC slices
CM4  cross-context journeys and non-peer compositions
CM5  S3 / contracts / persistence normalization
CM6  Harness simplification and active-path retirement
CM7  closeout
```

Within CM3 the default order is Authority Management, Application Communication Catalogue, Application Deployment, Business Connectivity, Access Policy. Change the order only when dependency evidence makes another order simpler.

## What must not happen

- no second permanent Harness;
- no new universal DSL;
- no mandatory CML/Context Mapper layer;
- no generated diagram becoming authority;
- no per-BC microservice assumption;
- no schema/ERD inferred from DDD entities;
- no bulk copying of all old anchors into a new tree before their slice is ready;
- no mass rewrite of accepted semantics merely to fit the new layout;
- no product implementation or product-test changes without separate authorization;
- no merge without explicit authorization.

## Evidence from experiments

The migration strategy incorporates two non-authoritative experiments:

- `architecture/model-layout-pilot`, especially commit `13a39b7b80b7beaec65bef98ea415ae908fc3bcf`, demonstrated a smaller Resource Catalogue semantic layout and the Context Mapper comparison.
- `architecture/generated-projections`, PR #134, demonstrated deterministic canonical-artifact → PlantUML → Structurizr projections.

These experiments are evidence only. Accepted `docs/**` anchors remain the source for migration semantics until each ledger unit cuts over.

## Completion condition

The workstream is complete when:

- current design truth is navigable through stable semantic/architecture/contract paths rather than migration phase directories;
- every migrated fact has one current owner;
- diagrams are generated from their canonical models;
- accepted S1-S4 semantics are preserved or explicitly changed through a separate design decision;
- the old migration-shaped anchors are no longer part of normal current-truth navigation;
- Harness/runtime validation is reduced to repository-state discovery, dependency/impact validation, specialized checks and projection orchestration;
- work can resume from the repository without chat history.
