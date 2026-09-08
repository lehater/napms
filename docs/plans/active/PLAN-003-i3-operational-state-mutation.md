# PLAN-003 — I3 operational state mutation

Status: `active`

## Goal

Implement authorized `AccessRule Active <-> Inactive` mutation as Access Policy domain behavior with attributable business audit/provenance, preserving Rule identity and Connectivity Decision correlation, then adapt PostgreSQL persistence only after the core behavior passes.

## Current stage

Refine the I3 Tactical DDD/application contract from the already accepted Wave-1 behavior before implementation. The architecture flow is `SetRuleOperationalState(ruleId, Active|Inactive)`, but exact same-state behavior, mutation authority action identity and minimum audit-record shape must be made explicit rather than invented in code.

## Inputs

Canonical inputs for this plan:

- `docs/requirements/wave1-product-requirements.md` — REQ-W1-005;
- `docs/requirements/wave1-acceptance-examples.md` — E7;
- `docs/requirements/wave1-quality-scenarios.md` — QS-07;
- `docs/requirements/wave1-semantic-contracts.md` — C5;
- `docs/domain/access-policy/tactical-model.md`;
- `docs/domain/ubiquitous-language.md`;
- `docs/architecture/wave1-domain-message-flows.md` — F2;
- `docs/architecture/wave1-data-ownership.md`;
- `docs/architecture/wave1-threat-model.md`;
- `docs/engineering/error-model.md`;
- `docs/engineering/dependency-injection.md`;
- `docs/engineering/observability.md`;
- current Access Policy core, PostgreSQL adapter and tests.

## Accepted behavior already fixed

- Access Rule operational state is exactly `Active | Inactive` in Wave 1;
- first Allowed materialization starts `Active`;
- state mutation preserves RuleId, RuleSemanticIdentity and Connectivity Decision coverage;
- `Inactive` preserves Rule/history but removes desired effect;
- state mutation does not require a new Connectivity Decision solely because of the transition;
- mutation requires effective Authority Management permission for action/scope/effective time;
- every accepted state transition is attributable and auditable at business level;
- business audit/provenance is domain truth, not an operational log.

## Work packages

1. Refine Tactical DDD for the state transition, including valid transition semantics and minimum attributable temporal audit/provenance.
2. Fix the application command/result and exact mutation-authority port action without inventing Authority Management internals.
3. Implement Domain/Application/Ports behavior and exhaustive relevant core tests.
4. Close all P0/P1 core/model/architecture findings and pass the core gate.
5. Adapt PostgreSQL persistence for state mutation and durable audit/provenance.
6. Add PostgreSQL integration proof for transactionality, identity/decision preservation and rollback/no-false-success behavior.
7. Run the final repository gates and record I3 PASS only when all exit criteria are met.

## Exit criteria

- accepted `Active -> Inactive` and `Inactive -> Active` behavior is explicit and executable;
- same-state request behavior is explicitly decided and tested;
- denied/unknown mutation authority fails closed with no Rule/audit mutation;
- successful mutation preserves RuleId, semantic identity and decision correlation;
- successful mutation produces attributable temporal business audit/provenance;
- failed persistence cannot report successful mutation;
- core behavior remains infrastructure-independent;
- PostgreSQL adapter preserves the accepted behavior transactionally;
- all relevant core and PostgreSQL integration tests are green;
- no open P0/P1 semantic, audit, authority, transaction or architecture issue;
- I3 result is recorded in canonical engineering state.

## Blockers

Three bounded I3 details require explicit refinement before code:

1. whether requesting the already-current operational state is an idempotent no-op or a rejected invalid transition;
2. the stable AuthorityAction identity used for Rule operational-state mutation;
3. the minimum domain audit-record fields/timestamp semantics for an accepted transition.

These are I3 Tactical/Application details, not reasons to reopen I1/I2.

## Validation

- core candidate: `make test`;
- PostgreSQL persistence adaptation: `make postgres-test`;
- harness/process changes: `make harness-check`;
- living DDD changes: `make knowledge-check`;
- final multi-area candidate: `make check` plus `make postgres-test`.

## Next

I4 — effective desired-policy selection for a logical `as-of`, including supported declarative effective conditions.
