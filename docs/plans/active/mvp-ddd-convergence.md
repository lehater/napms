# First MVP vertical — DDD convergence

Status: `completed — G2 PASS 2026-09-15; parked at design`.

Date: 2026-09-15.

## Goal

Finish the DDD needed by the first MVP vertical before any further code work.

Result: **complete for the accepted first MVP happy path**.

The earlier attempted downstream S3/S4 plans were revoked after the project-owner instruction to complete DDD first. Their Git history remains available as non-authoritative evidence, but they are no longer active/current artifacts.

## Lifecycle correction

The first vertical had moved toward implementation before the full target DDD baseline was actually closed. The project-owner instruction on 2026-09-15 returned the work to S2 and revoked the previous G4 implementation lease.

The convergence pass then found and resolved more than the initially visible AD/APR gaps:

- Application Deployment lacked target Tactical DDD;
- Access Policy Realization still classified MVP Tactical meaning as open;
- ACC requirements required immutable InteractionContractRevision while the target domain document had deferred that identity;
- Authority Management had no canonical target Tactical DDD;
- Business Connectivity was still only a Tactical candidate despite its remaining questions being non-blocking;
- stale Scoped Connectivity / realization requirements still reintroduced `ComponentDeployment -> exactly one Resource` and endpoint-era semantics;
- strategic/machine-readable maps retained stale Tactical-open and S1-open statements.

These conflicts are now closed in canonical target artifacts.

## Final target scope

```text
Business Connectivity Need -> stable ACC Interaction

ACC InteractionContractRevision
-> AD ApplicationDeployment / complete ComponentPlacement set
-> RC Resource / AddressSpace
-> AG bilateral authorization
-> AP current Policy Rule
-> RPM derived TargetRequiredPolicy
-> APR realization assessment / additive VerifiedChangeIntent
-> Provider Policy Renderer boundary
-> NEO controlled mutation semantics

AM -> effective authority for protected actions
TAE -> source-qualified technical evidence
PPI -> configured effective policy interpretation
```

## Completed Tactical work

### Application Deployment

Closed in `docs/domain/application-deployment/tactical-model.md`:

- stable ApplicationDeployment identity/continuity;
- ComponentPlacement is the relation value `(ComponentRef, ResourceRef)`;
- zero/one/many placements per Component are valid;
- exact duplicate relations are not;
- complete current placement set is authoritative AD truth;
- empty current set and unresolved truth are distinct;
- scaling/migration does not by itself change deployment identity;
- richer lifecycle/history is explicitly deferred because the MVP does not require it.

### Access Policy Realization

Closed in `docs/domain/access-policy-realization/tactical-model.md`:

- ComparisonScope / PermitSpace / SemanticDelta / Assessment / VerifiedChangeIntent classification;
- exact Realized/Drift/Uncomparable invariants;
- additive-only ENSURE-PERMIT semantics;
- `excess` is evidence, not removal authority;
- semantic verification of additive effect;
- assessment/delta/intent require no invented durable aggregate/lifecycle;
- scale/persistence/migration are downstream concerns, not missing Tactical DDD.

### Application Communication Catalogue

Closed the immutable revision contradiction in `target-tactical-model.md`:

- Interaction is stable directed component-pair identity;
- material traffic change creates a new immutable InteractionContractRevision;
- old revisions remain historically resolvable;
- one revision's full traffic-alternative set is atomic;
- no rich revision workflow/version numbering is required for MVP.

### Authority Management

Added canonical `docs/domain/authority-management/tactical-model.md`:

- exact actor/action/scope/time authority meaning;
- Group Membership + Role Assignment @ ResponsibilityScope + Role permits Action;
- temporal assignment/membership evidence;
- Admitted / Denied / Unknown distinction;
- Unknown fails closed;
- Resource responsibility metadata is never authority;
- no speculative nested-group/deny/ABAC/quorum framework.

### Business Connectivity

Closed the existing target candidate without inventing future workflow:

- stable BusinessProcess and ConnectivityNeed identity;
- Need references stable Interaction meaning, not one deployment/address/revision;
- current business justification is distinct from authorization/realization;
- exact concrete revision remains AG/ACC governed-subject truth;
- remaining process/criticality/duplicate-Need questions are non-blocking extensions.

## Cross-context consistency work

Updated current canonical artifacts so they no longer reintroduce superseded semantics:

- `docs/domain/context-map.md`;
- `docs/domain/strategic-model.md`;
- `docs/domain/strategic-model.json`;
- `docs/domain/semantic-ownership.md`;
- `docs/domain/resource-role-model.md`;
- `docs/requirements/README.md`;
- `docs/requirements/scoped-connectivity-inventory.md`;
- `docs/requirements/scoped-connectivity-inventory-acceptance-examples.md`;
- `docs/requirements/policy-realization-reconciliation-g1.md`.

## Gate result

Canonical checkpoint: `docs/domain/mvp-ddd-convergence-checkpoint.md`.

```text
Lifecycle stage: S2
Stage state: ACCEPTED
G2: PASS
Implementation authorization: none
```

G2 PASS is for the first MVP target DDD baseline across all 11 target Bounded Contexts. It does not claim that all conceivable future product extensions have been modelled.

## Explicit non-blocking deferrals

- generalized overlapping Responsibility Scope approval algebra;
- nested groups/role inheritance/explicit deny/ABAC/quorum authority semantics;
- richer BusinessProcess criticality/lifecycle/duplicate-Need behavior;
- richer ApplicationDeployment lifecycle/history;
- ACC revision draft/publish/version-number workflow;
- Prefix-aware NEP;
- multiple simultaneous Resource addresses/interfaces/VIPs/exposure;
- managed-policy removal/narrowing;
- richer APR change vocabulary/durable remediation plans;
- provider transport, persistence, migration, transaction and package architecture.

These reopen only on concrete requirement pressure.

## Stop condition

Do not continue to S3, S4 or implementation from this plan.

No production code, tests, schemas, migrations, adapters, bootstrap, HTTP or UI changes are authorized. The branch diff against `main` is documentation-only at this checkpoint.

A later architecture or implementation phase requires an explicit new project-owner request and a new downstream lifecycle decision from this G2 baseline.
