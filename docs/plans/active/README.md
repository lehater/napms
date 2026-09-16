# Active execution

Current: `PLAN-documentation-system-v2.md`
Goal: Design and validate Documentation System v2 before any canonical product-document migration.
Current task: Complete pre-pilot M1-M6 coherence/conformance review and mechanize P1 Harness invariants before M7 migration.
Lifecycle stage: `META`
Stage state: `IN_PROGRESS`
Lifecycle basis: `docs-v2/README.md`, `docs-v2/spec/*`, `docs-v2/migration/plan.md`, `docs-v2/review/harness-conformance-review.md`
Implementation authorization: `none`
Authorized scope: `none`
Authorization basis: `none`

## Working set

Read first:

- `docs/plans/active/PLAN-documentation-system-v2.md`
- `docs-v2/review/harness-conformance-review.md`
- `docs-v2/spec/agent-execution.md`
- `docs-v2/spec/validation.md`
- existing Harness validators only as required by the current finding

## Blockers

M7 artifact migration is paused until pre-pilot P0/P1 conformance findings are resolved and the minimum mechanized Harness suite is green.

## Gate

META review/validation work only. `docs/` remains canonical; `docs-v2/` is non-canonical until explicit cutover. No product implementation or pilot migration is authorized.

## Next

Resolve P1 findings in `docs-v2/review/harness-conformance-review.md`, starting with artifact single-owner semantics and deterministic plan/capsule consistency; then implement the minimum Harness checks through the existing `make harness-check` / `harness.yml` path.
