# Wave-1 Walking Skeleton — implementation staging

Status: `selected D2 implementation slice — domain/application-first`.

Date: 2026-09-08.

## Selected first stage — I1

Implement and exhaustively test the business/application path **without real infrastructure**:

```text
submit one structurally valid Access Rule Proposal
 -> AuthorityPort fake
 -> ApplicationCommunicationCataloguePort fake
 -> ConnectivityDecisionPort fake = Allowed|NotAllowed|Unknown/mismatch
 -> Access Policy materialize-or-resolve
 -> AccessRuleRepository port + in-memory fake
 -> application result
```

I1 exists to validate the internal application shape, Tactical DDD model, use-case orchestration, ports and all accepted positive/negative business behavior before database/framework/external-integration mechanics can influence the model.

## I1 dependency policy

| Dependency | I1 classification | Rule |
|---|---|---|
| Access Policy domain | **real** | full first-slice domain model/invariants |
| application/use-case orchestration | **real** | full first-slice behavior |
| ports | **real contracts** | defined from application/domain needs |
| AccessRuleRepository | **in-memory fake behind port** | no SQL/ORM/migrations/database in I1 |
| Authority Management | **fake behind port** | cover permitted/denied/unknown |
| Application Communication Catalogue | **fake behind port** | cover valid/invalid/unknown interaction |
| Connectivity Decision | **fake behind port** | cover Allowed/NotAllowed/Unknown/mismatch |
| HTTP/FastAPI | **not required for I1 gate** | adapter added after core passes |
| Resource Catalogue/export/Legacy | not in I1 | later increments |

## I1 must prove before infrastructure is allowed

- exact semantic identity value semantics and immutability;
- Allowed creates/resolves one Active Rule in the application model;
- repeated Allowed is idempotent at the repository-port contract level;
- NotAllowed creates no Rule;
- decision subject mismatch fails closed;
- authority denied/unknown prevents downstream decision/materialization;
- invalid/unknown described interaction prevents decision/materialization;
- dependency Unknown/Unavailable is not silently converted to permission or business denial;
- failure paths leave no forbidden domain/application side effects;
- provenance required by the first slice is preserved;
- domain/application packages depend on no FastAPI, ORM, SQL driver, database schema or external SDK;
- tests cover the accepted state/decision/authority/structural combinations for I1.

## Important limit of I1

An in-memory repository can validate the **semantic repository contract** and deterministic idempotency behavior, but it cannot prove production concurrency/transaction guarantees. The requirement remains fixed: one `RuleSemanticIdentity` -> at most one authoritative `AccessRule`. Its technical enforcement under concurrent processes is proved only in I2 against the real persistence adapter/database.

## Infrastructure gate

**No real infrastructure implementation begins until I1 Domain + Application + Ports tests are green and the model review finds no open P0/P1 semantic/structural issue.**

Only then I2 may introduce persistence/HTTP/external adapters and integration tests without changing accepted domain semantics. If infrastructure pressure appears to require a semantic change, reopen the owning domain/application decision rather than bending the model inside an adapter.