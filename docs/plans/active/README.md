# Active execution

Current: `PLAN-web-ui-convergence.md`

Goal: finish Web UI convergence with accessible browser journeys and final hosted evidence.

Current task: align stale journey assertions with the current accessible UI contract, then re-gate PR #94.

## Working set

Read first:
- `docs/plans/active/PLAN-web-ui-convergence.md`
- `web/AGENTS.md`
- `docs/ui/component-composition.md`

Expand to `e2e/test_j01_application_authoring.py`, `e2e/test_j03_connectivity_request_decision.py`, and the exact routed UI owners implicated by a failing journey.

## Blockers

None.

## Gate

Keep PR #94 draft while fixing the journey assertions. Mark Ready only for the complete Web + Harness + Docker runtime + Browser Journey gate. Any material failure returns the PR to draft. After green gates, clean the active plan and re-gate that cleanup head before squash merge.

## Next

Update the two stale browser assertions without weakening product semantics, then run the complete hosted gate.
