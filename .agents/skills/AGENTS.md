# Skill authoring scope

Apply root `AGENTS.md` first.

- One stable, reusable responsibility per Skill.
- `name + description` are the routing interface.
- Project truth never belongs in a Skill body.
- Shared mechanics belong in `docs/process/`, not duplicated across Skills.
- Prefer extending an existing Skill over creating an overlapping one.
- Add/update positive and confusable-negative routing corpus cases when a trigger boundary changes.
- `make harness-check` validates deterministic corpus/structure only; actual model-routing observations are separate evidence and can be scored with `tools/evaluate_skill_routing_results.py`.

Use `skill-design` to admit/review one Skill and `agent-harness-design` for whole-harness changes.
