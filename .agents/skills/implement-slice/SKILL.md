---
name: implement-slice
description: "Use for implementing or changing one NAPMS vertical/domain application slice from accepted behavior through Domain/Application/Ports and executable tests. Enforce core-first dependency rules and the active infrastructure gate. Route upstream semantic changes to domain-model-change and architecture conflicts to architecture-review."
---

# Implement Slice

Use this Skill only after the applicable `S4 Implementation Readiness` / G4 gate has authorized the slice. `docs/process/implementation-readiness-stage.md` owns pre-code impact/slicing/readiness; this Skill executes the accepted slice.

## Inputs

- active plan/capsule selecting a G4-accepted slice;
- relevant accepted requirements/semantic contracts;
- relevant Tactical DDD/ADRs/architecture constraints;
- current code/tests.

## Procedure

1. Confirm G4 authorized the requested implementation scope and required checks are known.
2. Confirm the requested behavior is already accepted at the required semantic level.
3. If implementation would change product behavior/quality expectations, use `REOPEN(S1)` rather than deciding it locally.
4. If implementation would change semantic identity, lifecycle, invariant, ownership or Bounded Context responsibility/contract, use `REOPEN(S2)` through the domain-change workflow.
5. If implementation exposes missing responsibility placement, data ownership, dependency direction or consistency architecture, use `REOPEN(S3)` rather than improvising locally.
6. Implement inside-out:
   ```text
   Domain -> Application + consuming Ports -> tests -> adapters only when active gate permits
   ```
7. Preserve fail-closed behavior, identity invariants and explicit outcomes.
8. Add/adjust tests before claiming behavior is complete.
9. Run the relevant local checks (`make test` at minimum for core changes).
10. Review dependency direction and claims-vs-evidence.
11. Classify material findings P0-P3; do not close the slice with P0/P1 open.

## Guardrails

No framework/DB/transport/config/logging/DI-container dependency in Domain. Infrastructure may not be introduced to compensate for unclear core semantics.

Implementation evidence may invalidate an accepted upstream guarantee; when that happens, persist the finding and reopen the single owning lifecycle stage instead of patching around it.
