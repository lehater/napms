# Requirements map

This directory contains current accepted product and quality behavior only.

Use the smallest requirement family that owns the behavior under change:

- `access-policy-core.md` — proposal, authoritative Access Rule, Rule reads/mutations and effective desired-policy behavior.
- `policy-export-core.md` — coherent logical-as-of normalized desired-policy export.
- `connectivity-requirements-core.md` + acceptance examples — legacy Connectivity Requirements packet; its capability content is under G1 revalidation and must not override the 2026-09-14 passports below.
- `requirement-policy-alignment.md` + acceptance examples — derived Requirement-to-Policy Alignment; revalidate against the new Need/authorization semantics before extending it.
- `connectivity-decision-core.md` + acceptance examples — legacy Connectivity Decision packet; the old single-decision model is under G1 revalidation and must not override bilateral approval semantics.
- `business-connectivity-g1.md` — current G1 observable behavior for Business Process, Connectivity Need and brownfield business attribution; BC grouping remains open.
- `access-governance-g1.md` — current G1 observable behavior for Access Request, bilateral source/destination approval, role/scope authority integration and revocation; BC grouping remains open.
- `policy-realization-reconciliation-g1.md` — current cross-capability G1 behavior for semantic-to-technical materialization, normalized required/observed comparison and convergence semantics; ownership remains open.
- `scoped-connectivity-inventory.md` — resource-centric cross-context inventory/product behavior.
- `technical-access-evidence-core.md` — source-qualified Technical Access Evidence recording/query behavior.
- `network-enforcement-placement-core.md` — Network Enforcement Placement behavior.
- `enterprise-identity-authoritative-sources.md` — local-first operation plus optional external identity/source extension seams.
- `catalogue-curation.md` + acceptance/security contracts — implemented Resource/Application catalogue curation baseline.
- `application-catalogue-target.md` — accepted Application Definition / Application Deployment product behavior and migration-safety requirements; revalidate any older optional/multi-Resource Deployment binding against the 2026-09-14 MVP exactly-one-Resource evidence before using it as target behavior.
- `web-ui-requirements.md` — product-facing Web UI information architecture and interaction requirements.

The consolidated stakeholder/G1 checkpoint for the current breadth-first revalidation is `../engineering/context-problems/capability-revalidation-checkpoint-2026-09-14.md`. It records cross-capability semantics, explicit non-inferences and unresolved S2/boundary questions so that detailed legacy documents cannot silently reintroduce superseded assumptions.

Access Policy Realization requirements are currently being revalidated from the single problem statement in `../domain/access-policy-realization/README.md`. Do not use removed APR requirement families as target behavior. The current realization/reconciliation passport also records newly confirmed normalization and desired-vs-observed semantics that APR/TAE/NEO documents must be checked against.

Historical Wave-1 G2 requirement packets are not living product truth. Their accepted outcomes were absorbed into the current files above, DDD/ADRs, implementation and executable evidence; provenance remains in `docs/baseline/` and Git history.

Do not restate domain identity/lifecycle ownership here when a domain artifact already owns the meaning. Requirements own observable behavior and quality outcomes. During this revalidation, detailed S2/architecture/storage choices in older documents are not promoted to requirements merely because they already exist.
