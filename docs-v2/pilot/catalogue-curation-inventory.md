# M7 pilot — catalogue curation inventory

Status: SELECTED / inventory in progress / non-canonical candidate work only.

## Pilot scope

Use the Resource Catalogue curation happy path as the first Documentation System v2 pilot: an operator creates and maintains catalogue resources through the existing HTTP surface, with accepted catalogue behavior, Resource Catalogue domain semantics, architecture boundary/contract documentation and executable implementation evidence already present.

This pilot migrates documentation knowledge only. It does not authorize product implementation and it does not change `docs/` canonical ownership.

## Why this slice

The slice satisfies the M7 selection criteria without using the policy-lifecycle area that is under separate active review:

- existing observable requirements and acceptance examples;
- a bounded Resource Catalogue domain model;
- an explicit catalogue-curation architecture boundary and HTTP contract;
- implemented FastAPI endpoints and executable evidence;
- meaningful S1 -> S2 -> S3 traceability while remaining small enough for one pilot;
- no need to invent new product behavior.

## Initial source inventory

| Legacy/current source | Candidate v2 type | Disposition | Pilot use |
|---|---|---|---|
| `docs/requirements/catalogue-curation.md` | `functional-requirement`, possibly `quality-requirement` | SPLIT | extract observable catalogue-curation behavior by capability; preserve stable semantic ids where present |
| `docs/requirements/catalogue-curation-acceptance-examples.md` | `acceptance-scenario` | MOVE/TRANSFORM | retain examples that prove accepted behavior; use Gherkin only where executable precision adds value |
| `docs/requirements/catalogue-curation-security.md` | `quality-requirement` and/or functional security requirements | SPLIT | classify each claim by observable behavior vs measurable quality expectation |
| `docs/domain/resource-catalogue/tactical-model.md` | `domain-model`, `domain-glossary` | TRANSFORM/SPLIT | convert formalizable semantics to the pilot domain model; keep only notation-insufficient narrative |
| `docs/domain/resource-catalogue/target-realization-model.md` | S2/S3 evidence requiring classification | SPLIT/REFERENCE | do not preserve a mixed realization document as a new canonical owner |
| `docs/architecture/catalogue-curation-boundary.md` | `container-view` and/or `interaction-flow`/architecture narrative | TRANSFORM/SPLIT | retain only architecture truth required to realize the accepted slice |
| `docs/engineering/catalogue-curation-http-api-contract.md` | `http-contract` | TRANSFORM | migrate catalogue HTTP boundary to first-class OpenAPI source or reference an already canonical native OpenAPI source if one exists |
| `backend/src/napms/contexts/resource_catalogue/presentation/http/curation.py` | executable realization evidence | REFERENCE | corroborate S3 contract and V4 realization; never infer missing S1/S2 truth from code |
| `backend/src/napms/contexts/resource_catalogue/presentation/http/workspace.py` | executable realization evidence | REFERENCE | use only if the selected happy path depends on workspace reads |
| relevant Resource Catalogue tests | `automated-test` evidence | REFERENCE | identify exact tests before candidate gate evaluation |

## Explicit exclusions

The first pilot does not migrate the whole Resource Catalogue, UI wireframes, application catalogue legacy compatibility, access-policy lifecycle, deployment behavior, or unrelated shared HTTP conventions. Shared sources are referenced only when the selected curation path demonstrates a direct dependency.

## Ownership guardrail discovered before execution

The current v2 specifications still contain an unresolved constraint-ownership inconsistency: the catalog/lifecycle text assigns externally imposed constraints to S0, while the target repository layout and project rule place canonical requirement constraints in S1. The pilot must not encode candidate constraint artifacts until this is corrected consistently in M1/M2/M6. Problem conditions/evidence remain S0; canonical requirement constraints belong to S1 by default, with S0 reopened only when the underlying problem truth itself changes.

This is a specification defect, not a reason to infer or duplicate constraint truth in the pilot.

## First task capsule

```yaml
scope: catalogue-curation-pilot
stage: S1
state: IN_PROGRESS
task: classify current catalogue-curation requirement sources into v2 S1 artifact records without changing canonical docs
primary_instruction: requirements-stage
artifact_types:
  - functional-requirement
  - quality-requirement
  - acceptance-scenario
inputs:
  - docs/requirements/catalogue-curation.md
  - docs/requirements/catalogue-curation-acceptance-examples.md
  - docs/requirements/catalogue-curation-security.md
outputs:
  - docs-v2/pilot/catalogue-curation/s1-inventory.md
validation_profile:
  - gate-g1
implementation_authorization: none
authorized_scope: none
authorization_basis: none
context_refs:
  - docs-v2/spec/lifecycle.md
  - docs-v2/spec/artifacts.md
  - docs-v2/spec/agent-execution.md
  - docs/requirements/catalogue-curation.md
  - docs/requirements/catalogue-curation-acceptance-examples.md
  - docs/requirements/catalogue-curation-security.md
context_expansions: []
blockers:
  - constraint ownership specification must be corrected before any constraint record is classified
next: classify S2 Resource Catalogue sources after S1 candidate inventory passes its applicable checks
```

## Pilot evidence to record

For every executed capsule record the direct context refs, any context expansion and its reason, output artifact types, exact validation commands/profile, ownership/applicability ambiguity, and whether the next task was handed off without being silently executed.

## Exit for selection/inventory step

This step is complete when the bounded slice, initial source dispositions, exclusions, first task capsule and known specification blocker are explicit. No candidate semantic migration is accepted until the constraint-ownership blocker is fixed.