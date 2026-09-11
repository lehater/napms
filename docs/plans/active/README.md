# Active execution

Current: `PLAN-web-ui-convergence.md`

Goal: converge routed Web UI screens on the shared design-system composition model and remove parallel legacy layout paths left after #91.

Current task: finish the repository-wide UI tail audit, then migrate confirmed legacy consumers in coherent groups without weakening feature semantics.

## Working set

Read first:
- `docs/plans/active/PLAN-web-ui-convergence.md`
- `web/AGENTS.md`
- `docs/ui/component-composition.md`
- `docs/ui/design-system.md`
- `web/scripts/check-ui-boundaries.mjs`

Expand to routed `web/src/features/**` pages/components and their existing design-system owners as the audit identifies concrete tails.

## Blockers

None. The previous #91 active capsule remained stale on `main`; this increment replaces it.

## Gate

Keep the PR draft while implementation is accumulating. Mark Ready only when the complete convergence change is ready for all applicable hosted checks. On any material failure, return to draft, fix on `refactor/web-ui-convergence`, and gate again. Squash merge only when Web, Harness, Docker runtime, and browser journey checks applicable to the final head are green.

## Next

Count and classify local page shells, width constraints, manual tables/pagers/forms, compatibility imports, raw visual constants, and dead duplicate screens; migrate them to shared composition, strengthen boundary enforcement, then run the final gate.
