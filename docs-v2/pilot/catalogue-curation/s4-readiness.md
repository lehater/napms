# Catalogue curation M7 pilot — S4 readiness

Status: IN PROGRESS / non-canonical / documentation materialization continuing.

## Pilot execution boundary

This M7 pilot is documentation-system design work only. Product source code is evidence, not an output.

Until a later, explicit implementation authorization changes this boundary:

- do not write, edit, refactor or generate product code;
- do not change tests to make the pilot pass;
- do not change runtime configuration, migrations, workflows or CI as part of this pilot;
- inspect implementation and tests only as realization evidence or to discover documentation/implementation drift;
- if documentation cannot be completed without a genuine product/domain decision not already answered by accepted documentation, record the gap or blocker instead of implementing a solution.

The pilot may create or edit only `docs-v2/**` candidate/design artifacts on its branch. Canonical `docs/**` remain unchanged until an explicit documentation cutover step.

## Source precedence during this migration pilot

Accepted current documentation has authority over existing implementation when they conflict.

For migration/classification purposes the precedence is:

1. accepted upstream documentation truth at the earliest owning stage;
2. downstream documentation consistent with that truth;
3. implementation and tests as realization/evidence only.

Therefore code/test behavior must not silently rewrite S0/S1/S2/S3 documentation semantics. A conflict with implementation is recorded as realization drift for later implementation reconciliation. It is not a documentation blocker unless the accepted documentation itself is ambiguous or contradictory.

## Materialized so far

The documentation-only materialization has produced the bounded S1 artifacts, the Resource Catalogue S2 domain model/glossary/traceability, and the S3 container/interaction-flow diagrams under `docs-v2/pilot/materialized/**`.

## Resolved realization drift

During OpenAPI preparation the executable RC implementation exposed plural `technicalAddresses`, while the accepted current domain documentation models one effective `AddressSpace` per Resource at a logical time, with `AddressSpace = HostAddress | Prefix`.

Under the source-precedence rule above, this is no longer a design decision for the documentation pilot:

- the accepted S2 documentation semantics remain authoritative;
- the executable plural shape is implementation drift/evidence to reconcile later;
- S2 is not reopened merely to copy implementation behavior;
- the candidate HTTP contract must express the accepted documented semantics, and validation must record where the current executable surface differs.

No product/code change is authorized or proposed by this resolution.

## Readiness result

Result: `PASS` to continue documentation-only materialization.

The former cardinality blocker is resolved by explicit documentation precedence. This is not a product G4 result and grants no product implementation lease.

## Next task

Materialize the bounded Resource Catalogue HTTP/OpenAPI candidate from accepted S1/S2/S3 documentation truth, explicitly recording implementation drift rather than importing conflicting executable cardinality. Then complete pilot documentation validation and migration-ledger review.