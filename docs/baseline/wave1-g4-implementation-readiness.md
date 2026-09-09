# Wave-1 G4 — Implementation readiness

Status: `G4 PASS — historical accepted snapshot`.

Date: 2026-09-08.

## Selected first production-code path

`Submit valid proposal -> authority/catalogue ports -> exact Allowed decision port -> Access Policy materialize-or-resolve -> transactional unique Rule -> return RuleId + Active`, with idempotent/concurrent duplicate proof.

## Historical G4 artifacts

Detailed PLAN-028 walking-skeleton/readiness packets and the later Wave-1 working requirement/architecture packets were absorbed into current product/domain/architecture truth, code and executable evidence. Git history is the archive for those packets.

Durable current successors include:
- `docs/requirements/access-policy-core.md`;
- `docs/requirements/policy-export-core.md`;
- `docs/domain/access-policy/tactical-model.md`;
- `docs/architecture/current-architecture.md`;
- ADR-001 / ADR-002 / ADR-005;
- current implementation and executable evidence under `src/` and `tests/`.

The original G4 Decision-provider assumption was intentionally minimal; ADR-005 supersedes it for current target semantics.

## Readiness challenge

| Finding | Severity | Historical result |
|---|---|---|
| Would code need to invent Rule identity/materialization semantics? | P1 | CLOSED |
| Would code need to invent architecture topology/module ownership? | P1 | CLOSED |
| Would first slice require invented Decision workflow? | P1 | CLOSED by the then-selected minimal port |
| Is concurrency/idempotency sufficiently constrained? | P1 | CLOSED |
| Are first-slice acceptance/security behaviors explicit? | P1 | CLOSED |
| Would first deployment require Legacy migration/cutover? | P1 | NO |
| Numeric SLA/workload absent | P3 | accepted pending evidence |

Open/unaccepted P0/P1 findings at G4: `none`.

## Decision

`G4 PASS` — production code could begin with I1.

Current implementation discoveries must follow current requirements/DDD/architecture rather than this historical readiness snapshot.
