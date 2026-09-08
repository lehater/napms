# Current implementation state

Status: `I2 PASS — I3 operational-state core may begin under the active plan`.

Date: 2026-09-08.

Current execution is owned by `docs/plans/active/README.md`; do not mirror its work-package status here.

## Completed through I2

- accepted Wave-1 product/quality/acceptance baseline;
- accepted Strategic DDD baseline and Access Policy tactical model;
- accepted target architecture and ADRs;
- Access Policy Domain/Application/Ports executable core and I1 semantic/architecture proof;
- PostgreSQL selected as the I2 production persistence proof engine;
- operation-scoped PostgreSQL AccessRuleRepository/UoW adapter behind application-owned ports;
- SQL migration for the Access Policy dataset;
- authoritative unique constraint over `RuleSemanticIdentity`;
- persistence round-trip preserving Rule identity, decision correlation and proposal/authority/catalogue provenance;
- concurrent identical Allowed materialization resolves one authoritative RuleId;
- semantic-identity uniqueness races are translated and resolved without treating unrelated database uniqueness failures as idempotent retries;
- transaction rollback produces no authoritative Rule;
- failed/unknown commit acknowledgement produces no application success;
- PostgreSQL driver failures are translated to infrastructure-neutral port exceptions;
- core remains independent of PostgreSQL/framework/infrastructure imports;
- final I2 model/transaction/architecture review has no open P0/P1 finding;
- core, knowledge, harness and PostgreSQL persistence gates passed on the I2 implementation candidate.

## I2 result

`PASS`.

The production concurrency claim is now backed by executable PostgreSQL 16 integration evidence, not by the I1 in-memory repository.

The proof uses ordinary PostgreSQL transactions and an authoritative unique constraint; PostgreSQL-specific exception types remain inside the adapter.

## Current infrastructure boundary

Persistence for the Access Policy I1 materialization slice is admitted and proven.

HTTP and real Authority/Catalogue/Connectivity Decision adapters are still not implied by I2 and are introduced only when an active increment requires them.

Subsequent domain behavior continues inside-out: Domain/Application/Ports and core tests first, then adaptation of PostgreSQL persistence.
