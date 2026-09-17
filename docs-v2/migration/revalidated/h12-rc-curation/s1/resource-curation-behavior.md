---
anchor_id: NAPMS-S1-RC-CURATION-BEHAVIOR
type_id: functional-requirement
owner_stage: S1
scope:
  scope_id: H12-RC-CURATION-MVP
  product_area: Resource Catalogue curation
  lifecycle_boundary: S1 observable Resource Catalogue curation requirements
canonical_payload: |-
  # Resource Catalogue curation behavior

  ## Supported user behavior

  For an authenticated user admitted to Resource Catalogue curation, the supported product workflow shall allow the user to:

  1. create/register an access-relevant Resource identity with required provenance;
  2. inspect Resource details;
  3. add a new endpoint/realization version with one or more technical addresses;
  4. end or replace time-qualified realization facts without rewriting historical facts;
  5. affiliate the Resource with one or more Responsibility Scopes using the existing time-qualified affiliation semantics;
  6. end or replace a scope affiliation without changing Resource identity;
  7. maintain Resource Responsibility assignments for supported person/team references and roles; and
  8. inspect the effective/current Resource projection while retaining access to technical identifiers and provenance.

  ## Resource discovery and missing relations

  The Resource workspace shall provide server-backed paging, search/filter over Resource reference and available display/contact information, and scope-focused filtering using effective Resource Scope Affiliation.

  A Resource remains a Resource when no effective scope affiliation or endpoint realization exists. Missing current realization, scope affiliation or relevant operational responsibility/contact information shall be represented explicitly rather than hidden or fabricated.

  ## Cardinality contract

  A new endpoint/realization version supports one or more technical addresses. This S1 contract does not narrow that cardinality to a single effective address or AddressSpace.

  ## Ownership boundary

  This requirement owns observable Resource-curation behavior only. Resource domain invariants and model boundaries belong to S2; API, persistence and UI realization choices belong to S3.
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
      Current canonical requirements refine the accepted self-service catalogue problem and journey into observable Resource-curation
      behavior while preserving later-stage ownership boundaries.
  recorded_at: '2026-09-17'
status: ACCEPTED
semantic_fingerprint: sha256-jcs-v1:1c70355ed0db0c2cf67d9167bf662f6351d665080ea5f4a3ac68e8e9821d2722
validation:
  freshness: CURRENT
  evidence_ref: docs-v2/migration/revalidated/h12-rc-curation/validation/s1-change-set-validation.yaml
  evidence_target: NAPMS-S1-RC-CURATION-BEHAVIOR
  validated_fingerprint: sha256-jcs-v1:1c70355ed0db0c2cf67d9167bf662f6351d665080ea5f4a3ac68e8e9821d2722
  profile: change-set-anchor-acceptance
  profile_version: cp-v1
  enforcement_status: specification-manual-not-CI
---
