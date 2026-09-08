# PLAN-003 — I3 operational state mutation

Status: `active`

## Goal

Implement authorized `AccessRule Active <-> Inactive` mutation as Access Policy domain behavior with attributable business audit/provenance, preserving Rule identity and Connectivity Decision correlation, then adapt PostgreSQL persistence only after the core behavior passes.

## Current stage

I3 semantic refinement reached one cross-context authority-scope decision gate before code. Existing canon already fixes the command `SetRuleOperationalState(ruleId, Active|Inactive)`, valid cross-state transitions and minimum attributable audit intent, but the Rule-to-Authority-Scope binding for later mutation is not explicit.

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

## Refinement findings

Evidence-supported I3 interpretation:

1. `SetRuleOperationalState` is the stable semantic command/action name already accepted by F2.
2. F2 permits only a valid `Active <-> Inactive` transition; requesting the already-current state therefore produces no accepted transition and no audit record. The application should expose this as an explicit expected non-success such as `AlreadyInRequestedState`, not manufacture a transition.
3. QS-07 fixes the minimum audit meaning as who/when/what. Combined with QS-06 and F2, an accepted transition must retain RuleId, from/to state, actor, effective action time, evaluated authority scope and authority provenance/reference. A separate technical log timestamp is not domain truth.

### P1 authority-scope binding

F2 intentionally accepts only `ruleId + targetState` from the actor; it does not accept caller-supplied authority scope. T1 requires action/scope/effective-time authority at the use-case boundary.

The current model stores the proposal's accepted `authority_scope` in Rule proposal provenance, but canon does not yet state whether that scope is also the stable governance scope for later Rule mutations.

Rejected implementation shortcuts:

- caller supplies mutation scope — P1 authorization-substitution risk because the application cannot prove it governs this Rule;
- silently reinterpret a historical provenance field as current governance scope — unsupported semantic promotion;
- dynamically derive scope from current resource/application ownership — adds unaccepted cross-context scope-resolution semantics.

Recommended minimal decision:

> The accepted proposal `authority_scope` becomes the stable governance scope of the materialized AccessRule. Later actions such as `SetRuleOperationalState` evaluate current/effective Authority Management assignments for the same Rule governance scope. Actor assignments may change over time; the governance-scope identity does not silently change with ownership/responsibility changes.

This is non-identity Rule governance metadata: changing authority assignments does not change RuleId, RuleSemanticIdentity or Connectivity Decision coverage.

## Blockers

P1 owner decision required: accept or reject the recommended stable Rule governance-scope semantics above before Tactical DDD/code implementation.

## Validation

- core candidate: `make test`;
- PostgreSQL persistence adaptation: `make postgres-test`;
- harness/process changes: `make harness-check`;
- living DDD changes: `make knowledge-check`;
- final multi-area candidate: `make check` plus `make postgres-test`.

## Next

I4 — effective desired-policy selection for a logical `as-of`, including supported declarative effective conditions.
