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

For a fresh non-trivial session use the repository recovery path:

```text
root AGENTS.md
  -> docs/plans/active/README.md
  -> nearest scoped AGENTS.md
  -> smallest applicable Skill
  -> capsule Read first working set
```

Read a full active PLAN only for planning/coordination/task transition or when the capsule lacks a material fact.
