# Active execution

Current: `PLAN-018-i18-technical-domain-access-resolution.md`

Goal: close I18 Technical-to-Domain Access Resolution with final architecture review, canonical truth absorption and exact-head hosted gates.

Current task: WP4 — architecture review and closure.

Working mode: architecture-review + execute-work-package.

## Working set

Read first:
- `docs/plans/active/PLAN-018-i18-technical-domain-access-resolution.md`
- `docs/architecture/access-policy-realization-resolution-boundary.md`

Expand only if needed into:
- `docs/domain/access-policy-realization/tactical-model.md`;
- `docs/requirements/technical-domain-access-resolution-acceptance-examples.md`;
- APR Domain/Application/adapters and their tests;
- PostgreSQL greenfield I18 proof;
- current-state/roadmap/strategic ownership;
- hosted workflow results.

## Recovery facts

- WP0 Tactical DDD/requirements/architecture are accepted.
- WP1 framework-free shared APR resolution core is implemented.
- WP2 predicate-aware RC/ACC + one-way TAE projection adapters are implemented without peer SQL bypass.
- WP3 durable PostgreSQL proof covers Exact, effective-time change, Ambiguous and zero Access Rule/Decision side effects; unit/adapter proofs cover Covered/Partial/Unresolved/Unknown.
- Protocol Any remains explicit Unknown by accepted first-slice boundary.
- No APR persistence, HTTP/Web, Authority Management workflow, NEP placement or I20 reconciliation semantics exist.
- Branch is based on current main and is not behind.

## Blockers

None before hosted closure gates.

## Gate

WP4 must:
- close all P0/P1 architecture findings;
- keep consumer-independent resolution and exact remainder semantics intact;
- verify canonical current-state/roadmap/ownership agree with implementation;
- run core/postgres/harness/knowledge hosted gates on one exact closure candidate;
- only after green gates remove completed PLAN-018, set active execution to Current: none and promote I19 as next;
- rerun final gates on the final exact head before squash merge.

## Next

Run the first hosted closure-candidate gates. Fix only demonstrated P0/P1 issues, then finalize I18 closure.
