# NAPMS documentation map

The repository keeps current product truth separate by concern.

- `domain/` — living Strategic/Tactical DDD and deferred domain seams.
- `requirements/` — accepted functional, quality and acceptance baseline.
- `architecture/` — target architecture, drivers, views and ownership constraints.
- `decisions/` — durable ADRs.
- `engineering/` — implementation contracts, gates and cross-cutting engineering policies.
- `plans/active/` — current execution pointer and active non-trivial plan.
- `process/` — reusable development/agent protocols.
- `baseline/` — accepted readiness/provenance snapshots, not the primary place to edit current truth.

Historical reconstruction, Legacy evidence and superseded DDD experiments remain in `lehater/sssr_xlam` and are not product truth here.

For a new work session: root `AGENTS.md` -> `plans/active/README.md` -> current plan -> nearest scoped `AGENTS.md`.
