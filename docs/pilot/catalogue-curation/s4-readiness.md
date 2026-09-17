# Catalogue curation M7 pilot — S4 readiness

Status: IN PROGRESS / non-canonical / documentation materialization continuing.

## Pilot execution boundary

This M7 pilot is documentation-system design work only. Product source code, tests and runtime realization are out of scope as design inputs.

Until a later, explicit implementation phase changes this boundary:

- do not write, edit, refactor or generate product code;
- do not change tests, runtime configuration, migrations, workflows or CI;
- do not inspect implementation or tests to resolve, validate or enrich product/domain/architecture/contract semantics;
- derive candidate v2 artifacts only from the accepted current documentation under `docs/**` plus the docs-v2 process/specification artifacts;
- if the accepted `docs/**` sources are ambiguous, contradictory or leave a material design choice unresolved, stop and ask for a decision rather than consulting code;
- if a detail is absent from accepted documentation and is not required for the artifact at the current stage, leave it unspecified rather than inventing it.

The pilot may create or edit only `docs-v2/**` candidate/design artifacts on its branch. Canonical `docs/**` remain unchanged until an explicit documentation cutover step.

## Source authority during this migration pilot

For product/project design truth the source set is the accepted current documentation in `docs/**`. Existing implementation is known to be stale and has no authority in this pilot.

Migration/classification precedence is therefore documentation-only:

1. accepted upstream `docs/**` truth at the earliest owning stage;
2. downstream `docs/**` artifacts consistent with that truth;
3. docs-v2 classification/materialization artifacts derived from 1–2.

Implementation and tests are intentionally excluded from this precedence and from validation of the design slice.

## Materialized so far

The documentation-only materialization has produced the bounded S1 artifacts, the Resource Catalogue S2 domain model/glossary/traceability, and the S3 container/interaction-flow diagrams under `docs-v2/pilot/materialized/**`.

## Superseded implementation-derived finding

The earlier cardinality concern obtained by inspecting executable code is invalid as a design blocker because implementation is outside the authoritative source set. It must not influence the migrated documentation.

The accepted `docs/domain/resource-catalogue/tactical-model.md` and `docs/domain/resource-catalogue/target-realization-model.md` remain the source for Resource realization semantics. Any future implementation reconciliation belongs to a later implementation phase and is not part of M7.

## Readiness result

Result: `PASS` to continue documentation-only materialization from `docs/**`.

This is not a product G4 result and grants no product implementation lease.

## Next task

Materialize the remaining bounded S3 HTTP contract from the accepted legacy documentation in `docs/**` only. If the legacy documentation does not determine a material contract choice needed for the artifact, stop and request that decision. After the contract is materialized, complete documentation-only validation and migration-ledger review.