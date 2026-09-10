# Active execution

Current: `PLAN-I28-user-journey-validation-pilot.md`
Goal: Prove a minimal Harness-supported user-journey validation loop on J01 Application Catalogue authoring, close its P0/P1 gaps, then retain only demonstrated reusable support.
Current task: WP-1 — validate `user-journey-validation` routing and make repository CI discoverable as an agent execution surface.
Working mode: `execute-work-package` with `agent-harness-design` / `skill-design` only where the Harness boundary itself needs review.

## Working set

Read first:
- `.agents/skills/user-journey-validation/SKILL.md`
- `AGENTS.md`
- `docs/process/working-loop.md`
- `tests/evals/skill-routing-cases.json`
- `tools/validate_harness.py`

Expand only if needed:
- `.agents/skills/skill-design/SKILL.md`
- `.github/workflows/harness.yml`
- `tools/validate_skill_routing.py`
- `docs/process/plan-lifecycle.md`

## Recovery facts

- I27 is complete and absorbed; I28 is the newly accepted pilot target.
- Journey validation owns end-to-end user-goal assessment and P0-P3 gap classification, not implementation or invention of product truth.
- The first pilot is J01 Application Catalogue authoring; J01-specific facts stay in the active plan/accepted requirements, not the reusable Skill.
- Repository GitHub Actions are part of the Harness execution surface: agents must inspect applicable workflows before declaring a deterministic gate unexecutable.
- `Ready for review` is the final hosted PR gate; `workflow_dispatch` may be used for intermediate equivalent checks when local execution is unavailable and the connected capability can dispatch it.
- The current GitHub connector can inspect Actions but does not expose creation of a new workflow-dispatch run; this is a tool limitation, not absence of CI.
- No new dispatcher, role runtime or generic QA framework is justified by the pilot.

## Blockers

The current connector cannot create a new `workflow_dispatch` run. WP-1 executable evidence therefore still requires either a checkout-capable environment, a manual workflow dispatch, or the final Ready-for-review hosted gate.

## Gate

WP-1 closes when the new Skill has a distinct trigger/responsibility boundary, routing coverage including confusable negatives, CI discoverability/fallback rules are guarded by the Harness validator, and `make harness-check` passes locally or through the equivalent hosted Harness workflow.

## Next

Obtain executable Harness-gate evidence. If it passes, advance the capsule to WP-2 and validate J01 against accepted Catalogue Curation/Web UI behavior before implementing any discovered gaps.
