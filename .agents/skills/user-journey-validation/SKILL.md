---
name: user-journey-validation
description: "Use when validating one NAPMS user journey end-to-end from a user goal through the UI to a durable outcome. Assess completeness, usability, essential negative/recovery states and evidence; classify gaps P0-P3 and route them to current owners. Do not invent product semantics or implement fixes as part of validation."
---

# User Journey Validation

1. State actor, start state, goal, end state and required durable result.
2. Load the accepted use-case/journey owner and only the canonical graph dependencies needed to interpret it.
3. Separate accepted behavior from assumptions. Missing/conflicting product truth is a blocker or decision for the owning artifact, not something to invent to make the journey pass.
4. Define the smallest representative fixture and execute the journey through the same UI actions available to the actor.
5. Assess discoverability, capability, correctness, feedback/recovery and required durability.
6. Exercise only the negative/correction paths needed to prove ordinary recovery.
7. Classify findings P0-P3 and record blocked step, observed result, expected accepted result and evidence.
8. Route each gap by owner: semantic/authority/ownership gap -> current design owner; accepted behavior missing in code -> authorized implementation workflow; presentation-only defect -> scoped Web work.
9. After fixes, rerun from a clean representative start state.
10. Add/refresh automated E2E regression for stable high-value paths when useful.

The journey is complete when its goal and durable result are reachable through the supported UI, material recovery paths work, and no P0/P1 findings remain.
