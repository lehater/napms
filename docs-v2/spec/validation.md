# Validation specification

Status: M5 COMPLETE — validation layers, profiles and failure routing defined; validator implementation remains post-spec/pilot work.

## Purpose

Validate canonical artifacts and lifecycle transitions with the cheapest deterministic checks first. Use agent/human semantic judgment only where the rule cannot be expressed reliably as a mechanical check.

## Principles

1. Fail fast on cheap structural/syntax defects before semantic evaluation.
2. Validate only artifacts and rules applicable to the current task/change scope.
3. Prefer deterministic tools over agent judgment for syntax, schema, references, path rules and generated drift.
4. A gate consumes validation evidence; it does not rerun unrelated repository checks by definition.
5. Local checks optimize feedback speed; CI provides authoritative integration evidence where configured.
6. Validation failures route to the stage/artifact owner of the defect, not necessarily the stage where the failure was observed.
7. Generated projections never validate independently of their canonical sources.

## Validation layers

| Layer | Purpose | Typical checks |
|---|---|---|
| V0 Structure | repository/artifact shape | path pattern, filename, required metadata/id, unique canonical owner |
| V1 Syntax | native source validity | PlantUML parse, YAML/JSON parse, OpenAPI/AsyncAPI/schema validation, Gherkin parse |
| V2 Consistency | relationships between canonical sources | resolvable refs, traceability targets, ownership consistency, duplicate canonical truth, contract/reference agreement |
| V3 Gate evidence | lifecycle sufficiency for selected scope | applicable mandatory/conditional artifacts present/current, blockers absent, required evidence refs valid |
| V4 Realization | implementation agrees with accepted design/contracts | contract tests, migrations, architecture/dependency tests, domain/unit tests |
| V5 Journey | observable integrated behavior | acceptance/integration/E2E journey evidence |

Layers are ordered by cost, not by lifecycle stage. A task runs only the subset its validation profile requires.

## Validation profiles

The future machine-readable registry should expose named profiles composed from rule ids. Initial semantic profiles are:

| Profile | Minimum intent |
|---|---|
| `artifact-edit` | V0 + V1 for changed canonical artifacts; directly affected V2 refs |
| `gate-g0` | applicable S0 V0-V2 + G0 evidence sufficiency |
| `gate-g1` | applicable S1 V0-V2 + G1 evidence sufficiency |
| `gate-g2` | applicable S2 V0-V2 + requirement/domain trace where applicable + G2 sufficiency |
| `gate-g3` | applicable architecture/contracts V0-V2 + G3 sufficiency |
| `gate-g4` | current upstream gate/evidence refs + implementation plan/test intent/migration applicability + G4 authorization checks |
| `implementation-slice` | changed source V4 checks plus contract/schema/migration checks selected by affected artifact types |
| `journey-validation` | applicable V4 prerequisites + selected V5 journey/E2E evidence |
| `repository-integration` | repository-wide deterministic invariants and configured CI integration suite |

Profiles prevent agents from loading/running every validation rule for every task.

## Artifact-rule families

M5 defines rule families; concrete commands/tooling may be added later.

### Markdown/narrative artifacts

- required stable metadata/identifier where the artifact class needs it;
- no lifecycle state encoded only in filename;
- referenced canonical ids/paths resolve;
- no obvious duplicate canonical owner for the same stable id.

### PlantUML/C4 artifacts

- source parses;
- referenced/includes resolve without reaching retired/generated canonical sources;
- filename/path matches artifact type ownership;
- rendered output, when produced, is derived from current source.

### OpenAPI/AsyncAPI/JSON Schema

- native document/schema validates;
- stable contract identifiers/version metadata satisfy repository convention;
- referenced schemas resolve;
- breaking-change/compatibility checks run when an established contract changes and tooling supports them.

### Gherkin/executable scenarios

- source parses;
- scenario identifiers/requirement references resolve where required;
- executable scenarios are discoverable by the configured test runner when they are canonical executable evidence.

### Traceability

- source and target identifiers resolve;
- relation type is allowed;
- no requirement is forced to belong to exactly one bounded context;
- generated indexes are reproducible from canonical mapping.

### Plans/capsules

- current stage/scope/task are explicit;
- exactly one primary instruction is selected;
- declared inputs/outputs resolve or are valid planned outputs;
- G4 authorization exists before implementation execution;
- stale authorization is rejected when an upstream dependency is dirty.

## Execution locations

| Location | Responsibility |
|---|---|
| Agent/local | narrowest fast checks for the current task before persisting/handing off |
| Harness | select profile, verify capsule/lifecycle applicability, enforce authorization/reopen rules, expose relevant repository commands |
| CI | authoritative deterministic integration checks, repository-wide invariants and expensive suites appropriate to changed paths |
| Gate evaluation | consume current validation results plus semantic evidence and decide PASS/REWORK/REOPEN/BLOCKED |

Harness must know which CI profiles/checks exist so an agent does not rediscover automation or falsely treat unrun checks as absent.

## Severity and routing

Validation findings use:

```text
P0 BLOCKER  — unsafe/invalid canonical state or implementation authorization; stop
P1 REQUIRED — gate/task cannot pass until corrected
P2 FOLLOWUP — valid current scope but material improvement/debt should be tracked
P3 INFO     — non-blocking observation
```

Routing rules:

- syntax/path/schema failure -> artifact owner/current task (`REWORK` when same stage);
- missing required earlier-stage truth -> `REOPEN(Sx)`;
- stale/dirty upstream dependency -> revoke dependent G4 authorization and route to owning stage;
- implementation contradicts accepted domain/requirement truth -> determine whether implementation is wrong or upstream truth is incomplete; route to the actual owner rather than editing both opportunistically;
- generated drift -> regenerate/fix generator; never edit projection as canonical truth.

P0/P1 findings block the relevant gate/task. P2/P3 do not silently expand the current capsule.

## Gate evidence contract

A gate evaluation receives a compact evidence set:

```yaml
scope: <semantic scope>
gate: G2
artifact_refs:
  - <applicable canonical refs>
validation_results:
  - profile: gate-g2
    status: pass|fail
    findings: []
blockers: []
semantic_questions: []
```

Mechanical PASS is necessary where configured but is not sufficient for semantic gate acceptance. The gate evaluator answers only the stage-specific sufficiency questions after deterministic failures are cleared.

## Drift and duplicate truth

Deterministic validation should eventually detect:

- generated output older/different than canonical source when committed projections are permitted;
- references to `docs-old/`, `docs-generated/` or retired artifacts as canonical inputs;
- two artifacts claiming the same stable canonical id;
- machine-readable registry paths that disagree with repository-layout rules;
- executable contract/test evidence referencing missing or retired requirements/contracts.

Do not attempt semantic duplicate detection with broad LLM scans on every change. Use stable ids/metadata first; semantic review is targeted when evidence indicates ambiguity.

## Changed-path selection

CI/Harness should map changed paths/artifact ids to validation profiles. Examples:

```text
docs/domain/**.puml
  -> artifact-edit + domain structural rules

docs/contracts/http/**.yaml
  -> artifact-edit + OpenAPI validation + compatibility when applicable

docs/decisions/**.md
  -> ADR structure/reference checks
backend/** + affected contract/domain refs
  -> implementation-slice
```

Exact path filters/commands are implementation details and should be derived from the finalized machine-readable catalog rather than duplicated across multiple workflows.

## CI integration rule

The repository already has CI as an integration capability. Under v2, agent routing metadata must surface relevant existing checks and their trigger scope. M6/M7 will map current workflows to the new profiles before any cutover. Do not create a parallel CI stack solely for docs-v2 if existing workflows can host the rules cleanly.

## Machine-readable validation registry

Target shape after the pilot stabilizes fields:

```yaml
profiles:
  gate-g2:
    rules:
      - artifact.path
      - plantuml.syntax
      - traceability.resolve
      - gate.g2.applicability

rules:
  plantuml.syntax:
    layer: V1
    severity: P1
    executor: <tool/command binding>
```

The registry defines routing and rule identity; executable commands remain repository tooling/configuration. Avoid embedding large shell implementations into metadata.

## M5 exit

M5 is complete when validation layers/profiles, artifact rule families, local/Harness/CI/gate responsibilities, severity, failure routing, drift handling and the target registry contract are explicit without implementing the complete validator suite or migrating product documentation.
