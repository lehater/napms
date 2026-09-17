# NAPMS canonical documentation

Status: CANONICAL.

`docs-v2/` is the sole current documentation authority for NAPMS after H20 cutover. It contains the machine-readable linked design graph, Harness specifications and durable workstream state used to take design from problem framing through implementation readiness.

`docs/` is retired, frozen migration evidence only. It cannot override accepted truth here and must not receive new design truth.

## Start here

For continuation of project design or Harness work:

1. read `meta/workstream-state.yaml`;
2. read `meta/roadmap.yaml` when lifecycle/program context is required;
3. load only the accepted anchors and specifications directly needed by the task;
4. follow semantic references rather than reconstructing truth from implementation code or historical chat.

## Current design maturity

The strategic NAPMS DDD baseline is canonical here. The selected first-MVP journey has accepted S1 requirements, S2 tactical domain design, S3 system architecture and S4 implementation/verification design. G4 is PASS for that exact MVP design scope. Implementation readiness does not itself authorize product-code or product-test changes.

## Repository areas

- `spec/` — Documentation System / Harness contracts.
- `migration/revalidated/` — accepted/revalidated NAPMS design anchors and their validation evidence.
- `meta/` — roadmap, durable workstream state and Harness evolution records.
- `horizontal/` — retained earlier projections/evidence from the redesign; canonical truth is determined by accepted anchors and their semantic references.
- `migration/` — migration provenance; historical source material does not outrank accepted anchors.

## Authority rules

- accepted current anchors are the design truth for their owned semantics;
- human-owned truth is never invented;
- product code and tests are implementation/evidence, not substitutes for product/domain/architecture design truth;
- generated views do not override canonical sources;
- changed design is revalidated through its affected semantic graph;
- operational Harness bookkeeping stays behind the design boundary rather than becoming a design process of its own.

H20 completed the authority cutover on 2026-09-17. The old `docs/` tree remains only as explicitly retired evidence so there is one normal documentation authority: this namespace.
