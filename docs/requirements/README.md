# Requirements map

This directory is a working knowledge base for current accepted product and quality behavior. Superseded specifications are removed rather than retained beside target requirements. Git history is the archive.

Use the smallest requirement family that owns the behavior under change:

- `business-connectivity-g1.md` — current observable behavior for Business Process, Connectivity Need and brownfield business attribution.
- `access-governance-g1.md` — current observable behavior for Access Request, bilateral source/destination approval, authority integration and withdrawal.
- `access-policy-core.md` — authoritative Policy Rule truth and effective authorized-policy projection after Access Governance grant/withdrawal.
- `application-catalogue-domain-target.md` — ACC Application/Component/Interaction plus immutable InteractionContractRevision behavior, and the accepted ACC/AD/RC ownership split.
- `policy-realization-reconciliation-g1.md` — current semantic-to-technical materialization, normalized required/configured comparison and convergence behavior.
- `scoped-connectivity-inventory.md` + acceptance examples — resource-centric composition over RC Resources, AD placements, Business Need, Access Governance, Access Policy and realization truth.
- `policy-export-core.md` — coherent logical-as-of normalized desired-policy export; implementation-specific assumptions must be revalidated when downstream target design changes.
- `technical-access-evidence-core.md` — source-qualified Technical Access Evidence recording/query behavior.
- `network-enforcement-placement-core.md` — accepted Network Enforcement Placement behavior.
- `enterprise-identity-authoritative-sources.md` — local-first operation plus optional external identity/source extension seams.
- `catalogue-curation.md` + acceptance/security contracts — implemented Resource/Application catalogue curation behavior; current target ACC/AD/RC semantics win where legacy curation/runtime vocabulary differs.
- `web-ui-requirements.md` — product-facing UI requirements; stale ComponentDeployment/endpoint terminology must not override current target domain contracts.

Connectivity Requirements, Connectivity Decision and Requirement-to-Policy Alignment requirement packets were removed after revalidation replaced their target semantics with Business Connectivity, Access Governance and the current policy/materialization chain. Their runtime remnants are migration/current-state evidence only and must not be reintroduced as target requirements.

`application-catalogue-target.md` may remain only where it carries migration/current-state information not represented by the target ACC/AD model; target design must prefer `application-catalogue-domain-target.md` on conflict.

The consolidated stakeholder/G1 checkpoint is `../engineering/context-problems/capability-revalidation-checkpoint-2026-09-14.md`; it is provenance for the revalidation, not authority over later accepted requirement/domain corrections recorded on 2026-09-15.

Current target Tactical DDD owners include:

- `../domain/application-communication-catalogue/target-tactical-model.md`;
- `../domain/application-deployment/tactical-model.md`;
- `../domain/resource-catalogue/tactical-model.md`;
- `../domain/business-connectivity/target-tactical-model.md`;
- `../domain/access-governance/target-tactical-model.md`;
- `../domain/access-policy/tactical-model.md`;
- `../domain/authority-management/tactical-model.md`;
- `../domain/network-enforcement-placement/target-tactical-model.md`;
- `../domain/technical-access-evidence/tactical-model.md`;
- `../domain/access-policy-realization/tactical-model.md`;
- `../domain/network-environment-operations/tactical-model.md`.

Requirements own observable behavior and quality outcomes. Do not promote S2 aggregate/state/storage choices or current implementation mechanics into requirements merely because they already exist.
