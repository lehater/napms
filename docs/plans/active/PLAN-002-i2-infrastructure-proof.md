# PLAN-002 — I2 infrastructure proof

Status: `active`

## Goal

Prove that a real relational AccessRuleRepository/UnitOfWork preserves the already accepted Access Policy semantics under production-grade transaction, uniqueness, retry and rollback behavior, without redefining Rule identity or application outcomes.

## Current stage

Select the simplest production-grade relational engine supported by the intended deployment and define the persistence adapter/integration-test harness. No persistence implementation should start by weakening or reshaping the accepted core contract.

## Inputs

Canonical inputs for this plan:

- `docs/requirements/wave1-product-requirements.md`;
- `docs/requirements/wave1-acceptance-examples.md`;
- `docs/requirements/wave1-semantic-contracts.md`;
- `docs/domain/access-policy/tactical-model.md`;
- `docs/architecture/wave1-data-ownership.md`;
- `docs/architecture/wave1-threat-model.md`;
- `docs/decisions/ADR-001-wave1-modular-application.md`;
- `docs/engineering/walking-skeleton-implementation-contracts.md`;
- `docs/engineering/walking-skeleton-acceptance-pack.md`;
- `docs/engineering/error-model.md`;
- `docs/engineering/configuration.md`;
- `docs/engineering/dependency-injection.md`;
- `src/napms/access_policy/` and corresponding core tests.

## Decision constraint

The database/vendor remains an engineering choice. Select it only from known deployment/support constraints; do not invent a production environment merely to unblock implementation.

If those constraints are unavailable, keep the choice explicit as an unknown and resolve it through `docs/process/decision-protocol.md`.

## Work packages

1. Select/record the relational engine and transaction mechanism used for the production proof.
2. Implement the Access Policy persistence adapter/UoW, schema and migrations behind the accepted ports.
3. Prove authoritative uniqueness for `RuleSemanticIdentity` under concurrent identical Allowed materializations.
4. Prove conflict/retry resolution returns the same authoritative RuleId.
5. Prove rollback/uncertain persistence outcomes are never reported as successful materialization unless the authoritative Rule is resolved.
6. Re-run the core gate unchanged, then run persistence integration tests on the exact candidate.
7. Record I2 PASS only when all exit criteria are met.

HTTP is not required for the persistence proof. Add a transport adapter in I2 only if a concrete acceptance/integration need appears and the active plan is updated before implementation.

## Exit criteria

- all I1 Domain/Application/architecture tests remain green;
- real relational repository/UoW implements the accepted port semantics without core dependency reversal;
- schema/migrations enforce the authoritative semantic-identity uniqueness invariant;
- concurrent identical Allowed materialization proves one authoritative Rule and one resolved RuleId;
- uniqueness race/retry behavior is deterministic and tested;
- rollback/uncertain persistence failure cannot produce false success;
- persistence integration tests run against the selected production-grade engine/mechanism;
- no open P0/P1 semantic, ownership, transaction or architecture issue;
- I2 result is recorded in canonical engineering state.

## Blockers

The production-grade relational engine/deployment support constraint is not yet recorded in this repository. This is an engineering choice to resolve before adapter implementation; it does not reopen I1 semantics.

## Validation

- unchanged core semantics: `make test`;
- harness/process changes: `make harness-check`;
- living DDD changes, if any become necessary: `make knowledge-check`;
- final multi-area candidate: `make check`;
- persistence integration command: define as part of the selected engine/test harness before implementation is considered complete.

## Next

I3 — authorized Access Rule `Active <-> Inactive` behavior, first through Domain/Application/Ports/tests and only then through persistence adaptation.
