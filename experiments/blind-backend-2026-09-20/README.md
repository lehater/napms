# Blind greenfield backend reconstruction — 2026-09-20

Status: IN_PROGRESS

## Research question

Can the current Harness, using only independently sourced NAPMS problem/product/stakeholder/evidence inputs and external constraints, reconstruct sufficient backend engineering knowledge for the IMPLEMENTATION consumer without forcing implementation to make material upstream decisions?

## Isolation

- Working branch: `research/blind-greenfield-backend-reconstruction`.
- `main` is read-only for source classification and remains unchanged.
- Existing NAPMS derived design is excluded until the new backend design is frozen.
- Frontend/UI design is out of scope except observable backend semantics required by accepted product input.
- Production implementation is out of scope.
- Harness is used as-is; Harness changes require a separately documented reproducible consumer failure first.

## Experiment order

1. Build and freeze the admissible Source Corpus.
2. Derive an experimental Engineering Graph for the IMPLEMENTATION consumer using current Harness rules.
3. Produce knowledge only when its prerequisites are satisfied.
4. Route missing semantics as Questions instead of downstream assumptions.
5. Run the Coding-Agent Challenge.
6. Freeze the blind design.
7. Only after freeze compare with canonical NAPMS.
