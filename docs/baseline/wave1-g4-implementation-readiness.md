# Wave-1 G4 — Implementation readiness

Status: `G4 PASS`.

Date: 2026-09-08.

## Selected first production-code path

`Submit valid proposal -> authority/catalogue ports -> exact Allowed decision port -> Access Policy materialize-or-resolve -> transactional unique Rule -> return RuleId + Active`, with idempotent/concurrent duplicate proof.

## Historical G4 artifacts

The detailed PLAN-028 walking-skeleton/readiness packets were absorbed into durable domain, requirements, architecture, code and executable evidence and are no longer retained as working-tree execution documents. Git history is the archive for those packets.

Durable successors include:
- `docs/domain/access-policy/tactical-model.md`;
- `docs/requirements/wave1-product-requirements.md`;
- `docs/requirements/wave1-semantic-contracts.md`;
- `docs/decisions/ADR-001-wave1-modular-application.md`;
- `docs/decisions/ADR-002-wave1-coherent-export-snapshot.md`;
- current implementation and executable evidence under `src/` and `tests/`.

## Readiness challenge

| Finding | Severity | Result |
|---|---|---|
| Would code need to invent Rule identity/materialization semantics? | P1 | CLOSED — G2 + tactical model |
| Would code need to invent architecture topology/module ownership? | P1 | CLOSED — G3/ADR-001 |
| Would code need to invent decision-domain workflow? | P1 | CLOSED — external port/fake/manual adapter only |
| Is concurrency/idempotency mechanism sufficiently constrained? | P1 | CLOSED — authoritative unique tuple + transaction/conflict resolution contract; exact SQL mechanism implementation-local |
| Are first-slice acceptance/security behaviors explicit? | P1 | CLOSED — acceptance pack + threat model |
| Is build/test/run path available? | P1 | CLOSED — existing Python/FastAPI scaffolding reused only as tooling; target package semantics replaced |
| Would first deployment require Legacy migration/cutover? | P1 | NO — isolated coexistence skeleton first |
| Exact deployment DB vendor not selected | P2 | NOT BLOCKING — relational transactional semantics fixed; choose simplest supported engine and validate concurrency against production engine |
| Exact auth/catalogue/decision production providers unknown | P2 | NOT BLOCKING for skeleton — real ports + fake/manual adapters explicitly selected; real integration is later backlog I7 |
| Numeric SLA/workload absent | P3 | accepted pending evidence |
| Exact lint/type/secret/deploy platform choices | P3 | implementation-local; must be added before corresponding production environment, not semantic blockers |

Open/unaccepted P0/P1 findings: `none`.

## G4 completion check

- Walking Skeleton selected: PASS;
- actor outcome/examples clear: PASS;
- Tactical DDD consistency rules defined: PASS;
- implementation ports/data/error/concurrency contracts implementable: PASS;
- acceptance/integration checks identified: PASS;
- engineering build/test/run/observe path defined: PASS;
- threat mitigations actionable: PASS;
- transition/rollback explicit: PASS;
- ordered vertical backlog established: PASS;
- code would need to invent product/architecture semantics: NO.

## Decision

`G4 PASS` — production code may begin with backlog increment I1. Any implementation discovery that contradicts accepted G2/G3 semantics must reopen the owning decision rather than silently changing behavior in code.