# Active execution

Current: `PLAN-018-i18-technical-domain-access-resolution.md`

Goal: implement I18 Technical-to-Domain Access Resolution as one consumer-independent APR capability over effective RC + ACC knowledge.

Current task: WP0 — Tactical DDD and observable-contract closure.

Working mode: domain-model-change + execute-work-package.

## Working set

Read first:
- `docs/plans/active/PLAN-018-i18-technical-domain-access-resolution.md`
- `docs/domain/ubiquitous-language.md`
- `docs/domain/technical-access-evidence/tactical-model.md`
- `docs/domain/semantic-ownership.md`

Expand only if needed into:
- current RC/ACC Domain/Application contracts;
- TAE core model;
- architecture/current-state/roadmap;
- implementation after the WP0 semantic gate.

## Recovery facts

- I17 is complete; TAE stores normalized source-qualified evidence and owns no domain-resolution truth.
- I18 belongs to Access Policy Realization.
- Proposal-side and Reconciliation-side matching are SAME_CAPABILITY.
- Domain Interaction identity is Source Component Deployment + Destination Component Deployment + immutable DCS revision.
- RC owns effective endpoint realization; ACC owns DCS + effective DeploymentResourceBinding.
- I19 placement and I20 reconciliation remain downstream.
- No APR implementation/persistence/runtime currently exists.

## Blockers

None identified before WP0. Any unresolved protocol/port or remainder semantics must remain explicit and keep the implementation gate closed.

## Gate

WP0 passes only when Tactical DDD + requirements/examples + architecture define:
- shared resolution result and correspondence algebra;
- Exact/Covered/Partial/Ambiguous/Unresolved/Unknown behavior;
- supported predicate/remainder semantics;
- effective-time/provenance rules;
- consumer-owned RC/ACC and TAE adapter boundaries;
- explicit fail-closed treatment for unsupported meaning.

Infrastructure and implementation remain closed until this gate passes.

## Next

Complete and review WP0. Stop before code if any P0/P1 semantic unknown remains.
