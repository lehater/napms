---
anchor_id: NAPMS-S1-RC-CURATION-AUTHORIZATION
type_id: functional-requirement
owner_stage: S1
scope:
  scope_id: H12-RC-CURATION-MVP
  product_area: Resource Catalogue curation
  lifecycle_boundary: S1 observable Resource Catalogue curation requirements
canonical_payload: |-
  # Resource Catalogue mutation authorization

  ## Admission

  Every Resource Catalogue mutation shall use the authenticated session Actor and the server-owned `CurateResourceCatalogue @ resource-catalogue` administrative action/scope. The owning backend use case selects that action/scope and evaluates Authority Management admission for the Actor and effective time before persistence.

  The client shall not supply trusted actor identity, catalogue authority scope or server action time.

  ## Separation from catalogue facts

  None of the following facts grants Resource Catalogue mutation permission by itself:

  - Resource Scope Affiliation;
  - Resource Responsibility or owner/contact role;
  - ability to read a Resource or catalogue workspace;
  - ability to read Connectivity/Checker;
  - `ProposeConnectivity` or `DecideConnectivity`;
  - Access Rule read or mutation authority.

  A Responsibility Scope carried as business data in a Resource affiliation mutation shall not replace the fixed `resource-catalogue` authorization scope.

  ## Read and mutation behavior

  UI visibility or enabled state for create/edit actions is presentation only. Direct invocation of the corresponding backend mutation shall still be denied when Authority Management admission is absent.

  Catalogue read visibility continues to follow the existing baseline until a separate accepted requirement changes it.

  ## Failure behavior

  Authorization denial shall remain distinguishable from domain/structural validation failure, optimistic concurrency conflict, idempotency conflict and persistence/transport uncertainty. Protected internal authority or provenance details shall not be leaked merely to explain a denial.
semantic_refs:
- relation: DERIVES_FROM
  target:
    kind: anchor-current
    anchor_id: NAPMS-S0-RC-CURATION-PROBLEM
  impact: semantic
  rationale_ref: provenance.derivation.rationale
- relation: REFINES
  target:
    kind: anchor-current
    anchor_id: NAPMS-S0-RC-CURATION-JOURNEY
  impact: semantic
  rationale_ref: provenance.derivation.rationale
provenance:
  origin_kind: mixed
  source_refs:
  - kind: repository-file
    path: docs/requirements/catalogue-curation.md
    blob_sha: 92833e29efc3bfdb6503e5b600e48296b8fb6041
  - kind: repository-file
    path: docs/requirements/catalogue-curation-security.md
    blob_sha: cef21bf26c44aae1b02e3313149278606892d26c
  authority_basis: imported-current-docs-ref-before-cutover
  derivation:
    input_anchor_refs:
    - anchor_id: NAPMS-S0-RC-CURATION-PROBLEM
      semantic_fingerprint: sha256-jcs-v1:b7b3162275fcd1df95904284f6846412278f332d3393e2aa8e9786ac6e914b12
    - anchor_id: NAPMS-S0-RC-CURATION-JOURNEY
      semantic_fingerprint: sha256-jcs-v1:5401681959c4ef07ce2b990b28ff2df1ee2eb5756b3d6355b641ab4f0f5bd475
    derivation_rule_or_method: DOCS-V2-NAPMS-MIGRATION-REVALIDATION.H12-T3
    derivation_kind: refinement
    rationale: >-
      Canonical I27 security requirements refine the accepted responsible-user journey with observable admission and denial
      behavior without moving Authority Management ownership into Resource Catalogue.
  recorded_at: '2026-09-17'
status: ACCEPTED
semantic_fingerprint: sha256-jcs-v1:abdfa0128b7311173305ca8e3641d5b1a96cf0076b726bd386e9324cf6e68f2c
validation:
  freshness: CURRENT
  evidence_ref: docs-v2/migration/revalidated/h12-rc-curation/validation/s1-change-set-validation.yaml
  evidence_target: NAPMS-S1-RC-CURATION-AUTHORIZATION
  validated_fingerprint: sha256-jcs-v1:abdfa0128b7311173305ca8e3641d5b1a96cf0076b726bd386e9324cf6e68f2c
  profile: change-set-anchor-acceptance
  profile_version: cp-v1
  enforcement_status: specification-manual-not-CI
---
