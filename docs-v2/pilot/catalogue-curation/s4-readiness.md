# Catalogue curation M7 pilot — S4 readiness

Status: BLOCKED / non-canonical / documentation materialization stopped on a design decision.

## Pilot execution boundary

This M7 pilot is documentation-system design work only. Product source code is evidence, not an output.

Until a later, explicit implementation authorization changes this boundary:

- do not write, edit, refactor or generate product code;
- do not change tests to make the pilot pass;
- do not change runtime configuration, migrations, workflows or CI as part of this pilot;
- inspect implementation and tests only to corroborate already accepted documentation truth or to discover documentation gaps;
- if documentation cannot be completed without a product/code decision, record the gap or blocker instead of implementing a solution.

The pilot may create or edit only `docs-v2/**` candidate/design artifacts on its branch. Canonical `docs/**` remain unchanged until an explicit documentation cutover step.

## Materialized so far

The documentation-only materialization has produced the bounded S1 artifacts, the Resource Catalogue S2 domain model/glossary/traceability, and the S3 container/interaction-flow diagrams under `docs-v2/pilot/materialized/**`.

The HTTP/OpenAPI artifact has deliberately not been created.

## Executable API evidence inspected

The repository uses FastAPI as the executable API-schema source. `create_http_api()` constructs the `FastAPI` application, and `build_http_process()` includes the Resource Catalogue curation, workspace and temporal routers. Their Pydantic request models and route declarations contribute to the generated OpenAPI schema.

The bounded inspection covered `api.py`, `http_process.py`, the RC `curation.py`, `temporal.py`, `workspace.py` routers and existing RC HTTP tests. Product files were read only.

## Design drift discovered during OpenAPI materialization

Materializing the HTTP contract exposed a semantic mismatch that cannot be resolved as a formatting/transformation choice:

- the accepted S2 pilot model, derived from the current domain documentation, models one effective `AddressSpace` per Resource at a logical time, with `AddressSpace = HostAddress | Prefix`;
- the executable RC HTTP/domain evidence uses plural `technicalAddresses` and represents a realization with endpoint realizations, so the executable contract can carry multiple addresses/endpoints in one realization;
- generating OpenAPI directly from executable evidence would therefore promote a downstream implementation shape into canonical contract/domain truth;
- forcing the one-AddressSpace S2 model into OpenAPI would instead document a contract that does not faithfully describe the executable surface.

This is exactly the class of ambiguity the pilot process is intended to stop on. No product behavior is inferred and no code change is proposed.

## Decision required

The documentation design needs an explicit semantic choice before the slice can continue:

1. Resource realization is semantically **one effective AddressSpace per Resource at a logical time**; plural executable `technicalAddresses` is realization/legacy drift to be recorded for later product reconciliation; or
2. Resource realization is semantically **a set/list of endpoint/address realizations per Resource at a logical time**; S2 domain documentation must be reopened and corrected before S3/OpenAPI materialization continues; or
3. another explicit semantic model is chosen and documented at S2.

This decision belongs upstream of the HTTP contract. It must not be made by copying the current implementation into documentation.

## Readiness result

Result: `BLOCKED` at OpenAPI materialization pending the Resource realization cardinality/semantics decision above.

Previously materialized S1/S2/S3 candidate artifacts remain non-canonical pilot evidence. The S2 model is specifically subject to reopening if option 2 or another model is selected. No canonical `docs/**`, product code, tests, migrations, runtime configuration, workflows or CI were changed.

## Next task after decision

Reopen the earliest affected stage (S2 if realization semantics change; otherwise S3 contract reconciliation), update affected candidate artifacts and traceability, then materialize the bounded RC OpenAPI contract and complete documentation validation.