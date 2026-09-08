# I2 persistence engine decision

Status: `accepted`

Date: 2026-09-08.

## Decision

Use **PostgreSQL** as the production proof target for I2 Access Policy persistence.

The I2 proof will use ordinary relational transaction semantics plus an authoritative unique constraint over:

`source_component_deployment_id + destination_component_deployment_id + dcs_contract_revision_id`.

Database conflict/error mapping remains inside the persistence adapter. PostgreSQL-specific mechanisms must not leak into Domain/Application contracts.

## Why PostgreSQL

- strong transactional unique constraints directly fit the authoritative semantic-identity invariant;
- concurrent insert/conflict behavior supports authoritative winner resolution without redefining application semantics;
- mature Python driver support;
- straightforward Linux/GitHub Actions integration testing;
- low operational/implementation complexity for the selected modular application architecture;
- no accepted architecture driver requires a more specialized database choice.

## Transaction proof scope

I2 must prove:

1. one committed authoritative Rule per `RuleSemanticIdentity`;
2. concurrent identical Allowed materializations resolve one RuleId;
3. uniqueness conflict/retry resolves the authoritative committed winner;
4. rollback/uncertain persistence outcomes never become false materialization success;
5. load-by-RuleId and find-by-semantic-identity preserve the accepted Rule/provenance model.

The database is an enforcement mechanism for the accepted Access Policy invariant, not the source of its meaning.

## Rejected alternatives for this increment

### SQLite

Rejected as the final I2 proof engine because its locking/concurrency behavior would not establish the intended production multi-process transactional guarantee.

### SQL Server / MySQL / MariaDB

Technically viable but not selected. There is no accepted deployment constraint that justifies their additional divergence from the simplest current CI/runtime path.

## Revisit trigger

Revisit PostgreSQL only if an actual deployment/platform constraint prevents its supported use or invalidates the transaction/concurrency mechanism proven by I2.
