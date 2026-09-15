# Active execution

Current: `mvp-vertical-implementation-readiness.md`
Goal: execute only the G4-authorized target technical-realization core slice for the first MVP vertical.
Current task: implement infrastructure-free target core/application contracts and fake-driven executable proof from current AP Rule projection through RPM/APR to renderer/NEO ports.
Lifecycle stage: `IMPLEMENTATION`
Stage state: `IN_PROGRESS`
Lifecycle basis: G2 PASS for first MVP semantic vertical, G3 PASS in `docs/architecture/first-mvp-vertical-g3-review.md`, and S4 plan `docs/plans/active/mvp-vertical-implementation-readiness.md`.
Implementation authorization: `G4 PASS`
Authorized scope: `Slice 1 only — backend/src/napms/workflows/policy_realization/application/**; new target MVP modules under backend/src/napms/contexts/access_policy_realization/domain/ and application/; corresponding new core tests plus bounded architecture-test updates listed in the S4 plan. No persistence, adapters, migrations, bootstrap, HTTP or UI.`
Authorization basis: `docs/plans/active/mvp-vertical-implementation-readiness.md — Slice 1 G4 PASS; docs/architecture/first-mvp-vertical.md; docs/architecture/first-mvp-vertical-g3-review.md; docs/requirements/access-policy-realization-mvp.md; ADR-020/ADR-021.`

## MVP execution rule

Implement the smallest target core that proves the accepted happy path and fail-closed branches. Do not implement infrastructure merely to make the core look complete.

Preserve:

- HostAddress-only current NEP/RPM edge;
- Prefix -> unresolved, never host-expanded;
- exact APR common/missing/excess algebra;
- additive-only ENSURE-PERMIT remediation;
- excess-only drift -> no mutation;
- unresolved/incomplete/unsupported -> no mutation;
- provider rendering and NEO as outbound ports in this slice;
- no peer-domain imports or peer SQL;
- no durable workflow state.

## Working set

Read first:

- `docs/plans/active/mvp-vertical-implementation-readiness.md`
- `docs/architecture/first-mvp-vertical.md`
- `docs/requirements/access-policy-realization-mvp.md`
- `.agents/skills/implement-slice/SKILL.md`
- only existing APR algebra/architecture tests needed by the authorized scope.

## Gate

G4 PASS applies only to Slice 1. Any required production edit outside the Authorized scope returns to S4/G4.

No PostgreSQL/schema/legacy migration is authorized in this lease.

## Required proof

- targeted new APR/policy-realization core tests;
- bounded architecture tests for dependency/boundary rules;
- `make harness-check`;
- `make knowledge-check`;
- broader backend/core gate when executable in the available environment.

## Next

Implement Slice 1 inside-out: target APR domain/application values first, then workflow consumer contracts/orchestration, then core and architecture tests. Stop/reopen if implementation exposes a missing upstream guarantee.
