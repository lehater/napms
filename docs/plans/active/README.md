# Active execution

Current: `PLAN-web-ui-component-composition.md`

Goal: integrate the completed Web UI component-composition migration through the repository's final hosted gates and one squash merge.

Current task: correct the failed Harness plan-continuity check, then re-run the final PR gates on the same branch.

## Working set

Read first:
- `docs/plans/active/PLAN-web-ui-component-composition.md`
- `docs/engineering/web-ui-component-composition-roadmap.md`
- `web/AGENTS.md`
- `docs/ui/component-composition.md`

Expand only to PR #91 workflow results/logs and the specific failing file when a gate reports a material defect.

## Blockers

The first final Harness gate failed because this active index did not use the required `Current: <plan-file>` contract. The migration itself remains on the same branch; no merge has occurred.

## Gate

PR #91 must be marked Ready for review only when the branch is ready for a complete Web + Harness final gate. If a material failure occurs, return PR #91 to draft, fix on `docs/web-ui-component-composition-roadmap`, and gate again. Squash merge only when all applicable final checks pass on the final head.

## Next

Commit this capsule repair, mark PR #91 Ready for review again, inspect both hosted gate results and logs, and either fix the same branch or squash merge when green.
