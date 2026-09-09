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
- `technical-domain-access-resolution.md` + acceptance examples — I18 Technical-to-Domain Access Resolution.
- `network-enforcement-placement-core.md` — I19 Network Enforcement Placement behavior.
- `access-policy-realization-reconciliation.md` + acceptance examples — I20 desired enforcement derivation and desired-vs-configured reconciliation.
- `enterprise-identity-authoritative-sources.md` — I23 enterprise authentication, actor mapping and Authority/ACC/Resource authoritative-source integration behavior.
- `web-ui-requirements.md` — product-facing Web UI information architecture and interaction requirements.

Historical Wave-1 G2 requirement packets are not living product truth. Their accepted outcomes were absorbed into the current files above, DDD/ADRs, implementation and executable evidence; provenance remains in `docs/baseline/` and Git history.

Do not restate domain identity/lifecycle ownership here when a domain artifact already owns the meaning. Requirements own observable behavior and quality outcomes.
