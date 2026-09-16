# Catalogue curation M7 pilot — S4 readiness

Status: CANDIDATE / non-canonical / documentation-migration readiness classified; materialization not yet executed.

## Pilot execution boundary

This M7 pilot is documentation-system design work only. Product source code is evidence, not an output.

Until a later, explicit implementation authorization changes this boundary:

- do not write, edit, refactor or generate product code;
- do not change tests to make the pilot pass;
- do not change runtime configuration, migrations, workflows or CI as part of this pilot;
- inspect implementation and tests only to corroborate already accepted documentation truth or to discover documentation gaps;
- if documentation cannot be completed without a product/code decision, record the gap or blocker instead of implementing a solution.

The pilot may create or edit only `docs-v2/**` candidate/design artifacts on its branch. Canonical `docs/**` remain unchanged until an explicit documentation cutover step.

## Capsule result

Scope: `catalogue-curation-pilot`  
Stage: `S4`  
Task: define the bounded documentation-materialization plan, migration ledger and validation intent for the selected documentation slice.

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
| RC catalogue HTTP surface | `http-contract` | `docs-v2/pilot/materialized/contracts/http/resource-catalogue.openapi.yaml` | S3 HTTP classification plus verified executable API evidence |

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
| `docs/engineering/catalogue-curation-http-api-contract.md` | RC OpenAPI candidate | TRANSFORM | selected RC operations/schemas/errors represented in machine-readable contract without inventing product behavior |

Legacy/current files remain untouched during pilot materialization. The ledger demonstrates disposition; deletion/move from canonical `docs/` is a later cutover action only.

## Executable API evidence inspected

The repository uses FastAPI as the executable API-schema source. `create_http_api()` constructs the `FastAPI` application, and `build_http_process()` includes the Resource Catalogue curation, workspace and temporal routers. Their Pydantic request models and route declarations therefore contribute to the generated OpenAPI schema.

The bounded inspection covered:

- `backend/src/napms/platform/http/api.py` — FastAPI application and shared public error/session boundary;
- `backend/src/napms/platform/bootstrap/http_process.py` — composition of RC routers into the runtime API;
- `backend/src/napms/contexts/resource_catalogue/presentation/http/curation.py` — Resource creation, realization creation, scope-affiliation and responsibility routes/models;
- `backend/src/napms/contexts/resource_catalogue/presentation/http/temporal.py` — realization replacement and relation-ending routes/models;
- `backend/src/napms/contexts/resource_catalogue/presentation/http/workspace.py` — Resource workspace/detail read routes/models;
- existing RC HTTP tests for corroborating request trust, idempotency, authority, temporal and concurrency behavior.

This evidence is sufficient to establish a trustworthy source for the candidate OpenAPI materialization. It does not authorize modifying those files, and implementation behavior must not be promoted into new S1/S2 truth merely because it exists in code.

## Materialization sequence

1. Materialize S1 candidate Markdown from the already classified records; do not reopen source interpretation during this step.
2. Materialize the S2 model as PlantUML plus the small context glossary/README and machine-readable traceability YAML.
3. Materialize S3 PlantUML container/flow artifacts.
4. Materialize the bounded RC OpenAPI candidate from accepted S3 contract truth, reconciling operation/schema details against FastAPI-generated executable schema evidence. When executable behavior conflicts with accepted upstream documentation, record drift; do not change code in this pilot.
5. Run applicable documentation/pilot validation and record exact results.
6. Compare candidate truth against the migration ledger for omission, duplicate ownership and cross-layer directionality.
7. Stop and report pilot findings. Do not migrate canonical `docs/` or change product code, tests, runtime configuration, migrations, workflow routing or CI.

## Validation intent

Apply the v2 validation layers/profiles to the materialized candidate:

- V0 structure: only allowed candidate artifact types/paths; one semantic owner per migrated claim;
- V1 syntax: Markdown structure, PlantUML parse where tooling is available, YAML parse, OpenAPI parse/validation when materialized;
- V2 consistency: stable requirement IDs unique; trace targets exist; no S1 bounded-context ownership; no duplicate RC realization truth; contract references accepted S1/S2 semantics rather than redefining them;
- V3 pilot gate evidence: record S1/S2/S3 classification PASS and S4 readiness result separately from canonical product gates;
- V4 realization: compare selected HTTP operations against FastAPI executable schema and existing tests as corroborating evidence, never as upstream product/domain truth and never by changing code/tests.

Repository/Harness validation remains required after candidate files exist. A hosted green run is evidence only for the exact head checked.

## Remaining design debt

The repository-layout specification exposes a system-level issue relevant to later cutover: `constraint` is semantically S0-owned while its current target physical path is `docs/requirements/constraints.md`. The selected catalogue-curation pilot has not identified a new S0 constraint, so this inconsistency does not block this bounded slice; it remains a layout issue rather than something to resolve opportunistically inside the pilot.

## G4/readiness result

Result: `PASS` for documentation-only pilot materialization readiness.

The previous HTTP-schema precondition is resolved: FastAPI router/model composition is the repository-native executable schema source for this bounded RC surface. This result authorizes only creation/validation of the listed non-canonical `docs-v2/**` pilot artifacts. It is not a product G4 result and grants no product implementation lease.

## Next task

Materialize the listed candidate documentation artifacts under `docs-v2/pilot/materialized/**`, beginning with the already classified S1 records. Product code and tests are read-only evidence throughout this pilot.