# Documentation scope

Apply root `AGENTS.md` first.

## Canonical ownership

- `domain/` — living Strategic/Tactical DDD: meaning, identity, lifecycle and semantic ownership.
- `requirements/` — current accepted observable product/quality behavior.
- `architecture/` — current target structure, dependency, consistency and runtime constraints.
- `decisions/` — consequential ADRs and explicit supersession.
- `engineering/` — implementation/runtime contracts, policies and capability snapshots.
- `ui/` — implementation-oriented presentation/interaction guidance.
- `plans/active/` — current execution state/coordination only.
- `baseline/` — accepted historical snapshots/provenance, not current truth.
- `process/` — reusable repository working protocols.

## Layer discipline

Keep one decision at its highest owning layer and link downward instead of retelling it.

- Requirements answer **what observable behavior/quality must hold**.
- Domain answers **what the concepts mean and who owns them**.
- Architecture answers **how semantic owners compose and what structural/runtime constraints preserve correctness**.
- UI answers **how accepted behavior is presented/interacted with**.
- Active plans answer **what execution delta is current, blocked and next**.

A lower layer may repeat a one-line invariant only when omission would make a local contract unsafe; otherwise link to the owner.

Historical milestone packets must not remain in living `requirements/`, `architecture/` or `ui/` merely as archives. Absorb durable outcomes into current owners; keep provenance in `baseline/` and Git history.

## Knowledge discipline

Classify material content as known/accepted, hypothesis, unknown or conflict. Do not turn an unknown into a convenient implementation assumption.

When a code finding changes accepted behavior, domain language/ownership or architecture, update the highest affected canonical layer first, then propagate only the required delta downward.

Completed/superseded execution artifacts do not remain as archives in the working tree; Git history preserves them.
