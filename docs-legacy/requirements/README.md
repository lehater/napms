# Requirements map

This directory contains current product and quality contracts. A requirement remains current project documentation after implementation if it is still required to reproduce the system's behavior.

## Selected next implementation slice

- `first-mvp-vendor-neutral-policy-export.md` — current effective policy over concrete source/destination Component Deployments + exact ACC revision + RC Resource/AddressSpace -> complete vendor-neutral table/CSV export without firewall/device/provider context.

## Current target contracts

- `application-catalogue-domain-target.md` — current Application/Component/Interaction behavior plus concrete Component Deployment and RC realization requirements for the target policy path.
- `business-connectivity-g1.md` — Business Connectivity behavior, including recognition before Process/Need attribution and Process-backed Need requirement for deliberate submission.
- `access-governance-g1.md` — proposal/change, bilateral governance, evidence-derived candidate and current-vs-proposed behavior.
- `access-policy-core.md` — current Policy Rule behavior for one concrete directed Component Deployment pair and exact effective revision.
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
- `policy-export-core.md` — implemented normalized desired-policy export behavior and reconstruction input for the selected target MVP.
- `web-ui-requirements.md` — current Web behavior, including explicit as-built compatibility boundaries.

As-built contracts do not override newer target ownership or vocabulary. They document what must be reproduced when rebuilding the current system; target contracts document the accepted intended design.

## Current lifecycle disposition

The affected first-MVP requirements passed G1 revalidation on 2026-09-16. The next lifecycle work is S2 Strategic/Tactical DDD revalidation of:

- ownership and identity of concrete Component Deployment;
- governance proposal/change history versus current Policy Rule ownership;
- cross-context contracts from ACC/RC/TAE into the access lifecycle;
- policy export/materialization references.

No implementation authorization is implied. Git history is the archive only for requirements that no longer describe any current as-built or target behavior.
