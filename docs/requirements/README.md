# Requirements map

This directory contains current accepted product and quality behavior only.

Use the smallest requirement family that owns the behavior under change:

- `access-policy-core.md` — proposal, authoritative Access Rule, Rule reads/mutations and effective desired-policy behavior.
- `policy-export-core.md` — coherent logical-as-of normalized desired-policy export.
- `connectivity-requirements-core.md` + acceptance examples — Connectivity Requirements.
- `requirement-policy-alignment.md` + acceptance examples — derived Requirement-to-Policy Alignment.
- `connectivity-decision-core.md` + acceptance examples — Connectivity Decision.
- `scoped-connectivity-inventory.md` — resource-centric cross-context inventory/product behavior.
- `technical-access-evidence-core.md` — source-qualified Technical Access Evidence recording/query behavior.
- `network-enforcement-placement-core.md` — Network Enforcement Placement behavior.
- `enterprise-identity-authoritative-sources.md` — local-first operation plus optional external identity/source extension seams.
- `catalogue-curation.md` + acceptance/security contracts — implemented Resource/Application catalogue curation baseline.
- `application-catalogue-target.md` — accepted Application Definition / Application Deployment product behavior and migration-safety requirements.
- `web-ui-requirements.md` — product-facing Web UI information architecture and interaction requirements.

Access Policy Realization requirements are currently being revalidated from the single problem statement in `../domain/access-policy-realization/README.md`. Do not use removed APR requirement families as target behavior.

Historical Wave-1 G2 requirement packets are not living product truth. Their accepted outcomes were absorbed into the current files above, DDD/ADRs, implementation and executable evidence; provenance remains in `docs/baseline/` and Git history.

Do not restate domain identity/lifecycle ownership here when a domain artifact already owns the meaning. Requirements own observable behavior and quality outcomes.
