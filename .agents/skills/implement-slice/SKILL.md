---
name: implement-slice
description: "Use for implementing or changing one NAPMS vertical/domain application slice from accepted behavior through Domain/Application/Ports and executable tests. Enforce core-first dependency rules and the active infrastructure gate. Route upstream semantic changes to domain-model-change and architecture conflicts to architecture-review."
---

# Implement Slice

Use this Skill only after the applicable `S4 Implementation Readiness` / G4 gate has authorized the exact slice. `docs/process/implementation-readiness-stage.md` owns pre-code impact/slicing/readiness; this Skill executes the accepted slice.

## Inputs

- active capsule with `Lifecycle stage: IMPLEMENTATION`;
- `Implementation authorization: G4 PASS`;
- non-`none` `Authorized scope` matching the requested slice;
- non-`none` `Authorization basis` identifying the applicable G4/upstream guarantees;
- relevant accepted requirements/semantic contracts;
- relevant Tactical DDD/ADRs/architecture constraints;
- current code/tests.

## Procedure

1. Confirm the capsule carries a current scoped G4 implementation lease.
2. Confirm the requested code work is inside `Authorized scope`; authorization for a different slice is not reusable.
3. Confirm the `Authorization basis` still points to applicable/non-dirty upstream guarantees. If it is missing, stale or ambiguous, return to S4/gate evaluation instead of assuming permission.
4. Confirm the requested behavior is already accepted at the required semantic level.
5. If implementation would change product behavior/quality expectations, revoke the affected implementation lease and use `REOPEN(S1)` rather than deciding it locally.
6. If implementation would change semantic identity, lifecycle, invariant, ownership or Bounded Context responsibility/contract, revoke the affected implementation lease and use `REOPEN(S2)` through the domain-change workflow.
7. If implementation exposes missing responsibility placement, data ownership, dependency direction or consistency architecture, revoke the affected implementation lease and use `REOPEN(S3)` rather than improvising locally.
8. Implement inside-out:
   ```text
   Domain -> Application + consuming Ports -> tests -> adapters only when active gate permits
   ```
9. Preserve fail-closed behavior, identity invariants and explicit outcomes.
10. Add/adjust tests before claiming behavior is complete.
11. Run the relevant local checks (`make test` at minimum for core changes).
12. Review dependency direction and claims-vs-evidence.
13. Classify material findings P0-P3; do not close the slice with P0/P1 open.

## Guardrails

No framework/DB/transport/config/logging/DI-container dependency in Domain. Infrastructure may not be introduced to compensate for unclear core semantics.

Implementation evidence may invalidate an accepted upstream guarantee; when that happens, persist the finding, revoke the affected G4 lease and reopen the single owning lifecycle stage instead of patching around it.
