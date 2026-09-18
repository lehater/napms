---
name: architecture-review
description: "Use to critically review a NAPMS architecture or implementation increment against current canonical requirements/domain ownership, C4 structure, architecture rules, contracts and persistence design. Produce prioritized P0-P3 findings and route each finding to the smallest current owner without inventing upstream semantics."
---

# Architecture Review

Review only the canonical graph nodes relevant to the scope plus concrete implementation evidence when implementation is being reviewed.

## Lenses

1. semantic ownership and BC != service/deployment;
2. dependency direction and port ownership;
3. domain identity/invariants and claims versus evidence;
4. fail-closed behavior and external seam semantics;
5. data ownership/persistence bypass risks;
6. authority/provenance constraints;
7. unnecessary distribution/abstraction/infrastructure;
8. consistency among current C4 structure, architecture rules, OpenAPI and persistence owners.

For each material finding report priority P0-P3, violated current owner/rule, concrete evidence and smallest corrective action. If the correction requires missing product/domain truth, route it to that canonical owner rather than resolving it as an architecture convenience.

P0/P1 findings block claiming the reviewed scope complete until addressed or explicitly accepted by the proper owner.
