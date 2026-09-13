# Active execution

Current: `domain-erd-revalidation.md` — bounded-context discovery/model revalidation before implementation.

Goal: identify and lock target domain problems/models context by context, preserve unresolved future work as context-local problem registers, and avoid implementing against unresolved or obsolete semantics.

Current task: APR discovery is parked with a durable context problem register; select the next bounded context/workstream to review.

Lifecycle stage: `S2`

Stage state: `IN_PROGRESS`

Lifecycle basis: active domain revalidation plan `docs/plans/active/domain-erd-revalidation.md`; completed context decisions remain in their canonical domain/ADR owners and unresolved APR work is parked in its context problem register.

Implementation authorization: `none`

Authorized scope: `none`

Authorization basis: `none`

## Working set

Read first:
- `docs/plans/active/domain-erd-revalidation.md`
- `docs/engineering/context-problems/README.md`

Expand only if needed:
- `docs/process/plan-lifecycle.md` when execution-state persistence or parking mechanics are being changed;
- the canonical domain/requirements/architecture artifacts for the next selected context;
- `docs/engineering/context-problems/access-policy-realization.md` only when resuming APR;
- `docs/process/domain-design-stage.md` when S2 routing or G2 evaluation is active.

## Recovery facts

- Access Policy Realization is not active execution now.
- APR canonical semantic framing remains `docs/domain/access-policy-realization/README.md`.
- APR unresolved future work is parked at `docs/engineering/context-problems/access-policy-realization.md`.
- The APR register records problems and real dependencies but deliberately does not impose a total execution order.
- A parked context problem register never authorizes implementation and does not require an active plan of its own.
- Create a context roadmap only if a future selected workstream has an evidence-backed ordering worth preserving.
- New context problem registers are created only after concrete unresolved work is identified; do not create empty placeholders.
- The lifecycle lease records current execution authority; this discovery/model-revalidation work has no G4 implementation authorization.

## Blockers

No repository blocker. The next bounded context/workstream must be selected before a context-specific active task is created.

## Gate

No context runtime migration is authorized merely by discovery or by a parked problem register. Lock the applicable canonical semantics and satisfy the selected context's design gate first. Code execution additionally requires a scoped G4 implementation lease.

## Next

Select the next bounded context for discovery/revalidation, work from its canonical truth, and capture its unresolved problems/gaps/dependencies under `docs/engineering/context-problems/` when enough concrete work has been identified to preserve.
