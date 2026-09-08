# Skill authoring scope

Apply root `AGENTS.md` first.

- One stable, reusable responsibility per Skill.
- `name + description` are the routing interface.
- Project truth never belongs in a Skill body.
- Shared mechanics belong in `docs/process/`, not duplicated across Skills.
- Prefer extending an existing Skill over creating an overlapping one.
- Add/update routing eval cases when a trigger boundary changes.
- Run `make harness-check` after harness/Skill changes.

Use `skill-design` to admit/review one Skill and `agent-harness-design` for whole-harness changes.
