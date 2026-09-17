# Validation specification

Status: M5 REVISED — strategic S2 derivation/distillation/context-relationship checks added after horizontal-pilot review.

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
8. Strategic S2 validation checks derivation of boundaries, not only internal consistency of the final BC list.

## Validation layers

| Layer | Purpose | Typical checks |
|---|---|---|
| V0 Structure | repository/artifact shape | path pattern, filename, required metadata/id, unique canonical owner |
| V1 Syntax | native source validity | PlantUML parse, YAML/JSON parse, OpenAPI/AsyncAPI/schema validation, Gherkin parse |
| V2 Consistency | relationships between canonical sources | resolvable refs, traceability targets, ownership consistency, duplicate canonical truth, contract/reference agreement, capability-to-context coverage |
| V3 Gate evidence | lifecycle sufficiency for selected scope | applicable mandatory/conditional artifacts present/current, blockers absent, required evidence refs valid |
| V4 Realization | implementation agrees with accepted design/contracts | contract tests, migrations, architecture/dependency tests, domain/unit tests |
| V5 Journey | observable integrated behavior | acceptance/integration/E2E journey evidence |

Layers are ordered by cost, not by lifecycle stage. A task runs only the subset its validation profile requires.

## Validation profiles

| Profile | Minimum intent |
|---|---|
| `artifact-edit` | V0 + V1 for changed canonical artifacts; directly affected V2 refs |
| `gate-g0` | applicable S0 V0-V2 + G0 evidence sufficiency |
| `gate-g1` | applicable S1 V0-V2 + G1 evidence sufficiency |
| `gate-g2` | applicable S2 V0-V2 + capability/boundary derivation + requirement/domain trace + relationship classification/distillation where applicable + G2 sufficiency |
| `gate-g3` | applicable architecture/contracts V0-V2 + G3 sufficiency |
| `gate-g4` | current upstream gate/evidence refs + implementation plan/test intent/migration applicability + G4 authorization checks |
| `implementation-slice` | changed source V4 checks plus contract/schema/migration checks selected by affected artifact types |
| `journey-validation` | applicable V4 prerequisites + selected V5 journey/E2E evidence |
| `repository-integration` | repository-wide deterministic invariants and configured CI integration suite |

Profiles prevent agents from loading/running every validation rule for every task.

## Artifact-rule families

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

### Strategic DDD artifacts

For a scope that discovers or materially revalidates multiple capabilities/Bounded Contexts:

- every material capability has a strategic disposition: accepted/candidate BC cluster, owner-preserving composition, integration/application capability, external responsibility or explicitly unresolved;
- capability grouping records enough semantic rationale to challenge whether capabilities belong together or apart;
- no BC is accepted solely because a legacy directory/service/module already has that name;
- each accepted BC has a coherent model/language/responsibility boundary rather than being only a technical component;
- where strategic importance differs materially, applicable domain distillation is explicit (for example Core / Supporting / Generic) or the artifact records why classification is not useful;
- every material BC-to-BC relationship records directionality where meaningful and an applicable DDD Context Mapping pattern, or explicitly records that no stronger pattern is yet justified;
- Shared Kernel is explicit only when shared model ownership/change coordination is deliberately accepted; common IDs/schemas alone do not imply it;
- the visual context map agrees with the canonical capability/relationship mappings;
- compositions and integration capabilities are not silently promoted to peer BCs.

### Traceability

- source and target identifiers resolve;
- relation type is allowed;
- no requirement is forced to belong to exactly one bounded context;
- capability-to-context mappings cover strategic boundary decisions when `capability-map` applies;
- generated indexes are reproducible from canonical mapping.

### Plans/capsules

- current stage/scope/task are explicit;
- exactly one primary instruction is selected;
- declared inputs/outputs resolve or are valid planned outputs;
- G4 authorization exists before implementation execution;
- stale authorization is rejected when an upstream dependency is dirty.

## G2 semantic sufficiency questions

After mechanical V0-V2 checks, G2 evaluation for strategic discovery/revalidation asks:

1. Are material capabilities identified from accepted behavior/domain language rather than inherited from implementation structure?
2. Does the capability map explain grouping/splitting and the disposition of capabilities that are not peer Bounded Contexts?
3. Are Bounded Context boundaries coherent in responsibility, model and Ubiquitous Language?
4. Has strategic distillation been performed where prioritization/differentiation is material, or explicitly judged non-applicable?
5. Are inter-context relationships classified strongly enough to preserve model integrity and autonomy, including upstream/downstream semantics where applicable?
6. Are requirements traceable to one or more domain responsibilities without physically re-owning S1 requirements?
7. Are unresolved strategic questions absent or explicitly blocking rather than hidden by tactical/architectural assumptions?

A G2 PASS cannot be based only on the existence of `context-map.puml` and context-local domain models when the scope required strategic boundary discovery.

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
- missing applicable strategic derivation evidence during S2 -> S2 `REWORK`, unless the gap is actually missing S0/S1 truth;
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

Deterministic validation should eventually detect generated drift, references to retired/generated sources as canonical inputs, duplicate stable canonical ids, registry/layout disagreement and executable evidence referencing missing/retired requirements/contracts. Strategic semantic review remains targeted rather than a broad LLM scan on every change.

## Changed-path selection

CI/Harness should map changed paths/artifact ids to validation profiles. Examples:

```text
docs/domain/capability-map.md
  -> artifact-edit + strategic capability coverage rules

docs/domain/context-relationships.yaml
  -> artifact-edit + relationship schema/reference rules
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

The repository already has CI as an integration capability. Under v2, agent routing metadata must surface relevant existing checks and their trigger scope. Do not create a parallel CI stack solely for docs-v2 if existing workflows can host the rules cleanly.

## Machine-readable validation registry

Target shape after the pilot stabilizes fields:

```yaml
profiles:
  gate-g2:
    rules:
      - artifact.path
      - plantuml.syntax
      - capability.coverage
      - context.relationships
      - traceability.resolve
      - gate.g2.applicability
```

The registry defines routing and rule identity; executable commands remain repository tooling/configuration.

## M5 revision note

The horizontal pilot demonstrated that final-state consistency is insufficient evidence for strategic boundary quality. G2 now requires applicable capability clustering/derivation, domain distillation and Context Mapping relationship evidence before strategic discovery can be accepted.
