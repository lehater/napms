# Web UI Component Composition Integration

Status: `active`

## Goal

Integrate the completed Web UI component-composition migration from branch `docs/web-ui-component-composition-roadmap` through PR #91 after the repository's final hosted gates pass.

## Inputs

- `docs/engineering/web-ui-component-composition-roadmap.md` — executed M0-M7 migration and acceptance criteria.
- `docs/ui/component-composition.md` — durable ownership/extraction rules.
- `web/AGENTS.md` — Web working contract.
- PR #91 — complete implementation branch and final gate surface.
- Issue #90 — migration tracking issue.

## Exit criteria

- PR #91 final Web gate passes on its current final head.
- PR #91 final Harness gate passes on the same final head.
- Any material gate failure is fixed on the same branch and re-gated through Draft -> Ready for review.
- PR #91 is squash merged into `main` only after all applicable gates pass.
- Issue #90 is closed after successful integration.
- `docs/plans/active/` no longer retains this completed plan after its durable outcome is integrated.

## Blockers

Current blocker is the final hosted gate. Earlier Harness runs exposed active-plan metadata/capsule format defects; those repository-process defects are corrected on the same branch before re-gating.

## Next

Request the final hosted gate again, inspect Web/Harness results and logs, fix any remaining failures on the same branch, then squash merge PR #91 when green.
