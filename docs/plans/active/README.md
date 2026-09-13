# Active execution

Current: `domain-erd-revalidation.md` — bounded-context discovery/model revalidation before implementation.

Goal: identify and lock target domain problems/models context by context, preserve useful future work in context-local roadmaps, and avoid implementing against unresolved or obsolete semantics.

Current task: APR discovery is parked with a durable local roadmap; select the next bounded context/workstream to review.

## Working set

Read first:
- `docs/plans/active/domain-erd-revalidation.md`;
- `docs/engineering/roadmaps/README.md`;
- `docs/process/plan-lifecycle.md`.

Expand only if needed:
- the canonical domain/requirements/architecture artifacts for the next selected context;
- `docs/engineering/roadmaps/access-policy-realization.md` only when resuming APR.

## Recovery facts

- Access Policy Realization is not active execution now.
- APR canonical semantic framing remains `docs/domain/access-policy-realization/README.md`.
- APR future work is parked at `docs/engineering/roadmaps/access-policy-realization.md` with resume point D1.
- A parked context roadmap never authorizes implementation and does not require an active `PLAN-*.md`.
- New context roadmaps are created only after concrete unresolved work is identified; do not create empty placeholders.

## Blockers

No repository blocker. The next bounded context/workstream must be selected before a context-specific active task is created.

## Gate

No context runtime migration is authorized merely by discovery or by a parked roadmap. Lock the applicable canonical semantics and satisfy the selected context's design gate first.

## Next

Select the next bounded context for discovery/revalidation, work from its canonical truth, and capture its durable future sequence under `docs/engineering/roadmaps/` when enough concrete work has been identified to justify a roadmap.
