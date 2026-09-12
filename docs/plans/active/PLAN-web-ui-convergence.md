# PLAN — Web UI convergence

Status: `active`

## Goal

Finish the routed Web UI convergence so shared design-system ownership, semantic visual tokens, page/table geometry, and browser journeys agree without changing accepted product semantics.

## Inputs

- Issue #93 and PR #94.
- `web/AGENTS.md` and `docs/ui/component-composition.md`.
- The current design-system/tokens and `web/scripts/check-ui-boundaries.mjs`.
- Browser Journey failures on the current PR head.

## Exit criteria

- Feature UI remains converged on durable design-system ownership and semantic tokens/presets.
- Browser journeys assert the current accessible UI contract rather than obsolete DOM roles/text-node boundaries.
- Web, Harness, Docker runtime, and Browser Journey gates are green on the same final head.
- The active execution capsule is cleaned before merge and that cleanup head is re-gated.

## Blockers

None.

## Next

Align the two failing browser journey assertions with the current accessible UI, run the complete hosted gate, clean this active plan, re-gate the cleanup head, then squash merge PR #94.
