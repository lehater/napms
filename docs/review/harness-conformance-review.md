# Pre-pilot Harness conformance review

Status: PRE-PILOT PASS — no open P0/P1 design finding; branch reconciled with `main`; hosted Harness green on the reconciled pre-pilot head.

## Review scope

Review M1-M6 against the current repository Harness, Skills, validators, lifecycle regression corpus, Makefile and hosted CI. Evaluate coherence, completeness, executability, progressive-disclosure behavior and mechanized enforcement.

## Resolved P1 findings

- `PLAN-CAPSULE-SYNC`: plan/capsule drift detection is isolated in `tools/validate_plan_capsule_sync.py`; base `tools/validate_plans.py` remains the canonical continuity/context-budget validator.
- `ART-OWNER`: artifact catalog has exactly one semantic owning stage per canonical artifact type; later discovery routes through reopen rather than multi-owner syntax.
- `EXEC-CAPSULE`: M4 defines pilot-grade capsule authorization/context fields and deterministic invariants; serialized valid/invalid capsule fixtures are checked by `tools/validate_docs_v2.py`.
- `VAL-MAPPING`: `tools/validate_docs_v2.py` is part of `make harness-check` and validates catalog, serialized capsule, routing and gate-applicability conformance.
- `MIGRATION-UPSTREAM-TRUTH`: M6 forbids reconstructing missing S0/S1 truth from domain, architecture, implementation or tests; missing trustworthy upstream truth is an explicit `DEFER`/gap.
- `MIGRATION-VALIDATION-ORDER`: candidate-mode Harness/validation support is established in B0 before candidate content batches; B4 is the final canonical routing switch.
- `CONTEXT-BUDGET`: the inherited active S3 resume capsule was reduced to its direct architecture candidate; additional sources are loaded only for a concrete review question.

## Hosted evidence

The reconciled branch is `behind_by: 0` relative to `main`; merge base is current `main` commit `87ceb05fc8aba8bf86d0713a615ca71793ac92c8`.

Hosted `harness gate` run `35070783398` completed successfully on branch head `df202a355acd8974770862d46dd52af6b9c96e00`. Its `make harness-check` job passed all current Harness checks:

- `validate_harness.py` — 9 skills validated;
- `validate_plans.py` — active plan continuity, lifecycle lease and context budget OK;
- `validate_plan_capsule_sync.py` — plan/capsule drift check OK;
- `validate_skill_routing.py` — 27 cases for 9 skills structurally valid; model routing not executed;
- `validate_lifecycle_transitions.py` — 17 cases OK;
- `validate_docs_v2.py` — catalog, serialized capsule, routing and gate applicability conformance OK.

This is the required pre-pilot hosted Harness evidence. It does not claim that deferred runtime/model-routing evidence has already been exercised.

## Remaining P2 / pilot evidence

### P2 — context minimization needs runtime evidence

M4 exposes `context_refs` and reasoned `context_expansions`, and regression fixtures can assert required/forbidden refs without inspecting chain-of-thought. Static conformance checks verify the contract. M7 provides the first actual routed-task evidence.

### P2 — path/layout conformance is not yet executable

M3 defines path patterns but the catalog is still Markdown. A broad parser would be brittle. M7 validates target paths for the selected pilot and determines whether a compact machine-readable artifact registry is justified before repository-wide path validation is implemented.

### P2 — validation profile executor coverage is not yet registry-backed

M5 profiles exist and routing fixtures reference known profiles. Existing `make harness-check`/hosted Harness is the executor surface. M7 records actual local/CI commands used and exposes any profile with no practical executor before a registry is frozen.

## Conformance matrix

| Rule id | Critical invariant | Enforcement | Current coverage | Pre-M7 state |
|---|---|---|---|---|
| `LIF-ENTRY` | change enters earliest affected semantic stage | scenario | lifecycle corpus + docs-v2 routing fixtures | mechanized structurally; exercise in pilot |
| `LIF-REOPEN` | unresolved earlier truth routes to REOPEN | deterministic + scenario | lifecycle transition corpus | covered |
| `LIF-DIRTY` | only dependent downstream guarantees become DIRTY | deterministic | lifecycle transition corpus | covered |
| `LIF-G4` | implementation requires current scoped G4 lease | deterministic | plan validator + serialized capsule fixtures + M4 contract | covered |
| `LIF-LEASE-REVOKE` | upstream reopen/dirty revokes dependent G4 lease | deterministic | lifecycle transition corpus + M4 contract | covered |
| `ART-OWNER` | every canonical artifact type has one semantic owner | deterministic | `validate_docs_v2.py` | covered |
| `ART-APPLICABILITY` | mandatory/conditional/optional semantics | deterministic | catalog check + gate fixtures | covered |
| `ART-REQ-BOUNDARY` | S1 requirements not owned/grouped by BC | deterministic + review | catalog invariant; migration semantics manual | sufficient for pilot |
| `ART-CANONICAL` | one stable canonical owner; generated/legacy not canonical input | deterministic + review | existing legacy checks + v2 specs | pilot verifies target refs |
| `LAY-PATH` | artifact type resolves to allowed path | deterministic | M3 prose only | defer registry; verify pilot paths |
| `EXEC-ONE-TASK` | one capsule = one concrete task/gate | deterministic + scenario | M4 contract + serialized capsule fixtures | pilot exercises runtime handoff |
| `EXEC-PRIMARY` | exactly one primary instruction | deterministic | serialized capsule fixtures + routing fixtures | covered |
| `EXEC-MIN-CONTEXT` | direct context only; expansion needs demonstrated reason | scenario + manual | M4 observable contract + capsule fixtures | pilot runtime evidence required |
| `EXEC-HANDOFF` | next task is named but not silently executed | scenario | M4 contract | pilot runtime evidence required |
| `VAL-PROFILE` | task maps to explicit validation profile | deterministic | routing fixtures + known profile set | covered for fixture set |
| `VAL-CI-DISCOVERY` | agent can discover local/hosted checks | deterministic | AGENTS/Harness workflow + Makefile + observed hosted run | covered |
| `PLAN-CAPSULE-SYNC` | active plan/capsule do not silently diverge | deterministic | `validate_plan_capsule_sync.py` | covered |

## Minimum mechanized suite

Implemented through the existing Harness rather than a parallel framework:

1. active plan/capsule continuity and drift checks;
2. artifact catalog single-owner/applicability check;
3. serialized pilot capsule authorization/context regression cases;
4. routing fixtures asserting `stage + primary instruction + artifact types + validation profile`;
5. mandatory/conditional/optional gate-applicability fixtures;
6. all checks reachable through `make harness-check` and proven through the existing hosted `harness.yml` command path.

## Manual review remains appropriate for

- whether a requirement is genuinely solution-agnostic enough for S1;
- whether a bounded-context boundary is semantically correct;
- whether an architecture decision is significant enough for an ADR;
- whether a conditional artifact is semantically applicable when its predicate cannot be derived mechanically;
- whether a context expansion was justified by a real information gap in ambiguous cases.

Manual checks are explicit gate questions, not hidden assumptions in agent prompts.

## Review gate

Pre-pilot gate PASS. No P0/P1 design finding remains open, the branch is reconciled with current `main`, and the hosted Harness is green on the reconciled pre-pilot head. M7 may now begin with selection/inventory of one bounded slice. Runtime context-minimization/handoff evidence and the need for a compact path/profile registry are evaluated from that pilot rather than by building more speculative infrastructure first.
