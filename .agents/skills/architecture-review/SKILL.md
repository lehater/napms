---
name: architecture-review
description: "Use to critically review a NAPMS implementation or architecture increment against accepted ADRs, semantic ownership, Clean Architecture/Ports-and-Adapters dependency direction, threat/data ownership constraints, and the active gate. Produce prioritized P0-P3 findings and do not invent upstream product/domain decisions."
---

# Architecture Review

Use this Skill as a judgement-heavy review inside `S3 Architecture` or when implementation evidence challenges accepted architecture. `docs/process/architecture-stage.md` owns S3 design/G3 progression; this Skill does not replace the stage protocol.

## Review lenses

1. semantic ownership and BC != service/deployment;
2. dependency direction and port ownership;
3. domain invariants/identity/idempotency and claims vs evidence;
4. temporal/fail-closed behavior and external seam semantics;
5. data ownership/persistence bypass risks;
6. security/authority/provenance constraints;
7. unnecessary infrastructure/distribution/abstraction;
8. consistency with accepted ADRs and active plan gate.

When a finding requires a missing product/domain decision, route it upstream with `REOPEN(S1/S2)` rather than proposing an architecture workaround. When the issue is an architecture-owned realization deficiency, keep it in S3 as `REWORK`.

## Output

For each material finding:
- priority P0-P3;
- violated accepted contract/invariant;
- concrete evidence/path;
- owning lifecycle stage;
- smallest corrective action.

P0/P1 that affect G3 guarantees prevent G3 PASS until resolved in the appropriate owner.
