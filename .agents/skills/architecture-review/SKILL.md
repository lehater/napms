---
name: architecture-review
description: "Use to critically review a NAPMS implementation or architecture increment against current accepted requirements, domain ownership, architecture contracts and applicable current ADRs, including Clean Architecture/Ports-and-Adapters dependency direction, threat/data ownership constraints, and the active gate. Produce prioritized P0-P3 findings and do not invent upstream product/domain decisions."
---

# Architecture Review

Use this Skill as a judgement-heavy review inside `S3 Architecture` or when implementation evidence challenges current accepted architecture. `docs/process/architecture-stage.md` owns S3 design/G3 progression; this Skill does not replace the stage protocol.

## Review lenses

1. semantic ownership and BC != service/deployment;
2. dependency direction and port ownership;
3. domain invariants/identity/idempotency and claims vs evidence;
4. temporal/fail-closed behavior and external seam semantics;
5. data ownership/persistence bypass risks;
6. security/authority/provenance constraints;
7. unnecessary infrastructure/distribution/abstraction;
8. consistency with current requirements/domain/architecture, applicable ADRs and the active plan gate;
9. consistency between current as-built architecture and target architecture where both are intentionally retained.

Load only ADRs that materially constrain the reviewed scope. An implemented ADR remains relevant when its choice is still needed to reproduce or safely evolve the current design; superseded-only ADRs are not working-tree authority.

When a finding requires a missing product decision, use `REOPEN(S1)`. When it requires missing/wrong domain semantics or ownership, use `REOPEN(S2)`. Do not encode ambiguous combined reopen targets. When the issue is an architecture-owned realization deficiency, keep it in S3 as `REWORK`.

## Output

For each material finding:
- priority P0-P3;
- violated current contract/invariant/decision;
- concrete evidence/path;
- owning lifecycle stage;
- smallest corrective action.

P0/P1 that affect G3 guarantees prevent G3 PASS until resolved in the appropriate owner.
