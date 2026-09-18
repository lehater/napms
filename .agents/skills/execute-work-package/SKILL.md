---
name: execute-work-package
description: "Use only when resuming or coordinating the currently active non-trivial NAPMS workstream. Recover its durable state, follow canonical owners through the design graph, perform the next coherent increment, and update state only when something materially changed. Do not use for isolated tasks unrelated to the active workstream."
---

# Execute Work Package

1. Read `docs/meta/current-workstream.yaml`.
2. If its status is `NONE`, return to task-first routing from root `AGENTS.md`.
3. If active, read only the referenced workstream state and the canonical graph nodes needed by its next action.
4. Confirm the user request belongs to that workstream; otherwise do not import workstream context into the task.
5. Perform the next coherent increment using the smallest applicable Skill and canonical owner set.
6. Follow `docs/canonical-graph.yaml` for affected downstream design; expand context only when a concrete dependency or contradiction requires it.
7. Update durable workstream state only when current work, blocker, authorization, accepted result or next action materially changes.
8. Stop only for missing human truth, a material contradiction, missing authorization, or requested-scope completion.

Do not create task capsules, gate transactions, lifecycle leases or checkpoint artifacts merely to continue work.
