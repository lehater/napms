---
name: implement-slice
description: "Use for implementing or changing one NAPMS vertical/domain application slice from accepted behavior through Domain/Application/Ports and executable tests. Enforce core-first dependency rules and the active infrastructure gate. Route upstream semantic changes to domain-model-change and architecture conflicts to architecture-review."
---

# Implement Slice

Use this Skill only after `S4 Implementation Readiness` / G4 has authorized the exact slice. `docs/process/implementation-readiness-stage.md` owns pre-code readiness; this Skill executes the accepted slice.

## Inputs

- active capsule with `Lifecycle stage: IMPLEMENTATION`;
- `Implementation authorization: G4 PASS`;
- non-`none` `Authorized scope` matching the requested slice;
- non-`none` `Authorization basis` identifying current G4/upstream guarantees;
- relevant current requirements/domain/architecture contracts;
- current code/tests.

## Procedure

1. Confirm a current scoped G4 implementation lease exists.
2. Confirm the requested code work is inside `Authorized scope`.
3. Confirm the authorization basis still points to applicable, non-dirty upstream guarantees; otherwise return to S4.
4. Confirm requested behavior is already accepted at its owning semantic level.
5. Product behavior/quality change -> revoke the affected lease and `REOPEN(S1)`.
6. Identity/lifecycle/invariant/ownership/context-contract change -> revoke the lease and `REOPEN(S2)` through domain-change routing.
7. Responsibility placement/data ownership/dependency/consistency architecture gap -> revoke the lease and `REOPEN(S3)`.
8. Implement inside-out:
   ```text
   Domain -> Application + consuming Ports -> tests -> adapters
   ```
9. Preserve fail-closed behavior, semantic identity and explicit outcomes.
10. Add/adjust executable proof before claiming the slice complete.
11. Run the applicable local/hosted repository checks.
12. Review dependency direction and claims-vs-evidence.
13. Do not close the slice with P0/P1 findings open.

## Guardrails

No framework, database, transport, configuration, logging or DI-container dependency belongs in Domain. Infrastructure does not compensate for unclear core semantics.

When implementation evidence invalidates an upstream guarantee, preserve the current finding in the active execution state, revoke the affected G4 lease and reopen the single owning lifecycle stage instead of patching around it.
