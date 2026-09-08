---
name: implement-slice
description: "Use for implementing or changing one NAPMS vertical/domain application slice from accepted behavior through Domain/Application/Ports and executable tests. Enforce core-first dependency rules and the active infrastructure gate. Route upstream semantic changes to domain-model-change and architecture conflicts to architecture-review."
---

# Implement Slice

## Inputs

- active plan and local exit;
- relevant accepted requirements/semantic contracts;
- relevant Tactical DDD/ADRs;
- current code/tests.

## Procedure

1. Confirm the requested behavior is already accepted at the required semantic level.
2. If implementation would change behavior, identity, lifecycle, ownership or BC responsibility, stop lower-layer invention and route through `domain-model-change`.
3. Implement inside-out:
   ```text
   Domain -> Application + consuming Ports -> tests -> adapters only when active gate permits
   ```
4. Preserve fail-closed behavior, identity invariants and explicit outcomes.
5. Add/adjust tests before claiming behavior is complete.
6. Run the relevant local checks (`make test` at minimum for core changes).
7. Review dependency direction and claims-vs-evidence.
8. Classify material findings P0-P3; do not close the slice with P0/P1 open.

## Guardrails

No framework/DB/transport/config/logging/DI-container dependency in Domain. Infrastructure may not be introduced to compensate for unclear core semantics.
