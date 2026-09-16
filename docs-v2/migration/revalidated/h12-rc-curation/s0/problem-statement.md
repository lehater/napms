---
anchor_id: NAPMS-S0-RC-CURATION-PROBLEM
type_id: problem-statement
owner_stage: S0
scope:
  scope_id: H12-RC-CURATION-MVP
  product_area: Resource Catalogue curation
  lifecycle_boundary: S0 problem and actor/goal journey
status: CANDIDATE
canonical_payload: |-
  # Resource Catalogue curation problem

  ## Need

  Normal local NAPMS users cannot onboard or maintain the access-relevant Resource catalogue through supported product workflows; the current supported onboarding path relies on out-of-band seed/database changes.

  ## Affected actor

  A responsible local catalogue user who needs to introduce or maintain access-relevant Resources for existing NAPMS access workflows.

  ## Desired outcome

  Provide a supported self-service path for maintaining the Resource catalogue knowledge needed by downstream Connectivity, Needs, Decisions, Rules, Checker and Realization workflows without direct seed/SQL edits.

  ## Scope boundary

  This S0 statement owns only the problem, actor and intended outcome. It does not define realization/address cardinality, domain boundaries, aggregate structure, API shape, persistence, UI layout or mutation-authority policy.

  ## Non-goal boundary

  The problem is not to build a generic CMDB or application-portfolio system; catalogue curation exists only to support NAPMS access outcomes.
provenance:
  origin_kind: imported-current-docs
  source_refs:
    - kind: repository-file
      path: docs/requirements/catalogue-curation.md
      blob_sha: 92833e29efc3bfdb6503e5b600e48296b8fb6041
  recorded_at: 2026-09-17
  authority_basis: imported-current-docs-ref-before-cutover
  root_basis: >-
    Current accepted product requirement explicitly states the self-service catalogue gap,
    affected responsible user workflow and intended access-domain outcome.
semantic_refs: []
semantic_fingerprint: sha256-jcs-v1:b7b3162275fcd1df95904284f6846412278f332d3393e2aa8e9786ac6e914b12
validation:
  freshness: NOT_VALIDATED
  profile: anchor-acceptance
  profile_version: h8-v1
  enforcement_status: specification-manual-not-CI
---
