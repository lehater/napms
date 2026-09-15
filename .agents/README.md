# NAPMS repository agent harness

The harness is intentionally small: start from the explicit task, follow the applicable `AGENTS.md` chain, load the smallest relevant Skill, and expand context only when the task demonstrates a dependency.

Conversation history is disposable execution context. Durable project truth, execution state and code checkpoints live in the repository.

## Responsibility split

- `AGENTS.md` — persistent routing and guardrails, including CI execution discoverability.
- `.agents/skills/` — routable judgement-heavy operational workflows.
- `docs/process/` — reusable protocols shared by several Skills.
- `docs/domain|requirements|architecture|engineering|decisions/` — project truth.
- `docs/plans/active/README.md` — compact current-task resume state, loaded only when current execution, gate or authorization matters to the requested task.
- `docs/plans/active/PLAN-*.md` — plan coordination, dependencies, future stages and overall exit.
- `backend/src/AGENTS.md` and `web/AGENTS.md` — scoped implementation routing.
- `tools/` and `backend/tests/evals/` — deterministic harness validation plus routing-eval inputs/contracts.
- `.github/workflows/` — hosted execution of repository gates; inspect applicable triggers and `workflow_dispatch` before declaring a check unavailable.

For resume/continue/current-plan work, recover from the active capsule before loading the working set. For an unrelated audit, review, research task or repository question, do not load the active capsule unless the task later demonstrates a dependency on current execution state.

Read the full active plan on demand rather than as mandatory startup context. Prefer a fresh chat after a semantic phase change or when conversation context becomes costly; recover durable state from the repository instead of prior chat history.

Prefer repository-local checks during ordinary editing when available. When the current agent environment cannot execute the required deterministic command, an applicable manually dispatchable GitHub Actions workflow is a valid intermediate execution surface; `Ready for review` remains the final hosted PR gate.

Do not add dispatchers, role state machines or multi-agent runtime unless a demonstrated workflow requires them.
