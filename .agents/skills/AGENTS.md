# Skill authoring scope

Apply root `AGENTS.md` first.

- One stable, reusable responsibility per Skill.
- `name + description` are the routing interface.
- Project truth never belongs in a Skill body.
- Skills operate on current owners found through `docs/canonical-graph.yaml`; they do not own lifecycle state.
- Prefer extending an existing Skill over creating overlap.
- Add/update positive and confusable-negative routing cases when a trigger boundary changes.
- Run `python tools/validate_skill_routing.py` when routing metadata/corpus changes.
- Run `make design-check` when Skill/agent changes affect repository design navigation or control rules.

Use `skill-design` for one Skill and `agent-harness-design` for repository-wide agent-environment changes.
