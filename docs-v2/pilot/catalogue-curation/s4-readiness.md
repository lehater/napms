# Catalogue curation M7 pilot — S4 readiness

Status: CANDIDATE / non-canonical / documentation-migration readiness classified; materialization not yet executed.

## Capsule result

Scope: `catalogue-curation-pilot`  
Stage: `S4`  
Task: define the bounded implementation plan, migration ledger and validation intent for materializing the selected documentation slice into candidate v2 artifacts.

Direct context used:

- `docs-v2/spec/repository-layout.md`
- `docs-v2/spec/validation.md`
- `docs-v2/migration/plan.md`
- `docs-v2/pilot/catalogue-curation/s1-inventory.md`
- `docs-v2/pilot/catalogue-curation/s2-inventory.md`
- `docs-v2/pilot/catalogue-curation/s3-inventory.md`

Context expansions: none.

## Planned candidate artifact set

These paths are pilot candidate materializations under `docs-v2/pilot/materialized/`; they deliberately mirror the cutover routing model without claiming canonical `docs/` ownership before cutover.

| Candidate artifact | Type | Pilot path | Source classification |
|---|---|---|---|
| catalogue curation observable behavior | `functional-requirement` | `docs-v2/pilot/materialized/requirements/functional/catalogue-curation.md` | S1 functional records |
| catalogue curation quality expectations | `quality-requirement` | `docs-v2/pilot/materialized/requirements/quality/catalogue-curation.md` | S1 quality records |
| catalogue curation acceptance intent | `acceptance-scenario` | `docs-v2/pilot/materialized/requirements/functional/catalogue-curation-acceptance.md` | S1 acceptance records |
| Resource Catalogue semantic model | `domain-model` | `docs-v2/pilot/materialized/domain/resource-catalogue/domain-model.puml` | S2 merged domain model |
| Resource Catalogue terminology | `domain-glossary` | `docs-v2/pilot/materialized/domain/resource-catalogue/README.md` | S2 glossary subset |
| catalogue requirement/domain trace | `requirement-domain-trace` | `docs-v2/pilot/materialized/domain/traceability/catalogue-curation.yaml` | S2 trace table |
| RC catalogue structural boundary | `container-view` | `docs-v2/pilot/materialized/architecture/containers.puml` | S3 container classification |
| RC catalogue mutation/read flows | `interaction-flow` | `docs-v2/pilot/materialized/architecture/flows/resource-catalogue-curation.puml` | S3 interaction flows |
| RC catalogue HTTP surface | `http-contract` | `docs-v2/pilot/materialized/contracts/http/resource-catalogue.openapi.yaml` | S3 HTTP classification plus verified native schema source |

No empty optional directories are to be created.

## Migration ledger

| Current source | Candidate target(s) | Disposition | Completion condition |
|---|---|---|---|
| `docs/requirements/catalogue-curation.md` | functional + quality candidate artifacts; S2/S3 statements excluded | SPLIT | every selected RC claim mapped once or explicitly routed/excluded |
| `docs/requirements/catalogue-curation-acceptance-examples.md` | acceptance candidate | TRANSFORM | selected A/F/G/I/J semantics preserved; ACC-only examples remain excluded |
| `docs/requirements/catalogue-curation-security.md` | functional + quality candidate artifacts | SPLIT | observable RC authorization behavior preserved without duplicating AM domain truth |
| `docs/domain/resource-catalogue/tactical-model.md` | domain model + glossary + trace | TRANSFORM/MERGE | RC identities/facts/invariants represented once |
| `docs/domain/resource-catalogue/target-realization-model.md` | domain model + glossary + trace | MERGE | overlapping realization semantics have one candidate owner |
| `docs/architecture/catalogue-curation-boundary.md` | container + interaction-flow candidates | SPLIT | RC architecture retained; ACC/migration/implementation statements routed out |
| `docs/engineering/catalogue-curation-http-api-contract.md` | RC OpenAPI candidate | TRANSFORM | selected RC operations/schemas/errors represented in machine-readable contract and checked against native executable schema |

Legacy/current files remain untouched during pilot materialization. The ledger demonstrates disposition; deletion/move from canonical `docs/` is a later cutover action only.

## Materialization sequence

1. Materialize S1 candidate Markdown from the already classified records; do not reopen source interpretation during this step.
2. Materialize the S2 model as PlantUML plus the small context glossary/README and machine-readable traceability YAML.
3. Materialize S3 PlantUML container/flow artifacts.
4. Before creating OpenAPI, locate and inspect the repository's native/executable API schema for the selected RC endpoints. Reconcile prose classification with that source; do not infer request/response schemas from prose alone.
5. Materialize the bounded RC OpenAPI candidate or record a BLOCKED disposition if no trustworthy schema source exists and required schemas cannot be established from accepted S3 truth.
6. Run applicable pilot validation and record exact results.
7. Compare candidate truth against the migration ledger for omission, duplicate ownership and cross-layer directionality.
8. Stop and report pilot findings. Do not migrate canonical `docs/`, product code, workflow routing or CI in this capsule.

## Validation intent

Apply the v2 validation layers/profiles to the materialized candidate:

- V0 structure: only allowed candidate artifact types/paths; one semantic owner per migrated claim;
- V1 syntax: Markdown structure, PlantUML parse where tooling is available, YAML parse, OpenAPI parse/validation when materialized;
- V2 consistency: stable requirement IDs unique; trace targets exist; no S1 bounded-context ownership; no duplicate RC realization truth; contract references accepted S1/S2 semantics rather than redefining them;
- V3 pilot gate evidence: record S1/S2/S3 classification PASS and S4 readiness result separately from canonical product gates;
- V4 realization: for the HTTP contract only, compare selected operations against repository-native/executable schema and existing implementation/tests as corroborating evidence, never as upstream product/domain truth.

Repository/Harness validation remains required after candidate files exist. A hosted green run is evidence only for the exact head checked.

## Blockers and preconditions

One precondition remains before full materialization can be declared ready: the native/executable API schema source for `/api/v1/catalogues/**` has not yet been inspected in this S4 capsule. This does not block materializing S1/S2/architecture candidates, but it blocks claiming the OpenAPI candidate complete.

The repository-layout specification also exposes a design debt relevant to later cutover: `constraint` is semantically S0-owned while its current target physical path is `docs/requirements/constraints.md`. The selected catalogue-curation pilot has not identified a new S0 constraint, so this inconsistency does not block this bounded slice; it remains a system-level layout issue rather than something to resolve opportunistically inside the pilot.

## G4/readiness result

Result: `REWORK` for full documentation-migration materialization readiness until the RC native/executable HTTP schema source is inspected and the OpenAPI materialization strategy is confirmed.

This is not a product G4 result and grants no product implementation lease. It is a pilot finding demonstrating that the execution model stops at a concrete missing input rather than filling contract schemas from downstream guesses.

## Next task

Inspect the smallest repository-native/executable API schema source that covers the selected Resource Catalogue endpoints and determine whether it is sufficient to materialize `resource-catalogue.openapi.yaml`. No other artifact materialization is authorized by this handoff.