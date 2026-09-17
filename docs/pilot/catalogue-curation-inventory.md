# M7 pilot — catalogue curation inventory

Status: COMPLETE / S1-S4 documentation slice materialized and reviewed / non-canonical.

## Pilot scope

The first Documentation System v2 pilot used the Resource Catalogue curation happy path. The authoritative product/project inputs for the pilot are accepted current documents under `docs/**`; implementation and tests are intentionally excluded because they are stale and are not design sources for this project phase.

The pilot migrates/designs documentation knowledge only. It does not authorize product implementation and does not change canonical `docs/` ownership.

## Source inventory and final disposition

| Legacy/current source | Candidate v2 type | Final disposition |
|---|---|---|
| `docs/requirements/catalogue-curation.md` | functional + quality requirements | SPLIT; selected RC observable behavior materialized |
| `docs/requirements/catalogue-curation-acceptance-examples.md` | acceptance scenarios | TRANSFORM; selected RC scenarios materialized |
| `docs/requirements/catalogue-curation-security.md` | functional + quality requirements | SPLIT; observable admission/trust behavior materialized without moving AM ownership |
| `docs/domain/resource-catalogue/tactical-model.md` | domain model + glossary | TRANSFORM/MERGE; current MVP semantics authoritative |
| `docs/domain/resource-catalogue/target-realization-model.md` | domain model/glossary support | MERGE; overlapping target semantics have one candidate owner |
| `docs/architecture/catalogue-curation-boundary.md` | container view + interaction flow | SPLIT/TRANSFORM for selected RC slice |
| `docs/engineering/catalogue-curation-http-api-contract.md` | HTTP contract | TRANSFORM to bounded OpenAPI; stale plural-address wording corrected from authoritative S2 decision |

## Explicit exclusions

The pilot does not migrate the whole Resource Catalogue, UI wireframes, application catalogue legacy compatibility, access-policy lifecycle, deployment behavior, unrelated shared HTTP conventions, product code or tests.

## Constraint ownership guardrail

Externally imposed/non-negotiable `constraint` artifacts are S0-owned. S1 consumes accepted S0 truth and does not redefine it. Physical placement under `docs/requirements/**` does not change semantic ownership. No new S0 constraint was identified in this slice.

## Materialized candidate set

The candidate artifacts are under `docs-v2/pilot/materialized/**`:

- S1 functional, quality and acceptance artifacts;
- S2 Resource Catalogue domain model, glossary and machine-readable requirement/domain trace;
- S3 container view, interaction flows and Resource Catalogue OpenAPI contract.

Canonical `docs/**` remain untouched.

## Design decision encountered during the pilot

Legacy S3 HTTP wording still described plural `technicalAddresses[]`/endpoint realization, while the revalidated S2 Resource Catalogue model explicitly supersedes that shape.

Decision: for MVP one Resource has at most one effective `AddressSpace` at a logical time, and that value is exactly one `HostAddress` or one `Prefix`. Multiple simultaneous addresses/prefixes are deferred until a future use case requires them.

The candidate S3 HTTP contract follows this S2 decision.

## Validation and exit

`docs-v2/pilot/catalogue-curation/validation-review.md` records V0-V3 and migration-ledger review as PASS for the bounded documentation pilot. V4/V5 implementation/journey realization is not applicable in the current design-only phase.

M7 catalogue-curation slice is complete through S4 documentation materialization and review. There are no unresolved product/domain questions in this selected slice.

No implementation lease and no canonical documentation cutover are granted by this completion result.

Next process boundary: feed M7 findings back into the Documentation System v2 specifications/migration plan, then make an explicit later decision about canonical documentation cutover.