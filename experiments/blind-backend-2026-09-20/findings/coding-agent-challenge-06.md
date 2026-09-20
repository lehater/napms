# Coding-Agent Challenge 06

Status: FAILED — transaction consistency/failure semantics require repair

## CAC-012 — P1 — mutable Need validation transaction semantics underspecified

SubmitAccessRequest and AttachPolicyRuleJustification depend on ConnectivityNeed being current while Access Policy state commits.

The design said validation occurs in the same transaction/snapshot, but did not select a PostgreSQL realization. READ COMMITTED has statement snapshots; REPEATABLE READ introduces different write-conflict behavior. A coding agent would have to choose a material consistency rule.

### Repair decision

Use an owner-provided **current-Need validation lock** inside one PostgreSQL READ COMMITTED Access Policy write transaction:

- Business Connectivity read adapter resolves the Need and acquires a row-level share/key-share lock sufficient to block Need retirement/update until the Access Policy transaction ends;
- the Access Policy transaction never writes Business Connectivity tables;
- after the lock is acquired, currentness/Interaction/participant facts are stable through Access Policy commit;
- if Need retirement acquired/committed its update first, validation observes RETIRED and rejects;
- if request/attachment acquires the validation lock first, retirement waits and the Access Policy mutation commits against a Need that remained current through commit;
- lock wait is bounded by request/DB timeout.

This makes the source requirement “current at submission/attachment” stronger and deterministic without distributed transactions or peer writes.

Other immutable peer references need no cross-owner lock.

Composite read-only Rule views/materialization use read-only REPEATABLE READ snapshots for coherent multi-owner reads.

## CAC-013 — P1 — unresolved concurrent Idempotency-Key timeout outcome

For a second request using the same scoped idempotency key while the first transaction is unresolved, the design allowed “bounded failure” but did not specify the public result.

### Repair decision

- second request waits only within configured DB/request deadline for the idempotency row/unique-key transaction to resolve;
- if first commits -> replay;
- if first rolls back -> second proceeds as NEW and then evaluates If-Match;
- if resolution cannot be established before timeout or DB availability fails -> `503 DEPENDENCY_UNAVAILABLE`;
- never return 409 merely because the identical command is still in progress;
- never fabricate success.

Freeze remains prohibited until Data/Component/Application/API/Operability/Test/Implementation encode these decisions and Challenge 07 passes.
