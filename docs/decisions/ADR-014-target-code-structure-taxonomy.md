# ADR-014 — Target code structure taxonomy

Status: `accepted current target decision; semantic classification revalidated 2026-09-16`.

## Context

The semantic-module-first layout preserves DDD ownership, but top-level backend paths must distinguish bounded contexts, cross-context workflows and technical runtime mechanics. The 2026-09-16 DDD revalidation also changed target ownership: Access Governance is now an internal Access Policy capability, and target Application Deployment owns concrete ComponentDeployment identity.

The target is optimized for long-term readability/boundary enforcement rather than migration convenience.

## Decision

Keep NAPMS as a modular monolith and make architectural kind explicit:

```text
backend/src/napms/
  contexts/       # bounded contexts / authoritative semantic owners
  workflows/      # cross-context application/read compositions; no authoritative business truth
  platform/       # bootstrap/runtime/config/auth/database/http support
```

A bounded context uses Clean Architecture locally:

```text
contexts/<context>/
  domain/
  application/
  infrastructure/
  presentation/
```

Only layers with actual responsibility are created.

A workflow normally uses:

```text
workflows/<workflow>/
  application/
  infrastructure/
  presentation/
```

A workflow may own rebuildable/read-result persistence required by its composition, but it does not own authoritative domain facts. Independent business identity/lifecycle/invariants are evidence to revisit the Bounded Context model.

`platform` owns technical process concerns only. Product behavior does not migrate there merely because several contexts need wiring.

There is no generic top-level `composition/` and no general shared business-model package. Cross-context reuse is through explicit consumer-owned ports/contracts. A DDD Shared Kernel requires an explicit later decision.

## Dependency rules

```text
domain
  <- application
      <- infrastructure / presentation
          <- platform/bootstrap wiring
```

Additional rules:

- one target context does not import another context's domain/private persistence;
- cross-context dependencies use explicit application contracts/ports;
- workflow application code owns projection contracts and does not import peer domain models;
- workflows never bypass context ownership through direct peer-table access;
- platform cannot become a feature/domain owner;
- infrastructure/presentation do not define authoritative business semantics;
- physical database colocation does not create shared ownership.

## Current target bounded contexts

- Business Connectivity;
- Access Policy;
- Authority Management;
- Resource Catalogue;
- Application Communication Catalogue;
- Application Deployment;
- Network Enforcement Placement;
- Technical Access Evidence;
- Access Policy Realization;
- Network Environment Operations.

`Access Governance` is no longer a separate target Bounded Context. RuleChange proposal/approval/rejection/withdrawal behavior belongs to Access Policy.

Provider Policy Interpreter, Provider Policy Renderer and Technical Evidence Acquisition/Collectors remain integration/application capabilities.

## Target contexts requiring new physical packages in the selected policy-authoring path

The implemented runtime does not yet provide target packages for:

```text
contexts/business_connectivity/
contexts/application_deployment/
```

Those target owners must be introduced rather than implemented by relabelling legacy `connectivity_requirements` or ACC compatibility deployment state.

`contexts/access_policy/` already exists, but the first migration step must keep its implemented legacy `AccessRule` model beside the new target `PolicyRule/RuleChange` model until the compatibility APIs are retired.

## Target workflows/compositions

Current target workflow/composition classification includes:

- **Full Vendor-Neutral Policy Export** — selected first implementation workflow; consumes target current effective Access Policy plus ACC/AD/RC semantics and AM only for the privileged export read guard;
- **Required Policy Materialization** — derived composition for target-specific realization/APR;
- **Evidence Access Recognition** — non-authoritative TAE + RC + AD + ACC correlation producing candidates for Access Policy; accepted target composition but not part of the first export G4 scope by default;
- Scoped Connectivity Inventory — retained as-built/non-peer read composition where current behavior requires it;
- Traffic Analysis Checker — retained composition where current behavior requires it;
- Requirement-to-Policy Alignment — compatibility path only while its as-built contracts remain required.

The existing `workflows/policy_export/` package is reused for the new target export path. Its old normalized-policy path remains as-built compatibility; the new path must use separate target contracts/result persistence and must not silently change `/api/v1/normalized-policy` semantics.

## Workflow-owned read artifacts

A workflow may persist a non-authoritative immutable read result when required by observable behavior. For the selected export:

```text
VendorNeutralPolicyExportResult
    exportId
    rows
    capture/source provenance
    expiresAt
```

is workflow-owned short-lived state used so JSON/table and CSV serialize the same materialization. It does not become a Bounded Context or policy authority.

## Compatibility classification

Current runtime packages such as `connectivity_requirements`, `connectivity_decision`, legacy ACC `ApplicationDeployment`/`DeploymentInteraction`/compatibility ComponentDeployment and legacy APR/operator structures remain as-built reconstruction/migration inputs.

Their physical presence does not make them target semantic owners.

The same term `ComponentDeployment` currently exists in compatibility runtime and target AD semantics with different meaning. Target code must keep those types/modules mechanically distinguishable until migration is complete.

No target mutation dual-writes an incompatible legacy semantic model merely for compatibility.

## Repository target

```text
napms/
  backend/
    pyproject.toml
    Dockerfile
    src/napms/
    tests/
  web/
  e2e/
  deploy/
  tools/
  docs/
  .agents/
  .github/
  Makefile
  README.md
```

The root Makefile remains the repository-level orchestration entry point.

## Alternatives

- Keep target BCs directly mixed with workflows/runtime under one generic package: rejected because ownership and architectural role become ambiguous.
- Global `domain/application/infrastructure` directories: rejected because they scatter Bounded Contexts across technical layers.
- Service per BC: rejected; no accepted topology driver requires distributed deployment.
- Retain Access Governance as a physical target module after domain ownership merged into Access Policy: rejected because package shape must not recreate superseded authority.
- Reuse legacy ACC compatibility ComponentDeployment as target AD storage: rejected because identity/Resource cardinality semantics differ.

## Consequences

Positive:

- path indicates both semantic owner and architectural role;
- new BCs are introduced explicitly instead of hidden behind legacy adapters;
- AP target/legacy coexistence can be mechanically guarded;
- cross-context orchestration remains visible;
- table/CSV same-result behavior has an explicit workflow state owner without inventing a BC.

Costs:

- temporary side-by-side target and compatibility models increase code surface;
- new BC persistence/API packages are required for BC and AD;
- architecture tests and CI rules must distinguish target from compatibility imports;
- later migration/removal remains a separately authorized change.

## Reconstruction rule

This ADR defines target physical taxonomy. `docs/architecture/current-architecture.md` and current engineering/API contracts remain authority for the as-built runtime during migration. Compatibility documentation is removed only after the implemented compatibility behavior is actually retired and reconstruction remains possible.
