# Requirements map

This directory contains current product and quality contracts. A requirement remains current project documentation after implementation if it is still required to reproduce the system's behavior.

## Selected next implementation slice

- `first-mvp-required-access-matrix.md` — ACC + AD + RC -> global vendor-neutral Required Access Matrix -> table/export.

## Current target contracts

- `application-catalogue-domain-target.md` — current ACC/AD/RC target behavior and ownership split.
- `business-connectivity-g1.md` — Business Connectivity behavior.
- `access-governance-g1.md` — Access Governance behavior.
- `access-policy-core.md` — Access Policy behavior.
- `network-enforcement-placement-core.md` — Network Enforcement Placement behavior.
- `technical-access-evidence-core.md` + `technical-access-evidence-acceptance-examples.md` — Technical Access Evidence behavior.
- `policy-realization-reconciliation-g1.md` + `access-policy-realization-mvp.md` — Access Policy Realization behavior.
- `provider-policy-renderer-mvp.md` — provider rendering boundary.
- `network-environment-operations.md` — Network Environment Operations behavior.
- `enterprise-identity-authoritative-sources.md` — authoritative-source extension boundary.

## Current as-built product contracts

These remain because they describe implemented behavior that must be reproducible even where later target semantics differ:

- `application-catalogue-target.md` — implemented Application Definition / Application Deployment product behavior.
- `catalogue-curation.md` + security/acceptance examples — implemented Application/Resource catalogue curation behavior.
- `scoped-connectivity-inventory.md` + acceptance examples — implemented resource-centric connectivity composition.
- `traffic-analysis-checker.md` — implemented Checker behavior.
- `policy-export-core.md` — implemented normalized desired-policy export behavior.
- `web-ui-requirements.md` — current Web behavior, including explicit as-built compatibility boundaries.

As-built contracts do not override newer target ownership or vocabulary. They document what must be reproduced when rebuilding the current system; target contracts document the accepted intended design.

The selected implementation scope is narrower than both the complete target model and the already implemented product. That does not make either class of requirement historical.

Git history is the archive only for requirements that no longer describe any current as-built or target behavior.
