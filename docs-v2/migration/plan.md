# Documentation System v2 migration plan

Status: ACTIVE DESIGN PLAN / no product migration authorized.

## Goal

Design, pilot and validate Documentation System v2 before replacing the current canonical `docs/` tree.

## Invariants

- `docs/` remains canonical until explicit cutover;
- `docs-v2/` contains specifications and later pilot material only;
- do not bulk-copy old documents into the new tree;
- migrate current truth artifact-by-artifact after its target specification exists;
- Git history is the long-term archive; `docs-old/` may exist only as short-lived cutover insurance if needed.

## Iterations

- [x] M0 — establish charter, principles and workstream skeleton.
- [ ] M1 — complete lifecycle specification.
- [ ] M2 — complete artifact catalog and applicability model.
- [ ] M3 — complete repository layout/naming specification.
- [ ] M4 — complete agent execution/progressive-disclosure specification.
- [ ] M5 — complete validation/CI model.
- [ ] M6 — map current docs to v2, define migration order, cutover and rollback.
- [ ] M7 — run one bounded pilot and revise specifications from evidence.
- [ ] V2 readiness review.
- [ ] Controlled migration and cutover.
- [ ] Remove temporary legacy tree after verification.

## Machine-readable specification track

Plan a compact schema for lifecycle, artifact types, applicability, locations and validations after the semantic specifications stabilize. Do not freeze YAML/schema fields before M1-M5 establish the semantics they encode.

## Current task

M1 — lifecycle specification.

## Exit criteria

V2 is ready for migration only when lifecycle, artifact catalog, layout, agent execution and validation specifications are coherent; the pilot passes; current-doc mapping is complete; and cutover/rollback rules are explicit.