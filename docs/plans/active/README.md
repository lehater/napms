# Active execution

Current: `PLAN-I28-user-journey-validation-pilot.md`
Goal: Prove a minimal Harness-supported user-journey validation loop on J01 Application Catalogue authoring, close its P0/P1 gaps, then retain only demonstrated reusable support.
Current task: WP-1 — validate the admitted `user-journey-validation` Skill and routing boundary.
Working mode: `execute-work-package` with `agent-harness-design` / `skill-design` only where the Harness boundary itself needs review.

## Working set

Read first:
- `.agents/skills/user-journey-validation/SKILL.md`
- `.agents/skills/skill-design/SKILL.md`
- `tests/evals/skill-routing-cases.json`

Expand only if needed:
- `tools/validate_harness.py`
- `tools/validate_skill_routing.py`
- `docs/process/plan-lifecycle.md`

## Recovery facts

- I27 is complete and absorbed; I28 is the newly accepted pilot target.
- Journey validation owns end-to-end user-goal assessment and P0-P3 gap classification, not implementation or invention of product truth.
- The first pilot is J01 Application Catalogue authoring; J01-specific facts stay in the active plan/accepted requirements, not the reusable Skill.
- No new dispatcher, role runtime or generic QA framework is justified by the pilot.

## Blockers

None known.

## Gate

WP-1 closes when the new Skill has a distinct trigger/responsibility boundary, routing coverage including confusable negatives, and `make harness-check` passes.

## Next

Run the Harness validators. If they pass, advance the capsule to WP-2 and validate J01 against accepted Catalogue Curation/Web UI behavior before implementing any discovered gaps.
