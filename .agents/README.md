# NAPMS repository agent harness

The harness is intentionally small: a fresh chat follows the applicable `AGENTS.md` chain, recovers the current task from the compact `docs/plans/active/README.md` resume capsule, and loads only the smallest relevant Skill and working set.

Conversation history is disposable execution context. Durable project truth, execution state and code checkpoints live in the repository.

## Responsibility split

- `AGENTS.md` — persistent routing and guardrails.
- `.agents/skills/` — routable operational workflows.
- `docs/process/` — reusable protocols shared by several Skills.
- `docs/domain|requirements|architecture|engineering|decisions/` — project truth.
- `docs/plans/active/README.md` — compact current-task resume state.
- `docs/plans/active/PLAN-*.md` — plan coordination, dependencies, future stages and overall exit.
- `src/AGENTS.md` and `web/AGENTS.md` — scoped implementation routing.
- `tools/` and `tests/evals/` — deterministic harness regressions.

Read the full active plan on demand rather than as mandatory startup context. Prefer a fresh chat after a semantic phase change or when conversation context becomes costly; recover from repository state instead of prior chat history.

Do not add dispatchers, role state machines or multi-agent runtime unless a demonstrated workflow requires them.
