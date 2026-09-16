# Code structure

Status: `current target structure with explicit as-built compatibility boundaries`.

Decision: `docs/decisions/ADR-014-target-code-structure-taxonomy.md`.

## Purpose

Repository paths make semantic ownership and dependency direction visible while allowing current as-built compatibility code to coexist with the accepted target.

The exact implemented runtime is documented by `current-architecture.md` and engineering contracts. This document defines structural target rules.

## Repository structure

```text
napms/
  backend/
    src/napms/
      contexts/
      workflows/
      platform/
    tests/
  web/
  e2e/
  deploy/
  tools/
  docs/
  .agents/
  .github/
  Makefile
```

## Backend taxonomy

### `contexts/`

Authoritative semantic owners live under:

```text
contexts/<context>/
  domain/
  application/
  infrastructure/
  presentation/
```

Create only layers with real responsibility.

Current target context owners are:

- `access_policy`;
- `access_policy_realization`;
- `application_catalogue`;
- `application_deployment`;
- `authority_management`;
- `business_connectivity`;
- `network_enforcement_placement`;
- `network_environment_operations`;
- `resource_catalogue`;
- `technical_access_evidence`.

There is no target `access_governance` context package. Proposal/formal-decision/current-rule semantics belong to `access_policy`. Any implementation package with older governance/decision vocabulary is compatibility-only until removed.

Current compatibility modules such as `connectivity_requirements`, `connectivity_decision`, legacy ACC deployment models or older APR/runtime structures remain reconstructable where implemented, but they are not target semantic owners.

One context never imports another context's private Domain or persistence model. Cross-context interaction uses explicit application contracts/ports and opaque semantic references.

### Access Policy target/legacy coexistence

The first target implementation keeps legacy `AccessRule` behavior and new target `PolicyRule/RuleChange` behavior mechanically distinct inside the same `access_policy` BC until an explicit migration is accepted.

Target semantics include only one formal RuleChange decision:

```text
Pending -> Accepted | Rejected
```

Do not introduce `access_governance`, source/destination approval modules, ApprovalBasis infrastructure or ResourceScope-based approval-routing packages as baseline target structure.

Customer-specific approval workflow integrations, if later required, belong to an outer adapter/workflow that invokes AP's formal decision application contract; they do not redefine AP Domain ownership.

### `workflows/`

`workflows/` contains explicit cross-context orchestration/read composition with no authoritative business truth:

```text
workflows/<workflow>/
  application/
  infrastructure/
  presentation/
```

A workflow may own rebuildable/TTL read artifacts, but does not acquire business identity/lifecycle merely by combining contexts and may not bypass owner contracts through direct persistence access.

The selected Full Vendor-Neutral Policy Export reuses `workflows/policy_export/`. It composes current effective target AP Rules with ACC + AD + RC and produces complete source/destination AddressSpace plus traffic rows without NEP/device/provider semantics. A short-lived workflow-owned ExportResult supports same-result JSON/table and CSV.

Evidence Access Recognition, when implemented, is another non-authoritative workflow/composition over TAE + RC + AD + ACC that produces candidates for AP rather than writing AP persistence directly.

### Compatibility and migration adapters

Compatibility adapters are allowed only where current as-built contracts need translation during migration.

Rules:

- place them in the consuming/owning outer layer, not a new semantic top-level bucket;
- consume public owner contracts where possible, never peer-private persistence;
- translate only when meaning is exact; ambiguous/unrepresentable state fails explicitly;
- do not create independent business identity/lifecycle;
- do not make compatibility vocabulary authoritative for target contracts;
- document the adapter while current runtime depends on it.

Legacy ACC compatibility ComponentDeployment IDs are never target AD ComponentDeployment IDs. Legacy AccessRule rows are never silently target PolicyRules. Target mutations do not dual-write legacy semantic state.

### `platform/`

`platform/` contains process/execution concerns only:

```text
platform/
  bootstrap/
  auth/
  database/
  http/
  observability/
```

`platform` never owns feature/domain behavior.

## Dependency direction

```text
domain
  <- application
      <- infrastructure / presentation
          <- platform/bootstrap wiring
```

Rules:

- Domain has no framework, persistence, transport, configuration, logging or DI dependencies.
- Application depends on its own Domain and explicit consumer-owned ports/contracts.
- Infrastructure/Presentation depend inward.
- Bootstrap wires concrete outer adapters.
- Cross-context interaction uses application contracts/ports.
- Workflows do not read/write peer-private persistence.
- PostgreSQL colocation does not imply shared ownership.
- A coherent cross-context snapshot exists only where Architecture explicitly accepts it.
- No service locator/global mutable dependency registry.

## Shared-code rule

Do not create a generic shared business-model/utilities package. Technical reuse belongs in narrow technical capabilities; semantic reuse stays behind owner contracts. A Shared Kernel requires an explicit domain decision.

## Provider integration capabilities

Provider Policy Interpreter and Provider Policy Renderer remain integration capabilities rather than Bounded Contexts. Provider-native semantics stay outside source-neutral domain models.

## Frontend taxonomy

```text
web/src/
  app/
  design-system/
  features/<feature>/
  components/
  lib/
```

Feature DTOs/domain-to-visual mapping remain feature-local. `design-system/` stays generic and domain-independent.

Target first-MVP features may include:

```text
features/business-connectivity/
features/component-deployments/
features/policy-rules/
features/policy-export/
```

Policy UI reflects target `Pending | Accepted | Rejected` RuleChange semantics and must not invent bilateral approval stages.

## Structural change rules

- Preserve accepted product/domain semantics unless the owning layer changes first.
- Put new authoritative code under its final semantic owner.
- Do not create transitional semantic top-level categories.
- Keep compatibility adapters only while required and document them.
- Move matching tests with their implementation boundary.
- Add/update architecture tests for mechanically enforceable boundaries.
- File size alone is not a decomposition rule.
- A physical move never silently transfers semantic ownership.

## Mechanical enforcement

Architecture checks should protect at least:

- allowed target context taxonomy (no authoritative `access_governance` package);
- Domain framework/persistence independence;
- cross-context Domain isolation;
- AP peer access through AP-owned ports;
- no AP Domain dependency on RC ResourceScopeAffiliation for baseline RuleChange decision;
- no source/destination approval-side or ApprovalBasis target model;
- target AD isolation from ACC compatibility deployment types;
- no peer-private persistence access;
- policy export isolation from NEP/APR/NEO/provider semantics;
- provider-specific code outside source-neutral domain models;
- design-system independence from feature/domain semantics.

## Reconstruction rule

This target structure plus `current-architecture.md`, current ADRs and engineering contracts must be sufficient to recreate both the as-built topology and accepted target ownership. Do not delete structural documentation merely because corresponding code has been implemented.
