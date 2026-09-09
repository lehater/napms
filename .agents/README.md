# NAPMS repository agent harness

The harness is intentionally small: one agent follows the applicable `AGENTS.md` chain, recovers current execution from `docs/plans/active/`, and uses the smallest relevant Skill.

## Responsibility split

- `AGENTS.md` — persistent routing and guardrails.
- `.agents/skills/` — routable operational workflows.
- `docs/process/` — reusable protocols shared by several Skills.
- `docs/domain|requirements|architecture|engineering|decisions/` — project truth.
- `docs/plans/active/` — current execution state.
- `src/AGENTS.md` and `web/AGENTS.md` — scoped implementation routing.
- `tools/` and `tests/evals/` — deterministic harness regressions.

Do not add dispatchers, role state machines or multi-agent runtime unless a demonstrated workflow requires them.
