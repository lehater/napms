# Active execution

Current: `PLAN-target-code-structure-migration.md`
Goal: migrate NAPMS to the accepted final backend and Web taxonomy without product/domain semantic change.
Current task: M6 — implement final Web locality in two atomic commits on `refactor/m6-web-locality`.

## Working set

Read first:
- `docs/plans/active/PLAN-target-code-structure-migration.md`
- `docs/architecture/code-structure.md`
- `docs/engineering/target-code-structure-migration-roadmap.md`

Expand only if needed: current `web/src` files being moved.

## Blockers

None.

## Gate

M5 is complete in PR #78, squash merge `3bd5525061a382b77d6298ea5d607bd7f2f63179`. M6 ownership is classified: application bootstrap/routing belongs under `app/`; feature HTTP/model/UI belongs under the owning feature; root `api.ts` must disappear; root `components` must contain only shared UI primitives; `lib` remains technical only. No generic shared semantic model/package is introduced.

## Next

Implement root app/API ownership cleanup, then normalize every feature to applicable `api / model / components / pages` directories, add Web structure guards, run local gates, and stop for architectural review before the M6 PR.
