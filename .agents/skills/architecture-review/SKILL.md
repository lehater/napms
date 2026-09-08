---
name: architecture-review
description: "Use to critically review a NAPMS implementation or architecture increment against accepted ADRs, semantic ownership, Clean Architecture/Ports-and-Adapters dependency direction, threat/data ownership constraints, and the active gate. Produce prioritized P0-P3 findings and do not invent upstream product/domain decisions."
---

# Architecture Review

## Review lenses

1. semantic ownership and BC != service/deployment;
2. dependency direction and port ownership;
3. domain invariants/identity/idempotency and claims vs evidence;
4. temporal/fail-closed behavior and external seam semantics;
5. data ownership/persistence bypass risks;
6. security/authority/provenance constraints;
7. unnecessary infrastructure/distribution/abstraction;
8. consistency with accepted ADRs and active plan gate.

## Output

For each material finding:
- priority P0-P3;
- violated accepted contract/invariant;
- concrete evidence/path;
- smallest corrective action.

P0/P1 must be closed or explicitly accepted by the appropriate owner before a gate passes.
