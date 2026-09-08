# Documentation scope

Apply root `AGENTS.md` first.

## Canonical ownership

- `domain/` — living Strategic/Tactical DDD.
- `requirements/` — accepted product behavior, quality and semantic contracts.
- `architecture/` — current target architecture.
- `decisions/` — consequential ADRs.
- `engineering/` — engineering contracts/policies and implementation snapshots.
- `plans/active/` — current execution state only.
- `baseline/` — accepted snapshots/provenance, not the primary place to edit current truth.
- `process/` — reusable repository working protocols.

Do not duplicate one current decision across several files. Link to the canonical owner.

## Knowledge discipline

Classify material content as known/accepted, hypothesis, unknown or conflict. Do not turn an unknown into a convenient implementation assumption.

When a code finding changes accepted behavior, domain language/ownership or architecture, update the highest affected canonical layer first, then propagate downward.

Completed/superseded execution artifacts do not remain as archives in the working tree; Git history preserves them.
