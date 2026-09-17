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
  3. establish a time-qualified Resource realization with one AddressSpace, either one HostAddress or one Prefix;
  4. end or replace time-qualified realization facts without rewriting historical facts;
  5. affiliate the Resource with one or more Responsibility Scopes using the existing time-qualified affiliation semantics;
  6. end or replace a scope affiliation without changing Resource identity;
  7. maintain Resource Responsibility assignments for supported person/team references and roles; and
  8. inspect the effective/current Resource projection while retaining access to technical identifiers and provenance.

  ## Resource discovery and missing relations

  The Resource workspace shall provide server-backed paging, search/filter over Resource reference and available display/contact information, and scope-focused filtering using effective Resource Scope Affiliation.

  A Resource remains a Resource when no effective scope affiliation or realization exists. Missing current realization, scope affiliation or relevant operational responsibility/contact information shall be represented explicitly rather than hidden or fabricated.

  ## Cardinality contract

  For the MVP, one Resource has at most one effective AddressSpace at one logical time. When present, that AddressSpace is exactly one HostAddress or one Prefix. Multiple simultaneous addresses/prefixes and endpoint/interface abstractions are outside the MVP unless a later accepted requirement changes this rule.

  ## Ownership boundary

  This requirement owns observable Resource-curation behavior only. Resource domain invariants and model boundaries belong to S2; API, persistence and UI realization choices belong to S3.
semantic_refs:
- relation: DERIVES_FROM
  target: {kind: anchor-current, anchor_id: NAPMS-S0-RC-CURATION-PROBLEM}
  impact: semantic
  rationale_ref: provenance.derivation.rationale
- relation: REFINES
  target: {kind: anchor-current, anchor_id: NAPMS-S0-RC-CURATION-JOURNEY}
  impact: semantic
  rationale_ref: provenance.derivation.rationale
provenance:
  origin_kind: mixed
  source_refs:
  - {kind: repository-file, path: docs/requirements/catalogue-curation.md, blob_sha: 92833e29efc3bfdb6503e5b600e48296b8fb6041}
  - {kind: stakeholder-correction, ref: H12-R-RC-MVP-SINGLE-ADDRESS-SPACE}
  authority_basis: explicit-stakeholder-correction
  derivation:
    input_anchor_refs:
    - {anchor_id: NAPMS-S0-RC-CURATION-PROBLEM, semantic_fingerprint: sha256-jcs-v1:b7b3162275fcd1df95904284f6846412278f332d3393e2aa8e9786ac6e914b12}
    - {anchor_id: NAPMS-S0-RC-CURATION-JOURNEY, semantic_fingerprint: sha256-jcs-v1:5401681959c4ef07ce2b990b28ff2df1ee2eb5756b3d6355b641ab4f0f5bd475}
    derivation_rule_or_method: stakeholder-correction-of-earlier-S1-transcription
    derivation_kind: refinement
    rationale: >-
      The stakeholder corrected the earlier S1 transcription and confirmed the MVP rule already represented by the canonical Resource realization model: zero or one effective HostAddress-or-Prefix per Resource at a logical time.
  recorded_at: '2026-09-17'
status: ACCEPTED
validation:
  freshness: CURRENT
  evidence_ref: docs-v2/migration/revalidated/h12-rc-curation/validation/s1-cardinality-correction-validation.yaml
  evidence_target: NAPMS-S1-RC-CURATION-BEHAVIOR
  profile: changed-and-affected-design
  profile_version: cp-v2
  enforcement_status: specification-manual-not-CI
---
