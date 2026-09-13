# Plans

Current non-trivial execution lives under `active/`.

Completed/superseded plans are removed after their durable outcomes are absorbed into canonical repository truth. Git history is the plan history.

Long-range ordered sequencing is canonicalized outside `active/` only when it remains valid current engineering truth.

Bounded-context roadmaps that must survive workstream switches live under `docs/engineering/roadmaps/` and follow `docs/process/plan-lifecycle.md`. A parked context roadmap does not make that context active and does not justify keeping a `PLAN-*.md` under `active/`.

Current active execution: `docs/plans/active/domain-erd-revalidation.md`.

Context-roadmap registry: `docs/engineering/roadmaps/README.md`.

Completed roadmap references that remain useful include:
- `docs/engineering/target-code-structure-migration-roadmap.md` — completed M0-M7 migration to `backend/src/napms/{contexts,workflows,platform}` and final Web locality;
- `docs/engineering/code-structure-refactoring-roadmap.md` — historical I32 structural snapshot;
- `docs/engineering/application-catalogue-target-migration-roadmap.md` — completed I31 Application Catalogue target migration;
- `docs/engineering/catalogue-curation-roadmap.md` — completed I27 Catalogue Curation;
- `docs/engineering/traffic-analysis-checker-roadmap.md` — I26.

Obsolete APR design history is not retained. The current APR semantic framing is `docs/domain/access-policy-realization/README.md`; its parked future sequence is `docs/engineering/roadmaps/access-policy-realization.md`.

Only a selected current increment receives a detailed `PLAN-*.md` under `active/`.
