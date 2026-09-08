# Walking Skeleton acceptance/test pack — PLAN-028 WP-04

Status: `accepted test-ready baseline — core gate before infrastructure`.

Date: 2026-09-08.

## I1 core test matrix — mandatory before infrastructure

All tests run through Domain/Application with real port contracts and in-memory/fake adapters.

1. **Allowed/new** — permitted + valid exact interaction + exact Allowed -> one Active Rule, created=true.
2. **Allowed/retry** — exact repeated subject -> same RuleId, created=false, repository contains one Rule.
3. **NotAllowed** — valid proposal + exact NotAllowed -> no Rule.
4. **Decision subject mismatch** -> reject/fail closed, no Rule.
5. **Authority denied** -> catalogue/decision/materialization not invoked beyond what orchestration requires; no Rule.
6. **Authority unknown/unavailable** -> no implicit permission; no Rule.
7. **Interaction invalid** -> no decision/materialization; no Rule.
8. **Interaction unknown/unavailable** -> no decision/materialization; no Rule.
9. **Decision unknown/unavailable** -> no Rule and explicit degraded/error result distinct from NotAllowed.
10. **Identity equality** — same Source/Destination/DCS revision is same semantic identity.
11. **Identity difference** — change Source OR Destination OR DCS revision yields a different subject; no silent rebinding.
12. **Identity immutability** — materialized Rule semantic identity cannot be mutated.
13. **Initial state** — first Allowed materialization is Active, never an approval/intermediate state.
14. **Provenance minimum** — Rule/result preserves exact decision correlation and required proposal/authority provenance.
15. **Failure side effects** — every rejected/unknown path leaves repository/domain state unchanged.
16. **Port ordering/short-circuit behavior** — denied/invalid prerequisites prevent unnecessary downstream decision/materialization calls.
17. **Core architecture independence** — Domain/Application import graph has no FastAPI, ORM, SQL driver, database adapter or external SDK dependency.
18. **Repository contract behavior** — in-memory implementation obeys find/add/idempotent semantic expectations used by application.

Where input types have validation boundaries, add equivalence/edge tests for missing/invalid identifiers and unsupported enum/result values at the appropriate core boundary. Do not inflate tests with meaningless permutations that cannot alter behavior; cover every semantically distinct branch and invariant.

## I1 gate

I1 passes only when:
- all core tests are green and deterministic;
- every accepted I1 behavior/invariant has executable coverage;
- no open/unaccepted P0/P1 Tactical DDD/application-structure finding remains;
- core code is infrastructure/framework independent.

**Passing I1 does not claim production concurrency safety.** In-memory execution cannot prove cross-process transactional uniqueness.

## I2 infrastructure tests — only after I1

After the core gate, add:
- persistence integration: unique semantic identity under real transaction semantics;
- concurrent identical Allowed materialization -> one authoritative Rule and same resolved RuleId;
- retry after uniqueness race/conflict;
- rollback/uncertain persistence outcome never reported as success unless authoritative Rule can be resolved;
- migrations/schema constraints;
- HTTP adapter acceptance/error mapping if HTTP is selected for the increment;
- real adapter contract tests for each external integration when introduced.

## Trace

Core tests prove G2 Allowed/NotAllowed/idempotency/identity behavior, QS-01/QS-02/QS-06 and threats T1/T2/T3/T9 at the domain/application boundary. I2 separately proves that chosen infrastructure preserves those semantics under real technical failure/concurrency conditions.

## Security assertions

- caller-supplied permission/decision flags are never trusted as substitutes for ports;
- decision subject is compared to canonical proposal identity;
- unauthorized/unknown actions fail closed;
- diagnostic errors do not expose unrelated policy/catalogue data.