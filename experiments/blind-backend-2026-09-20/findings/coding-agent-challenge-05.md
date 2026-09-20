# Coding-Agent Challenge 05

Status: FAILED — materialization response-commit semantics require repair

## CAC-011 — P1 — streaming export vs dependency-failure HTTP semantics

Accepted contracts simultaneously require:

- materialization can stream a potentially large export without buffering the whole row set;
- COMPLETE/UNRESOLVED are successful computation outcomes using HTTP 200;
- dependency/runtime failure preventing evaluation is HTTP 503, not UNRESOLVED;
- all facts come from one coherent database snapshot.

If implementation starts a 200 response and streams rows while still discovering required facts, a later database/dependency failure can no longer become HTTP 503. The coding agent would have to invent response-commit behavior.

## Required repair

CurrentPolicyMaterializer uses two phases inside one REPEATABLE READ (or stronger) read-only snapshot:

### Phase 1 — preflight

- page/chunk every selected Rule and required Need/Interaction/Deployment/Resource facts;
- evaluate effective/non-effective state;
- determine every semantic MaterializationIssue;
- verify all database/dependency reads needed for the result can be completed;
- compute status COMPLETE/UNRESOLVED and compact counts;
- do not write HTTP response headers/body yet;
- do not buffer full normalized rows.

If preflight has dependency/runtime failure, abort transaction and return 503 before response commitment.

### Phase 2 — emit

Using the same still-open snapshot:
- repeat bounded/chunked fact traversal;
- emit the already-determined COMPLETE/UNRESOLVED response incrementally;
- stream rows/nonEffective/issues without holding complete export in memory.

If transport/client cancellation or an unexpected infrastructure failure occurs after response commitment, the HTTP body is incomplete/truncated and is **not** a valid successful export artifact. It must never be converted to a syntactically complete COMPLETE response.

No product semantic is changed; this closes interface/reliability realization semantics required by existing contracts.
