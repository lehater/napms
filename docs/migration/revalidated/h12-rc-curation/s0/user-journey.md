---
anchor_id: NAPMS-S0-RC-CURATION-JOURNEY
type_id: user-journey
owner_stage: S0
scope:
  scope_id: H12-RC-CURATION-MVP
  product_area: Resource Catalogue curation
  lifecycle_boundary: S0 problem and actor/goal journey
status: ACCEPTED
canonical_payload: |-
  # Resource Catalogue self-service onboarding journey

  ## Actor

  A responsible local catalogue user who is admitted to perform the applicable catalogue-curation workflow.

  ## Goal

  Make a new or changed access-relevant Resource usable by normal NAPMS access workflows without direct database/seed edits.

  ## Journey

  1. Register or identify the Resource through a supported product workflow.
  2. Supply or maintain the Resource realization information needed by downstream access workflows.
  3. Associate the Resource with relevant Responsibility Scope information when needed.
  4. Maintain operational responsibility/contact information when needed.
  5. Inspect the resulting Resource catalogue representation through the supported product.
  6. Use the Resource from the existing downstream connectivity/access workflow.

  ## Successful outcome

  The Resource can participate in the intended NAPMS access workflow through supported catalogue curation, and routine onboarding no longer depends on out-of-band seed/SQL edits.

  ## Scope boundary

  This S0 journey preserves actor, goal, broad flow and intended outcome only. Exact observable curation behavior and cardinalities belong to S1; domain ownership and invariants belong to S2; API, persistence and UI realization belong to S3.
provenance:
  origin_kind: mixed
  source_refs:
    - kind: repository-file
      path: docs/requirements/catalogue-curation.md
      blob_sha: 92833e29efc3bfdb6503e5b600e48296b8fb6041
    - kind: repository-file
      path: docs/requirements/catalogue-curation-acceptance-examples.md
      blob_sha: c98ab5174740b890c9b4b240530f1b9eec89cc91
  recorded_at: 2026-09-17
  authority_basis: imported-current-docs-ref-before-cutover
  derivation:
    input_anchor_refs:
      - anchor_id: NAPMS-S0-RC-CURATION-PROBLEM
        semantic_fingerprint: sha256-jcs-v1:b7b3162275fcd1df95904284f6846412278f332d3393e2aa8e9786ac6e914b12
    derivation_rule_or_method: DOCS-V2-HUMAN-KNOWLEDGE-ACQUISITION.user_journey_enrichment
    derivation_kind: refinement
    rationale: >-
      The accepted current requirement states the responsible-user catalogue onboarding workflow
      and the desired end-to-end outcome. This journey narrows that accepted flow to the Resource
      Catalogue migration slice without adding S1 behavior or S2/S3 design choices.
semantic_refs:
  - relation: DERIVES_FROM
    target: {kind: anchor-current, anchor_id: NAPMS-S0-RC-CURATION-PROBLEM}
    impact: semantic
    rationale_ref: provenance.derivation.rationale
semantic_fingerprint: sha256-jcs-v1:5401681959c4ef07ce2b990b28ff2df1ee2eb5756b3d6355b641ab4f0f5bd475
validation:
  freshness: CURRENT
  evidence_ref: docs-v2/migration/revalidated/h12-rc-curation/validation/s0-change-set-validation-v2.yaml
  evidence_target: NAPMS-S0-RC-CURATION-JOURNEY
  validated_fingerprint: sha256-jcs-v1:5401681959c4ef07ce2b990b28ff2df1ee2eb5756b3d6355b641ab4f0f5bd475
  profile: change-set-anchor-acceptance
  profile_version: cp-v1
  enforcement_status: specification-manual-not-CI
---
