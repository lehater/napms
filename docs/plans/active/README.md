# Active execution

Current: `PLAN-018-i18-technical-domain-access-resolution.md`

Goal: implement I18 Technical-to-Domain Access Resolution as one consumer-independent APR capability over effective RC + ACC knowledge.

Current task: WP3 — integration proof.

Working mode: implement-slice + architecture-review + execute-work-package.

## Working set

Read first:
- `docs/requirements/technical-domain-access-resolution-acceptance-examples.md`
- APR Domain/Application/adapters;
- existing PostgreSQL integration fixture patterns for TAE, ACC and RC.

## Recovery facts

- WP0 accepted semantics are closed.
- WP1 shared resolution core is implemented.
- WP2 RC/ACC and TAE adapters are implemented without peer SQL bypass from APR.
- Exact/Covered/Partial/Ambiguous/Unresolved/Unknown have core/adapter-level executable cases.
- Predicate-disjoint unsupported DCS material does not poison a result.
- Relevant missing RC realization and unsupported ACC transport produce Unknown.
- TAE action/time facts stay provenance; asOf is explicit.

## Blockers

None for WP3.

## Gate

WP3 passes only when PostgreSQL-backed proof demonstrates:
- durable TAE record/readback projects into APR;
- current effective ACC bindings + RC realizations produce Exact;
- effective-time change changes resolution through RC/ACC truth rather than stale reuse;
- a second distinct DCS with the same technical region produces Ambiguous with no winner;
- resolution creates no Access Rule or Connectivity Decision;
- evidence remains durable and unchanged;
- existing unit examples collectively cover Covered/Partial/Unresolved/Unknown.

## Next

Add and review the durable integration proof. Open WP4 only after no P0/P1 integration finding remains.
