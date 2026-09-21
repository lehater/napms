# NAPMS repository agent harness

The harness is intentionally small: start from the explicit task, follow the applicable `AGENTS.md` chain, load the smallest relevant Skill, and expand context only when the task demonstrates a dependency.

Conversation history is disposable execution context. The repository working tree contains the reconstructable current project specification, current execution state and executable evidence. Git history is the archive for genuinely replaced material.

## Responsibility split

- `AGENTS.md` — persistent routing and guardrails, including CI execution discoverability.
- `.agents/skills/` — routable judgement-heavy operational workflows.
- `docs/process/` — reusable protocols shared by several Skills.
- `docs/requirements/` — current product behavior and quality contracts, including implemented/as-built requirements.
- `docs/domain/` — current Strategic/Tactical DDD and semantic ownership.
- `docs/architecture/` — current as-built and target architecture contracts.
- `docs/decisions/` — design decisions still needed to reproduce or evolve the current system.
- `docs/engineering/` — current API, persistence, runtime, configuration and operational contracts.
- `docs/contracts/ui/` plus `docs/architecture/mvp-frontend-*.yaml` and `docs/plans/mvp-frontend-*.yaml` — current UI/frontend behavior, architecture, component, verification, test and implementation design.
- `docs/plans/active/README.md` — compact current-task resume state, loaded only when current execution, gate or authorization matters to the requested task.
- `docs/plans/active/PLAN-*.md` — active coordination only while needed for current execution.
- `backend/src/AGENTS.md` and `web/AGENTS.md` — scoped implementation routing.
- `tools/` and `backend/tests/evals/` — deterministic harness validation plus routing-eval inputs/contracts.
- `.github/workflows/` — hosted execution of repository gates; inspect applicable triggers and `workflow_dispatch` before declaring a check unavailable.

For resume/continue/current-plan work, recover from the active capsule before loading the working set. For an unrelated audit, review, research task or repository question, do not load the active capsule unless the task later demonstrates a dependency on current execution state.

Read the full active plan on demand rather than as mandatory startup context. Prefer a fresh chat after a semantic phase change or when conversation context becomes costly; recover durable current state from the repository instead of prior chat history.

## Documentation retention guardrail

Implemented project design is not historical by virtue of being implemented. Do not remove requirements, architecture contracts, ADRs, API/persistence contracts or UI specifications while they are needed to reconstruct the current designed system.

Archive/remove only material that no longer describes either current as-built or current target design: obsolete alternatives, superseded-only specifications, completed migration/checkpoint material, audit snapshots and finished execution plans. When a file mixes history with current design, preserve or rewrite the current design before removing the historical portion.

Prefer repository-local checks during ordinary editing when available. When the current agent environment cannot execute the required deterministic command, an applicable manually dispatchable GitHub Actions workflow is a valid intermediate execution surface; `Ready for review` remains the final hosted PR gate.

Do not add dispatchers, role state machines or multi-agent runtime unless a demonstrated current requirement needs them.
