# Pre-pilot Harness conformance review

Status: IN PROGRESS — M7 paused until P0/P1 findings are resolved and minimum automated conformance coverage is defined.

## Review scope

Review M1-M6 against the current repository Harness, Skills, validators, lifecycle regression corpus, Makefile and hosted CI. Evaluate coherence, completeness, executability, progressive-disclosure behavior and mechanized enforcement.

## Findings

### P1 — active execution capsule is stale

`docs/plans/active/README.md` still says the current task is M1 although the active plan has completed M1-M6 and points to M7. This proves that mutable execution state can drift between the plan and the canonical active capsule.

Action: update the capsule now and add a deterministic consistency check so plan/capsule stage/task cannot silently diverge.

### P1 — v2 critical invariants are not yet mapped to executable checks

The existing Harness already has useful deterministic validators (`validate_harness.py`, `validate_plans.py`, `validate_lifecycle_transitions.py`, skill-routing corpus), but M1-M5 introduce new invariants without a rule-to-check ownership map. A specification can therefore regress while current Harness CI remains green.

Action: establish the conformance matrix below and implement the minimum P1 deterministic checks before M7 migration begins.

### P1 — artifact lifecycle ownership is ambiguous for multi-stage rows

The artifact catalog says a canonical artifact has lifecycle ownership, but entries such as `user-journey` (`S0/S1`), `constraint` (`S0/S1`), `persistence-model` (`S3/S4`) and `migration` (`S4/Implementation`) encode multiple owning stages. This weakens deterministic routing and conflicts with the single-owner principle.

Action: separate `owning-stage` from `consumed/updated-at` semantics. Every artifact type must have one semantic owner; later stages may consume/update only under an explicit rule or reopen the owner.

### P1 — task capsule contract cannot yet be mechanically validated

M4 defines the capsule shape but intentionally leaves it as prose/YAML example. Without a compact schema/validator, primary-skill uniqueness, stage validity, authorization and input/output references remain convention-only.

Action: create a pilot-grade schema/fixture contract and validator before M7 execution uses capsules as evidence. Do not make it a broad registry yet.

### P2 — skill-routing tests cover selection but not context minimization

The current routing corpus checks expected/not-expected Skills. It does not prove which artifacts/protocols were loaded, whether one primary instruction was selected, or whether unnecessary context was avoided.

Action: add Harness scenario fixtures whose observable output includes selected stage, primary skill, artifact types and context references. Avoid testing prose response text.

### P2 — lifecycle transition regression is strong but does not validate artifact applicability

Current lifecycle cases cover PASS/REWORK/BLOCKED/REOPEN/ENTRY/internal S2 reroute, selective dirty propagation and G4 revocation. They do not prove that a gate blocks only on applicable mandatory/conditional artifacts.

Action: add gate-applicability fixtures after artifact ownership is corrected.

### P2 — CI discoverability exists but v2 profile coverage is not machine-verifiable

Root Harness conventions and existing workflows expose CI, and `make harness-check` already aggregates Harness validators. M5 names validation profiles, but there is no check proving each critical profile/rule has a local/CI executor or explicit manual classification.

Action: validate the conformance matrix itself: every critical invariant must be `deterministic`, `scenario`, or `manual`, with an owner/executor.

### P2 — branch is behind current main

The docs-v2 branch diverged and is one commit behind `main` at review start. Review/cutover decisions must not rely on a stale repository baseline.

Action: reconcile current `main` before final pre-pilot sign-off; rerun Harness/CI after reconciliation.

## Conformance matrix

| Rule id | Critical invariant | Enforcement | Existing coverage | Required before M7 |
|---|---|---|---|---|
| `LIF-ENTRY` | change enters earliest affected semantic stage | scenario | lifecycle transition ENTRY is structural only | add routing scenarios |
| `LIF-REOPEN` | unresolved earlier truth routes to REOPEN, not downstream patch | deterministic + scenario | lifecycle transition corpus | extend with routing fixture |
| `LIF-DIRTY` | only dependent downstream guarantees become DIRTY | deterministic | lifecycle transition corpus | retain |
| `LIF-G4` | implementation requires current scoped G4 lease | deterministic | Harness markers + transition corpus | add capsule authorization check |
| `LIF-LEASE-REVOKE` | upstream reopen/dirty revokes dependent G4 lease | deterministic | lifecycle transition corpus | retain + capsule check |
| `ART-OWNER` | every canonical artifact type has one semantic owning stage | deterministic | none | add |
| `ART-APPLICABILITY` | mandatory/conditional/optional semantics are explicit | deterministic | prose only | add catalog check/fixtures |
| `ART-REQ-BOUNDARY` | S1 requirements are not owned/grouped by bounded context | deterministic + review | prose only | add naming/metadata rule; semantic exceptions manual |
| `ART-CANONICAL` | one stable canonical owner; generated/legacy cannot be canonical input | deterministic | partial legacy checks | extend |
| `LAY-PATH` | artifact type resolves to allowed canonical path | deterministic | none for v2 | add pilot-grade check |
| `EXEC-ONE-TASK` | one capsule represents one concrete task/gate | schema + scenario | prose only | add schema/fixtures |
| `EXEC-PRIMARY` | exactly one primary skill/instruction | deterministic | routing corpus selects skill | add capsule validation |
| `EXEC-MIN-CONTEXT` | load only direct/applicable context, expand on demonstrated need | scenario + manual | skill negative cases only | add observable routing fixture |
| `EXEC-HANDOFF` | durable result/state persisted; next task not silently executed | scenario | none | add pilot fixture |
| `VAL-PROFILE` | task/artifact maps to explicit validation profile | deterministic | none | add pilot registry/fixture |
| `VAL-CI-DISCOVERY` | agent can discover relevant local/hosted checks | deterministic | AGENTS markers + Harness workflow | retain and extend to v2 profiles |
| `VAL-MATRIX` | every critical invariant has an enforcement class/owner | deterministic | this matrix only | add validator once encoded |
| `PLAN-CAPSULE-SYNC` | active plan and active capsule cannot contradict current task/stage | deterministic | current validator missed observed drift | fix before M7 |

## Minimum mechanized suite before M7

Do not build the full v2 validator platform. Extend the existing Harness with the smallest regression surface that catches the observed risks:

1. active plan/capsule consistency check;
2. v2 artifact-catalog single-owner/applicability check;
3. pilot task-capsule schema validator with G4/primary-skill invariants;
4. a small routing fixture corpus asserting `stage + primary skill + artifact types + validation profile`, not answer wording;
5. gate applicability fixtures for mandatory/conditional/optional behavior;
6. keep all of the above behind `make harness-check` and the existing `harness.yml` hosted gate.

## Manual review remains appropriate for

- whether a requirement is genuinely solution-agnostic enough for S1;
- whether a bounded-context boundary is semantically correct;
- whether an architecture decision is significant enough for an ADR;
- whether a conditional artifact is semantically applicable when the predicate cannot be derived mechanically;
- whether context expansion was justified by a real information gap in ambiguous cases.

Manual checks should be explicit gate questions, not hidden assumptions in agent prompts.

## Review gate

M7 migration work remains paused while any P0/P1 finding above is unresolved. Pilot **selection/inventory** may be used as read-only evidence if needed, but no pilot artifact migration should begin until the minimum deterministic suite is green.
