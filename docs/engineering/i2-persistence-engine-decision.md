# I2 persistence engine decision

Status: `owner decision required`

Date: 2026-09-08.

## Decision question

Which relational database engine is the production proof target for I2 Access Policy persistence?

The chosen engine must be credible for the intended deployment because I2 claims concurrency, uniqueness and rollback guarantees against the selected production-grade mechanism.

## Known constraints

Accepted/known:

- Access Policy requires one authoritative Rule per `RuleSemanticIdentity`;
- materialization must preserve that invariant under retries and concurrent transactions;
- false success after rollback/uncertain persistence outcome is prohibited;
- a local transaction boundary is preferred while distribution is unjustified;
- one physical database may host multiple module-owned datasets;
- Python >=3.10 is the current runtime;
- hosted CI currently runs on `ubuntu-latest`;
- no relational driver/ORM/database dependency is currently selected;
- no numeric workload/SLA requires a specialized database topology.

Unknown:

- target production platform;
- organization-supported database products;
- managed-service availability;
- operational ownership/backup/HA standards;
- whether PostgreSQL is permitted in the intended deployment.

These unknowns are deployment facts, not Access Policy semantics.

## Alternatives

### A — PostgreSQL

Recommendation: **preferred if supported by the intended deployment**.

Why:

- strong transactional unique constraints directly fit the authoritative semantic-identity invariant;
- standard concurrent insert/conflict behavior supports winner resolution without inventing application semantics;
- mature Python driver support;
- straightforward Linux/GitHub Actions integration-test execution;
- low implementation complexity for the current modular application;
- no repository evidence favors another engine.

Consequence:

- I2 can prove the required invariant using a unique constraint over
  `source_component_deployment_id + destination_component_deployment_id + dcs_contract_revision_id`;
- retry/conflict tests must resolve the authoritative committed row;
- transaction error mapping remains adapter-owned.

Risk:

- selecting PostgreSQL without confirming deployment support would turn an unknown environment assumption into target architecture.

### B — SQL Server

Use when it is an explicit platform/operations constraint.

Strengths:

- production-grade transactions and unique constraints satisfy the same semantic requirement;
- common enterprise operational support.

Costs for this repository:

- additional ODBC/driver/runtime setup;
- heavier Linux CI integration;
- no current evidence that this complexity is required.

The implementation should rely on ordinary transaction + unique-constraint behavior rather than make database-specific merge semantics part of the domain contract.

### C — MySQL/MariaDB

Technically viable if explicitly supported by the deployment environment.

There is no current repository evidence that prefers it over PostgreSQL, so selecting it now would be arbitrary.

### D — SQLite

Rejected as the final I2 proof engine.

Reason:

- useful for local/unit persistence experiments, but its locking/concurrency model would not establish the production concurrency guarantee required by I2 for a normal multi-process/server deployment;
- an SQLite-only PASS would overstate evidence.

## Recommendation

Choose **PostgreSQL** if the target environment supports it.

This is the simplest option aligned with current architecture drivers and CI mechanics, while preserving a conventional relational transaction/unique-constraint implementation.

## Owner decision required

Accept one of:

1. `PostgreSQL is supported/approved for the NAPMS production target` — proceed with PostgreSQL I2 implementation;
2. `PostgreSQL is not the target; use <supported relational engine>` — implement against that engine;
3. production database support is still genuinely undecided — keep I2 adapter implementation blocked.

## Revisit trigger

Revisit the engine choice if the actual deployment platform cannot run/support the selected engine, or if a production constraint invalidates the transaction/concurrency mechanism used by the I2 proof.
