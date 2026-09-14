# Requirements map

This directory contains current accepted product and quality behavior plus explicitly marked legacy/current-implementation packets that must not override newer target requirements.

Use the smallest requirement family that owns the behavior under change:

- `business-connectivity-g1.md` — current G1 observable behavior for Business Process, Connectivity Need and brownfield business attribution; BC grouping remains open.
- `access-governance-g1.md` — current G1 observable behavior for Access Request, bilateral source/destination approval, role/scope authority integration and revocation; BC grouping remains open.
- `access-policy-core.md` — current G1 target behavior for authoritative Policy Rule truth and effective authorized-policy projection after Access Governance grant/withdrawal.
- `application-catalogue-domain-target.md` — current G1 ACC target for ComponentDeployment, exactly-one-Resource MVP binding and atomic interaction contract publication; ADR/domain realization remains to be revalidated in S2.
- `policy-realization-reconciliation-g1.md` — current cross-capability G1 behavior for semantic-to-technical materialization, normalized required/observed comparison and convergence semantics; ownership remains open.
- `scoped-connectivity-inventory.md` + acceptance examples — current resource-centric composition over Resource/Deployment, Need, Access Governance, Access Policy and realization truth.
- `policy-export-core.md` — coherent logical-as-of normalized desired-policy export; revalidate implementation-specific Rule-state assumptions when its owning downstream design is revisited.
- `technical-access-evidence-core.md` — source-qualified Technical Access Evidence recording/query behavior.
- `network-enforcement-placement-core.md` — accepted Network Enforcement Placement behavior.
- `enterprise-identity-authoritative-sources.md` — local-first operation plus optional external identity/source extension seams.
- `catalogue-curation.md` + acceptance/security contracts — implemented Resource/Application catalogue curation baseline; current target ACC semantics are owned by `application-catalogue-domain-target.md` where they differ.
- `web-ui-requirements.md` — product-facing Web UI information architecture and interaction requirements; revalidate screens/actions that still expose superseded Requirement/Decision workflow semantics before implementation.

Legacy or dirty packets retained as evidence:

- `connectivity-requirements-core.md` + acceptance examples — legacy Connectivity Requirements packet; Process-backed application-semantic Connectivity Need behavior is now owned by `business-connectivity-g1.md`.
- `connectivity-decision-core.md` + acceptance examples — legacy single `Allowed | NotAllowed` Connectivity Decision packet; current authorization workflow is bilateral and owned by `access-governance-g1.md`.
- `requirement-policy-alignment.md` + acceptance examples — accepted historical I14 baseline; revalidate against current Connectivity Need and authorization semantics before extending or treating it as target behavior.
- `application-catalogue-target.md` — implemented I31 Application Deployment behavior retained for migration/current-state evidence; it is not the target ComponentDeployment model.

The consolidated stakeholder/G1 checkpoint is `../engineering/context-problems/capability-revalidation-checkpoint-2026-09-14.md`. It records cross-capability semantics, downstream invalidations and unresolved S2/boundary questions so older detailed documents cannot silently reintroduce superseded assumptions.

Access Policy Realization target Tactical DDD remains under revalidation from `../domain/access-policy-realization/README.md`. The current realization/reconciliation passport records the accepted normalized desired-vs-observed semantics that APR/TAE/NEO design must respect. Provider-specific rendering ownership remains a downstream design question and must not redefine G1 semantics.

Historical Wave-1 packets, current runtime/API contracts and implementation code are evidence of existing behavior, not automatic target truth when they conflict with the revalidated requirements above.

Requirements own observable behavior and quality outcomes. Do not promote S2 aggregate/state/storage choices or current implementation mechanics into requirements merely because they already exist.
