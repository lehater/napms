# Documentation System v2 migration plan

Status: M6 COMPLETE / no product migration authorized.

## Goal

Migrate current project knowledge and Harness/CI routing into Documentation System v2 without creating dual canonical truth, losing reconstructive knowledge or coupling the cutover to a big-bang rewrite.

## Invariants

- `docs/` remains canonical until explicit cutover;
- `docs-v2/` contains v2 specifications and bounded pilot material only before cutover;
- do not bulk-copy old documents into the new tree;
- migrate current truth artifact-by-artifact after target ownership/type is known;
- content is normalized into v2 artifact types rather than preserving legacy file boundaries;
- every migrated semantic claim has one canonical owner after cutover;
- missing upstream truth is recorded as a migration gap and is never reconstructed by inference from downstream domain, architecture, implementation or tests;
- executable implementation/tests may corroborate migrated truth but never become the source of product/problem, requirement or domain truth;
- Git history is the long-term archive; `docs-old/` is temporary cutover insurance only if used;
- candidate-mode Harness/validation support is enabled before candidate product artifacts depend on it; final canonical routing switches only at cutover;
- no production implementation is authorized by the documentation migration itself.

## Iterations

- [x] M0 — establish charter, principles and workstream skeleton.
- [x] M1 — complete lifecycle specification.
- [x] M2 — complete artifact catalog and applicability model.
- [x] M3 — complete repository layout/naming specification.
- [x] M4 — complete agent execution/progressive-disclosure specification.
- [x] M5 — complete validation/CI model.
- [x] M6 — map current docs/Harness/CI to v2 and define migration/cutover/rollback.
- [ ] M7 — run one bounded pilot and revise specifications from evidence.
- [ ] V2 readiness review.
- [ ] Controlled migration and cutover.
- [ ] Remove temporary legacy tree after verification.

## Current inventory classes

The current tree is migrated by semantic class, not file-for-file.

| Current owner | V2 disposition |
|---|---|
| `docs/requirements/**` | split/normalize into S1 functional, quality, acceptance and glossary artifacts; externally imposed/non-negotiable constraints route to S0; remove bounded-context/gate naming from canonical requirement ownership |
| `docs/domain/**` | normalize into context map, per-bounded-context domain models, state models, domain glossary and sparse requirement-domain traceability |
| `docs/architecture/**` | normalize into system/container/flow/deployment/persistence architecture sources; move interface contracts to `docs/contracts/**` when they are first-class contracts |
| `docs/engineering/**` | classify each item: first-class contract -> `docs/contracts/**`; architecture realization -> `docs/architecture/**`; implementation/runbook truth -> nearest source/operations owner; remove duplicated prose after canonical owner exists |
| `docs/ui/**` | preserve product/UI truth only where still required; map observable behavior back to S1 requirements and keep UI-specific design close to its actual UI owner rather than inventing a lifecycle stage |
| `docs/decisions/**` | retain only decisions needed to reproduce/evolve current truth; normalize ADR naming/references |
| `docs/process/**` | migrate process rules after M7 validates v2 lifecycle/execution semantics; do not mix product migration with process rewrite |
| `docs/plans/**` | preserve only current execution state; completed/superseded plans remain Git history |
| `.agents/**`, `AGENTS.md` | update routing/skill contracts to v2 only after pilot proves loading/routing model |
| `.github/workflows/**`, `Makefile`, `tools/**` | map existing checks to v2 validation profiles; extend existing workflows rather than create parallel CI where practical |

## Legacy-content classification

Every current document is assigned exactly one migration disposition:

```text
MOVE       — content already matches one v2 canonical owner; relocate/rename with minimal semantic change
SPLIT      — one legacy file contains several v2 artifact types/owners
MERGE      — duplicate legacy files contribute to one canonical v2 artifact
TRANSFORM  — semantics remain valid but representation changes, e.g. prose model -> PlantUML/OpenAPI
REFERENCE  — executable/native source outside docs is canonical; v2 docs only reference it
RETIRE     — historical/superseded-only content; preserve in Git history, not current tree
DEFER      — applicability/current truth is unresolved; blocks that migration batch, not unrelated batches
```

No file is copied merely to make the target tree look complete. `DEFER` is also the required disposition when an upstream semantic owner has no trustworthy current source; downstream artifacts are evidence of the gap, not authority to fill it.

## Migration batches

### B0 — Candidate validation and pilot infrastructure

Scope:

- enable only the deterministic v2 catalog/capsule/layout checks needed to validate non-canonical candidate material through the existing Harness/CI surface;
- keep current `docs/` routing and canonical knowledge checks authoritative;
- choose one bounded product slice with requirements + domain + architecture/contract + executable evidence;
- create only the target paths required by that slice under the pilot area;
- exercise task capsules, artifact applicability and validation profiles;
- record spec defects rather than working around them silently.

No canonical switch. Candidate-mode validation may recognize `docs-v2/**`; it must not make candidate product artifacts canonical or redirect production agents away from `docs/`.

### B1 — Product/problem and S1 requirements

- migrate S0 problem/evidence/constraint truth only from trustworthy current S0-equivalent sources or explicit stakeholder/evidence input;
- when trustworthy S0 truth is absent, record `DEFER`/gap rather than reconstructing it from requirements, domain models, architecture, implementation or tests;
- normalize functional requirements by observable behavior/capability, not bounded context;
- separate quality requirements, glossary and acceptance scenarios; route externally imposed/non-negotiable constraints to S0;
- establish stable ids needed for downstream traceability.

Exit: S0/S1 truth for the migrated scope is explicitly sourced and complete enough that S2 migration does not need to infer requirements or problem truth from downstream files. Missing upstream truth remains a visible blocker for that scope.

### B2 — Domain

- migrate context map and bounded-context ownership;
- create/normalize formal domain models and state models where applicable;
- establish sparse requirement-domain traceability;
- retire prose that only duplicates the formal model.

Exit: domain semantics can be reconstructed without consulting legacy domain files.

### B3 — Architecture and contracts

- normalize C4/interaction/deployment/persistence sources as applicable;
- extract HTTP/event/schema contracts into first-class native contract artifacts;
- retain ADR references to the new canonical owners;
- classify remaining engineering documentation.

Exit: architecture and cross-boundary contracts can be reconstructed without legacy architecture/engineering files.

### B4 — Final process, Harness and CI routing

- replace repository routing with v2 artifact/layout/validation metadata only after candidate batches have passed candidate-mode validation;
- update stage/task skills to load only applicable specs/artifacts;
- finalize mapping of `make harness-check`, `make knowledge-check`, `make check`, Web/E2E and other existing checks to v2 validation profiles;
- update hosted workflow path filters for the final target tree;
- add only missing deterministic validators demonstrated by the pilot/migration.

Exit: agents and CI resolve v2 canonical truth and no longer depend on legacy paths. B4 is the final routing switch, not the first point at which candidate artifacts receive validation.

### B5 — Cutover and cleanup

- run readiness review;
- freeze semantic migration during cutover window;
- verify target v2 tree and routing/CI on the cutover commit/PR;
- switch canonical root;
- remove temporary legacy tree after verification.

## Pilot selection criteria (M7)

Choose a slice that is:

- already implemented and has executable evidence, so migration can be checked against reality without designing new product behavior;
- non-trivial across at least S1, S2 and S3 boundaries;
- small enough to migrate in one bounded workstream;
- supported by existing tests/CI;
- representative of a cross-boundary contract or meaningful domain model;
- not currently under unrelated active product redesign.

Prefer a slice with one clear user journey and a small number of bounded contexts. Avoid the broadest or most contentious capability for the first pilot.

Executable evidence is corroborating/realization evidence only. If it conflicts with or exposes a gap in upstream truth, route the finding to the owning stage; do not reverse-engineer a new requirement/domain rule and silently declare it canonical.

## Pilot outputs

M7 creates only the artifacts needed for the selected slice and records:

```text
legacy -> v2 disposition mapping
actual task capsules used
context expansions required
validation profiles/checks executed
ambiguous ownership/applicability findings
spec changes required
migration effort/duplication discovered
```

A successful pilot may still change M1-M5 specifications; those changes are evidence-driven, not treated as failure.

## Harness migration map

Current repository routing already has task-first loading, scoped Skills, lifecycle protocols, active-plan semantics and explicit CI awareness. M4 should therefore be adopted by **refactoring existing routing**, not by introducing a second Harness.

Target changes after pilot:

```text
AGENTS routing
  current docs categories -> v2 artifact/catalog routing

stage/skill instructions
  broad document reads -> task capsule + applicable artifact types

Harness validators
  current structural checks -> V0/V2 capsule/catalog/layout checks

knowledge validators
  current domain invariants -> v2 artifact/profile checks
```

During M7 the existing Harness remains authoritative for repository execution; pilot-specific v2 instructions are explicitly scoped and cannot authorize product implementation.

## CI migration map

Current hosted workflows are retained and evolved.

- `harness.yml` remains the hosted Harness gate; candidate-mode v2 spec/registry/path triggers and checks may be added in B0 without changing canonical product routing.
- `knowledge.yml` remains the canonical knowledge validation surface until cutover; candidate knowledge validation may be added separately within the existing validation entry points, then its final target paths switch in B4/cutover.
- implementation/Web/Postgres/Docker/journey workflows remain implementation evidence and are mapped to V4/V5 profiles rather than duplicated.
- `Makefile` remains the local command entry point unless the pilot demonstrates a simpler replacement.

Before cutover, path filters must recognize the final `docs/` v2 layout including `docs/contracts/**`. Candidate checks must be active early enough to validate B1-B3 material before it can be accepted for cutover; do not globally redirect existing canonical checks to `docs-v2/`.

## Canonical-truth safeguard

Before cutover every migrated pilot/batch artifact carries explicit non-canonical pilot status. References from current canonical `docs/` must not depend on `docs-v2/`.

At cutover the switch is atomic from the repository consumer perspective:

```text
before: docs/ = canonical, docs-v2/ = non-canonical candidate
after:  docs/ = canonical v2; legacy tree = non-canonical temporary safety copy or removed
```

Do not operate indefinitely with both roots accepted as canonical.

## Batch verification

Each migration batch must prove:

1. every source legacy artifact has a disposition;
2. every retained semantic claim has one target canonical owner and a trustworthy source appropriate to that owner stage;
3. target artifacts pass applicable V0-V3 candidate checks before they are eligible for cutover;
4. direct references/traceability resolve;
5. reconstruction test passes for the migrated scope without legacy files;
6. executable evidence still agrees where applicable, while disagreements/gaps reopen the semantic owner rather than redefining upstream truth;
7. no agent/Harness routing depends on a path scheduled for retirement before its replacement routing is active.

## Cutover readiness review

Cutover is allowed only when:

- M1-M5 specs have absorbed M7 findings;
- all migration batches B1-B4 are complete;
- no P0/P1 migration or validation findings remain;
- all current docs have a migration disposition;
- reconstruction test passes without legacy tree;
- Harness routing resolves only target canonical owners;
- CI path filters/checks cover the target layout;
- G4 authorization behavior remains enforced for production implementation;
- rollback commit/ref is known and no irreversible runtime change is coupled to the docs cutover.

## Cutover procedure

Preferred cutover is one PR/squash boundary after migration has already been validated in the candidate tree:

1. stop product-document edits for the short cutover window;
2. record the pre-cutover `main` commit as rollback point;
3. ensure candidate v2 content is current with `main`;
4. if operationally useful, move current `docs/` to temporary `docs-old/` in the cutover branch;
5. move validated candidate content to `docs/`;
6. update root/scoped AGENTS, Skills, Makefile/tooling and workflow path filters in the same cutover change;
7. run local applicable checks and hosted CI;
8. verify reconstruction/routing smoke tests using only new canonical paths;
9. merge only with required checks passing;
10. remove `docs-old/` promptly after post-merge verification, or omit it entirely if Git history/rollback is sufficient.

## Rollback

Rollback is repository-only because migration/cutover must not contain runtime product changes.

Trigger rollback when post-cutover P0/P1 findings show loss/ambiguity of canonical truth, broken Harness routing or missing required CI coverage that cannot be corrected safely as a narrow follow-up.

Rollback action:

- restore the pre-cutover canonical tree/routing from the recorded commit via a normal PR/revert;
- keep migration findings in the META workstream;
- correct the candidate/specification;
- repeat readiness review before another cutover.

Do not preserve a permanently active `docs-old/` as a fallback architecture.

## Machine-readable specification track

M1-M5 semantics are now stable enough for a pilot-oriented compact registry prototype, but M7 should exercise the fields before they become a repository-wide source of routing truth. Candidate registries cover lifecycle, artifact types, locations, validations and skill/task routing.

## Current task

Pre-pilot review/conformance gate. M7 remains paused until P0/P1 findings are resolved and the minimum mechanized suite is green.

## M6 exit

M6 is complete when current knowledge/Harness/CI classes have target dispositions, migration batches and verification rules are explicit, pilot criteria are defined, and cutover/rollback can be executed without dual canonical truth.
