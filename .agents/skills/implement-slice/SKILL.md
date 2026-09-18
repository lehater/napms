---
name: implement-slice
description: "Use for an explicitly authorized NAPMS implementation slice whose required behavior and architecture already exist in current canonical design. Implement inside-out, preserve owner boundaries, add executable proof, and route any newly exposed design gap back to its canonical owner instead of inventing semantics in code."
---

# Implement Slice

## Preconditions

- explicit product-code/test authorization covers the requested slice;
- `docs/plans/first-mvp-implementation-readiness.yaml` or another current readiness owner covers the slice;
- required domain, architecture, HTTP and persistence owners are current in `docs/canonical-graph.yaml`.

## Procedure

1. Confirm requested code/test work is inside explicit authorization.
2. Load only the canonical graph nodes the slice consumes plus the implementation files being changed.
3. Confirm requested behavior is already defined by its owning design artifact.
4. If implementation exposes missing product/domain/architecture truth, stop that affected part and route the question/change to the owning canonical artifact; do not infer the answer from code.
5. Implement inside-out: Domain -> Application/Ports -> executable tests -> adapters/composition.
6. Preserve module ownership, fail-closed authority behavior, stable identities and explicit outcomes.
7. Add or adjust executable proof before claiming the slice complete.
8. Run applicable product checks. If canonical design changed as part of separately authorized design work, also run `make design-check`.
9. Review dependency direction and claims versus evidence before completion.

Implementation evidence may reveal a design gap, but it never becomes the replacement design source.
