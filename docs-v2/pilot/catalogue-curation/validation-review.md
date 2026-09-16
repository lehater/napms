# Catalogue curation M7 pilot — validation review

Status: COMPLETE / documentation-only pilot slice.

## Validation boundary

This review validates only the documentation-system pilot artifacts derived from accepted `docs/**`. Product code, tests, runtime configuration, migrations, workflows and CI are excluded as design evidence and were not changed for this review.

## Materialized artifact set

S1:
- `materialized/requirements/functional/catalogue-curation.md`
- `materialized/requirements/quality/catalogue-curation.md`
- `materialized/requirements/functional/catalogue-curation-acceptance.md`

S2:
- `materialized/domain/resource-catalogue/domain-model.puml`
- `materialized/domain/resource-catalogue/README.md`
- `materialized/domain/traceability/catalogue-curation.yaml`

S3:
- `materialized/architecture/containers.puml`
- `materialized/architecture/flows/resource-catalogue-curation.puml`
- `materialized/contracts/http/resource-catalogue.openapi.yaml`

## V0 — structure and ownership

Result: PASS.

- Candidate artifacts are contained under `docs-v2/pilot/materialized/**`; canonical `docs/**` ownership is untouched.
- Requirements are organized by observable behavior/quality rather than bounded context ownership.
- Resource Catalogue semantic truth is owned by the S2 domain model/glossary.
- Architecture and HTTP artifacts consume S1/S2 truth without becoming alternative domain owners.
- No empty optional directory tree was pre-created.
- No S0 constraint was invented from downstream solution wording.

## V1 — artifact syntax/shape

Result: PASS for pilot review.

- Markdown artifacts have explicit status/scope and stable requirement/acceptance IDs.
- PlantUML artifacts use bounded model/container/sequence notation and do not carry generated renderings as canonical truth.
- Traceability YAML is machine-readable and references materialized S1 identifiers.
- OpenAPI is expressed as OpenAPI 3.1 YAML and contains only the selected Resource Catalogue surface.

This review records structural/syntactic inspection of the candidate source text. No product-code or test execution is part of this documentation-only validation boundary.

## V2 — cross-artifact consistency

Result: PASS after one documented S2→S3 correction.

- `REQ-CAT-RC-001..006` remain observable S1 requirements; RC model terms are not imported into S1 as ownership.
- `Resource`, `ResourceAddressFact`, `AddressSpace`, `ResourceScopeAffiliation`, `ResourceResponsibility` and `CurrentResourceRealization` have one S2 semantic owner.
- MVP cardinality is consistent across S2 and the candidate HTTP contract: at one logical time a Resource has at most one effective `AddressSpace`, exactly `HostAddress` or `Prefix` when resolved.
- The superseded S3 `technicalAddresses[]`/endpoint shape from the legacy HTTP document is intentionally not migrated. The user resolved the legacy-document contradiction in favor of the current S2 MVP semantics.
- Responsibility, scope affiliation and actor authority remain distinct across S1/S2/S3.
- Temporal maintenance is create/end/replace; historical facts/provenance are preserved.
- Application Communication Catalogue, DCS and Deployment Resource Binding semantics remain outside the bounded pilot rather than being reassigned to RC.

## V3 — stage/gate evidence

Result: PASS for pilot evidence only.

- S1 classification completed with a candidate G1 PASS.
- S2 classification completed with a candidate G2 PASS.
- S3 classification completed with a candidate G3 PASS, then its stale address-cardinality transport detail was corrected during materialization from authoritative S2 truth.
- S4 documentation-materialization readiness is PASS.

These are M7 pilot results, not canonical product gate decisions and not an implementation lease.

## V4/V5 — realization and journey

Result: NOT APPLICABLE to this design-only M7 execution.

The current project instruction explicitly excludes implementation/code/tests as design sources. No claim is made that the stale implementation realizes these candidate artifacts. Implementation realization and executable journey validation belong to a later explicitly authorized implementation phase.

## Migration-ledger review

Result: PASS for the selected Resource Catalogue slice.

- `docs/requirements/catalogue-curation.md`: selected RC observable behavior is split into S1 functional/quality artifacts; S2/S3 claims are not duplicated there.
- `docs/requirements/catalogue-curation-acceptance-examples.md`: selected RC scenarios are materialized; ACC-only scenarios remain excluded.
- `docs/requirements/catalogue-curation-security.md`: observable admission/trust behavior is represented without moving Authority Management domain ownership into RC.
- `docs/domain/resource-catalogue/tactical-model.md` + `target-realization-model.md`: overlapping target semantics are merged into one candidate RC domain model/glossary/trace set.
- `docs/architecture/catalogue-curation-boundary.md`: selected RC structural and interaction concerns are separated into S3 architecture artifacts.
- `docs/engineering/catalogue-curation-http-api-contract.md`: selected RC transport surface is transformed to OpenAPI, with the superseded plural-address shape corrected to the current MVP S2 decision.
- Canonical legacy files are retained; no cutover/deletion is performed in M7.

## Pilot findings for docs-v2

1. Earliest-stage ownership worked as intended: the S2 model prevented stale downstream S3 transport wording from silently redefining Resource semantics.
2. A documentation-only migration must not consult implementation when the implementation is known stale; the process must support an explicit source-authority policy per migration/pilot.
3. Machine-readable traceability and OpenAPI are useful only after semantic ownership/classification is resolved; generating them earlier would have encoded the stale plural-address contract.
4. The target physical location `docs/requirements/constraints.md` remains system-level layout debt because `constraint` is semantically S0-owned. This pilot did not encounter a new constraint and therefore did not resolve the global layout issue.
5. Candidate artifact materialization can be performed without modifying canonical `docs/**`; this supports a review-before-cutover migration strategy.

## Completion result

M7 catalogue-curation documentation slice: COMPLETE.

The bounded slice has been classified, materialized and documentation-validated through S4. There are no unresolved product/domain questions in the selected slice after the MVP single-AddressSpace decision.

No implementation is authorized. No canonical documentation cutover is authorized by this result.

The next process boundary is M7 pilot evaluation/system-spec feedback and, after that feedback is accepted, an explicit decision on whether/how to cut over candidate artifacts into canonical `docs/**`.