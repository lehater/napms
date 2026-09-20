# Backend implementation completion criteria

Status: ACCEPTED candidate

Depends on: `implementation-design.md`.

The IMPLEMENTATION consumer may claim realization complete only when all of the following are true:

1. Every HTTP operation and operation-to-permission mapping in the accepted contracts is implemented.
2. Every accepted domain invariant and application consistency rule is enforced by its owning component.
3. PostgreSQL schema and ordered migrations realize Persistence Design, including optimistic concurrency, immutable/final decision constraints, idempotency and history.
4. Cross-owner validation uses the accepted shared transaction snapshot without peer writes.
5. CurrentPolicyMaterializer cannot return COMPLETE while any active Rule lacks required current realization/communication facts.
6. Normalized rows preserve exact traffic semantics and independent provenance.
7. Authentication, fail-closed permission checks, secret handling and security-analysis obligations are proven.
8. Operability contracts for structured diagnostic evidence, readiness/liveness, timeout/cancellation and redaction are proven.
9. Architecture/component dependency checks prove the intended module/adapter direction.
10. Every accepted Test Design contract has executable evidence at the appropriate domain/application/integration/API/security/operability level.
11. All migrations can initialize an empty PostgreSQL database and the full acceptance journey succeeds using only public HTTP plus configured identity infrastructure; no manual database state fabrication is required.
12. No source code/test has introduced a new product/domain/architecture/interface/data/security semantic convention that is absent from accepted design.

Any failed item is implementation/evidence work unless it exposes a genuine upstream semantic gap; such a gap must be routed to its owning Authority as a Question.
