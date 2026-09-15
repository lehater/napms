# NAPMS documentation map

The working tree keeps current truth separate by responsibility and keeps historical execution/design detail out of the normal agent surface.

- `domain/` — living Strategic/Tactical DDD: meaning, identity, lifecycle and semantic ownership.
- `requirements/` — current accepted product/quality behavior; use `requirements/README.md` to route to the smallest requirement family.
- `architecture/` — current target structure/ownership/runtime constraints; use `architecture/README.md`.
- `decisions/` — consequential ADRs, including explicit supersession history.
- `engineering/` — implementation/runtime contracts, policies and capability snapshots.
- `ui/` — implementation-oriented visual/interaction guidance derived from current requirements.
- `plans/active/` — compact current execution capsule plus coordination plan.
- `process/` — reusable development/agent protocols.
- `baseline/` — accepted historical snapshots/provenance; not normal startup context.

Historical Wave-1 G2/G3 working packets are preserved by baseline summaries and Git history rather than living beside current requirements/architecture.

For a fresh non-trivial task use task-first recovery:

```text
root AGENTS.md
  -> nearest scoped AGENTS.md
  -> smallest applicable Skill
  -> minimal task working set
```

Insert `docs/plans/active/README.md` after the root map only when the requested task resumes/continues current execution, depends on the current lifecycle/gate, or needs implementation authorization. Do not preload the current product workstream for unrelated audits, reviews, research or repository questions.

Read a full active PLAN only for planning/coordination/task transition or when the capsule lacks a material fact.
