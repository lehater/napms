# Requirements map

This directory is a working knowledge base for current accepted product and quality behavior. Superseded specifications are removed rather than retained beside target requirements. Git history is the archive.

Use the smallest requirement family that owns the behavior under change:

- `business-connectivity-g1.md` — current observable behavior for Business Process, Connectivity Need and brownfield business attribution.
- `access-governance-g1.md` — current observable behavior for Access Request, bilateral source/destination approval, authority integration and revocation.
- `access-policy-core.md` — authoritative Policy Rule truth and effective authorized-policy projection after Access Governance grant/withdrawal.
- `application-catalogue-domain-target.md` — ACC target for ComponentDeployment, exactly-one-Resource MVP binding and immutable interaction contracts.
- `policy-realization-reconciliation-g1.md` — current cross-capability behavior for semantic-to-technical materialization, normalized required/configured comparison and convergence semantics.
- `scoped-connectivity-inventory.md` + acceptance examples — resource-centric composition over Resource/Deployment, Business Need, Access Governance, Access Policy and realization truth.
- `policy-export-core.md` — coherent logical-as-of normalized desired-policy export; implementation-specific assumptions must be revalidated when its downstream design changes.
- `technical-access-evidence-core.md` — source-qualified Technical Access Evidence recording/query behavior.
- `network-enforcement-placement-core.md` — accepted Network Enforcement Placement behavior.
- `enterprise-identity-authoritative-sources.md` — local-first operation plus optional external identity/source extension seams.
- `catalogue-curation.md` + acceptance/security contracts — implemented Resource/Application catalogue curation behavior; current target ACC semantics are owned by `application-catalogue-domain-target.md` where they differ.
- `web-ui-requirements.md` — product-facing UI requirements expressed in current target terminology.

Connectivity Requirements, Connectivity Decision and Requirement-to-Policy Alignment requirement packets were removed after revalidation replaced their target semantics with Business Connectivity, Access Governance and the current policy/materialization chain. Their runtime remnants are migration/current-state evidence only and must not be reintroduced as target requirements.

`application-catalogue-target.md` may remain only where it carries migration/current-state information not yet represented by the target ACC model; target design must prefer `application-catalogue-domain-target.md` on conflict.

The consolidated stakeholder/G1 checkpoint is `../engineering/context-problems/capability-revalidation-checkpoint-2026-09-14.md`. Access Policy Realization Tactical DDD remains under revalidation from `../domain/access-policy-realization/README.md`.

Requirements own observable behavior and quality outcomes. Do not promote S2 aggregate/state/storage choices or current implementation mechanics into requirements merely because they already exist.
