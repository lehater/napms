# Active execution

Current: `PLAN-web-ui-convergence.md`

Goal: converge routed Web UI screens on the shared design-system composition model and remove parallel legacy layout paths left after #91.

Current task: finish convergence enforcement and validate the final routed Web UI on one hosted-gate head.

## Working set

Read first:
- `docs/plans/active/PLAN-web-ui-convergence.md`
- `web/AGENTS.md`
- `docs/ui/component-composition.md`
- `web/scripts/check-ui-boundaries.mjs`

Expand to `docs/ui/design-system.md` or routed feature/design-system files only when a concrete UI rule or failing check requires them.

## Blockers

None.

## Gate

Keep the PR draft while implementation is accumulating. Mark Ready only when the complete convergence change is ready for all applicable hosted checks. On any material failure, return to draft, fix on `refactor/web-ui-convergence`, and gate again. Squash merge only when Web, Harness, Docker runtime, and browser journey checks applicable to the final head are green.

## Next

Run the strict UI ownership/build check, then Web, Harness, Docker runtime, and browser journey on one head. Resolve any failure before active-plan cleanup and the final re-gate.
