---
anchor_id: NAPMS-S1-RC-CURATION-INTEGRITY
type_id: quality-requirement
owner_stage: S1
scope:
  scope_id: H12-RC-CURATION-MVP
  product_area: Resource Catalogue curation
  lifecycle_boundary: S1 observable Resource Catalogue curation requirements
canonical_payload: |-
  # Resource Catalogue integrity and history quality

  ## Historical integrity

  Time-qualified Resource realization, scope-affiliation and responsibility facts shall be maintained by adding, ending or replacing versions/relations according to their owning semantics. Supported curation shall not silently rewrite historical facts as non-temporal scalar fields.

  ## Validation integrity

  Catalogue mutations shall fail explicitly when required identifiers, references or provenance are missing; temporal intervals are invalid; or overlapping effective facts violate accepted catalogue invariants.

  Immutable identities or revisions already referenced by downstream business truth shall not be silently rewritten.

  ## Submission safety

  Duplicate submission shall be idempotent when a natural command identity/idempotency contract exists, or otherwise be prevented and reported safely.

  This quality requirement does not select a transport representation, ETag scheme, persistence technology or command-identity design; those realization decisions belong to later stages.
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
      Canonical curation requirements constrain the self-service workflow with observable history-preservation, validation
      and safe-submission qualities while leaving technical realization to later stages.
  recorded_at: '2026-09-17'
status: ACCEPTED
semantic_fingerprint: sha256-jcs-v1:e505118d22c45bd930386310d38cb9939697df774293a7b92505e9a6a8f03460
validation:
  freshness: CURRENT
  evidence_ref: docs-v2/migration/revalidated/h12-rc-curation/validation/s1-change-set-validation.yaml
  evidence_target: NAPMS-S1-RC-CURATION-INTEGRITY
  validated_fingerprint: sha256-jcs-v1:e505118d22c45bd930386310d38cb9939697df774293a7b92505e9a6a8f03460
  profile: change-set-anchor-acceptance
  profile_version: cp-v1
  enforcement_status: specification-manual-not-CI
---
