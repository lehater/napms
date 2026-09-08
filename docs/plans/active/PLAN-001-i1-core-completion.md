# PLAN-001 — I1 core completion

Status: `active`

## Goal

Close I1 with a proven Access Policy Domain/Application/Ports core and no open P0/P1 semantic or architecture issue, without introducing production infrastructure.

## Current stage

Final core/model/architecture review after the migrated core test suite first passed in GitHub Actions.

## Inputs

Canonical inputs for this plan:

- `docs/requirements/wave1-product-requirements.md`;
- `docs/requirements/wave1-acceptance-examples.md`;
- `docs/requirements/wave1-semantic-contracts.md`;
- `docs/domain/strategic-model.md` + `strategic-model.json`;
- `docs/domain/access-policy/tactical-model.md`;
- `docs/engineering/walking-skeleton-implementation-contracts.md`;
- `docs/engineering/walking-skeleton-acceptance-pack.md`;
- `docs/engineering/error-model.md`;
- `docs/engineering/observability.md`;
- `docs/engineering/configuration.md`;
- `docs/engineering/dependency-injection.md`;
- `src/napms/access_policy/` and the corresponding tests.

## Work packages

1. Review remaining Authority/Catalogue/Decision/Repository contracts against accepted G4 semantics.
2. Expand/fix core and architecture tests for material findings.
3. Classify findings P0-P3 and close all P0/P1.
4. Run the complete core gate on the exact candidate state.
5. Record I1 PASS only when the exit criteria are met.

## Exit criteria

- all Domain/Application/architecture tests green;
- accepted first-slice behavior matrix covered;
- no framework/infrastructure dependency in core;
- no open P0/P1 model/application/port issue;
- implementation claims do not exceed test evidence;
- I1 result recorded in canonical engineering state.

## Blockers

None currently known. Any newly discovered material semantic unknown keeps I1 open until resolved or explicitly accepted as non-blocking with a revisit trigger.

## Infrastructure prohibition

Until I1 PASS, do not add production DB/ORM/migrations, HTTP/FastAPI wiring, real external adapters or infrastructure mechanisms that shape unclear core semantics.

## Validation

- core candidate: `make test`;
- harness/process changes: `make harness-check`;
- living DDD changes: `make knowledge-check`;
- final repository candidate when several areas changed: `make check`.

## Next

I2 — infrastructure proof: relational repository/UoW, authoritative uniqueness/concurrency/rollback proof, then transport/external adapters as accepted by the next plan.
