# PLAN-003 — I3 operational state mutation

Status: `active`

## Goal

Implement authorized `AccessRule Active <-> Inactive` mutation as Access Policy domain behavior with attributable business audit/provenance, preserving Rule identity and Connectivity Decision correlation, then adapt PostgreSQL persistence only after the core behavior passes.

## Current stage

I3 semantic refinement is accepted. `RuleGovernanceScope` is explicit: the accepted proposal authority scope becomes stable non-identity governance metadata of the materialized Rule, and later state mutation authority is evaluated against that stored scope. Next stage is Domain/Application/Ports implementation and core proof.

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

## Accepted behavior

- Access Rule operational state is exactly `Active | Inactive` in Wave 1;
- first Allowed materialization starts `Active`;
- accepted proposal `authority_scope` becomes stable non-identity `RuleGovernanceScope`;
- state mutation authority is evaluated against the Rule's stored governance scope, never caller-supplied scope;
- current/effective Authority Management assignments may change over time without silently rebinding Rule governance scope;
- state mutation preserves RuleId, RuleSemanticIdentity, RuleGovernanceScope and Connectivity Decision coverage;
- `Inactive` preserves Rule/history but removes desired effect;
- state mutation does not require a new Connectivity Decision solely because of the transition;
- same-state request is not an accepted transition and creates no transition audit;
- every accepted state transition is attributable and auditable at business level;
- minimum accepted transition audit is who/when/what plus evaluated governance scope and authority provenance;
- business audit/provenance is domain truth, not an operational log.

## Work packages

1. Implement Domain/Application/Ports behavior and exhaustive relevant core tests from the accepted refined Tactical DDD.
2. Close all P0/P1 core/model/architecture findings and pass the core gate.
3. Adapt PostgreSQL persistence for state mutation and durable audit/provenance.
4. Add PostgreSQL integration proof for transactionality, identity/decision/governance-scope preservation and rollback/no-false-success behavior.
5. Run the final repository gates and record I3 PASS only when all exit criteria are met.

## Exit criteria

- accepted `Active -> Inactive` and `Inactive -> Active` behavior is executable;
- same-state request returns explicit no accepted transition/no audit;
- denied/unknown mutation authority fails closed with no Rule/audit mutation;
- successful mutation preserves RuleId, semantic identity, governance scope and decision correlation;
- successful mutation produces attributable temporal business audit/provenance;
- caller cannot substitute authorization scope;
- failed persistence cannot report successful mutation;
- core behavior remains infrastructure-independent;
- PostgreSQL adapter preserves the accepted behavior transactionally;
- all relevant core and PostgreSQL integration tests are green;
- no open P0/P1 semantic, audit, authority, transaction or architecture issue;
- I3 result is recorded in canonical engineering state.

## Refinement decisions

1. `SetRuleOperationalState` is the stable semantic command/action already accepted by F2.
2. F2 permits only `Active <-> Inactive`; requesting the already-current state returns explicit `AlreadyInRequestedState`, is not an accepted transition and creates no audit record.
3. QS-07 + QS-06 define minimum transition audit as RuleId, from/to state, actor, effective action time, evaluated RuleGovernanceScope and authority provenance/reference.
4. The accepted proposal `authority_scope` becomes stable `RuleGovernanceScope` of the materialized AccessRule.
5. Later actions evaluate current/effective Authority Management assignments for that stored governance scope. Actor assignments may change over time; governance scope does not silently change with ownership/responsibility changes.

Rejected:
- caller-supplied mutation scope;
- implicit scope rebinding from current ownership/responsibility;
- treating historical authority assignment as current permission.

## Blockers

None currently known.

## Validation

- core candidate: `make test`;
- PostgreSQL persistence adaptation: `make postgres-test`;
- harness/process changes: `make harness-check`;
- living DDD changes: `make knowledge-check`;
- final multi-area candidate: `make check` plus `make postgres-test`.

## Next

I4 — effective desired-policy selection for a logical `as-of`, including supported declarative effective conditions.
