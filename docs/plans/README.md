# Plans

Current non-trivial execution lives under `active/`.

Completed/superseded plans are removed after their durable outcomes are absorbed into canonical repository truth. Git history is the plan history.

Unresolved bounded-context work that must survive a workstream switch lives primarily under `docs/engineering/context-problems/` and follows `docs/process/plan-lifecycle.md`. A context problem register records problems, gaps, real dependencies and blockers without making that context active and without asserting a total execution order.

Long-range ordered sequencing is canonicalized outside `active/` only when the order itself remains useful current engineering truth. Context roadmaps are optional and should not be created merely to list future work.

Current active execution: `docs/plans/active/domain-erd-revalidation.md`.

Context-problem registry: `docs/engineering/context-problems/README.md`.

Completed roadmap references that remain useful include:
- `docs/engineering/target-code-structure-migration-roadmap.md` — completed M0-M7 migration to `backend/src/napms/{contexts,workflows,platform}` and final Web locality;
- `docs/engineering/code-structure-refactoring-roadmap.md` — historical I32 structural snapshot;
- `docs/engineering/application-catalogue-target-migration-roadmap.md` — completed I31 Application Catalogue target migration;
- `docs/engineering/catalogue-curation-roadmap.md` — completed I27 Catalogue Curation;
- `docs/engineering/traffic-analysis-checker-roadmap.md` — I26.

Obsolete APR design history is not retained. The current APR semantic framing is `docs/domain/access-policy-realization/README.md`; its unresolved work is parked in `docs/engineering/context-problems/access-policy-realization.md`.

Only a selected current increment receives a detailed `PLAN-*.md` under `active/`.
