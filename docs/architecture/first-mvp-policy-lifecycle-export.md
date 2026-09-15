# First MVP — Policy lifecycle and vendor-neutral export architecture

Status: `S3 target architecture candidate 2026-09-16`.

## Purpose

Realize the G1/G2-accepted first-MVP behavior without transferring semantic ownership:

```text
ACC Application / Component / Interaction / immutable revision
RC Resource / AddressSpace / ResponsibilityScope affiliation
AD concrete ComponentDeployment(ComponentRef, ResourceRef)
BC Process / ConnectivityNeed
AM EffectiveAuthority
        |
        v
AP PolicyRule + RuleChange governance/current-effect lifecycle
        |
        v
current effective PolicyRule set
        + ACC + AD + RC
        |
        v
Full Vendor-Neutral Policy Export
        -> JSON/table read model
        -> CSV
```

This architecture is for the target path. Existing normalized-policy export and ACC compatibility deployment semantics remain as-built contracts until explicitly migrated.

## Architecture style

Keep the existing modular monolith and Clean Architecture/Ports-and-Adapters direction:

```text
context domain
    <- context application / consumer-owned ports
        <- context infrastructure / presentation

cross-context workflow application
    <- workflow infrastructure / presentation

platform/bootstrap
    -> wires concrete outer adapters only
```

No service-per-context distribution, broker or new process boundary is required by the first MVP.

## Target backend ownership

```text
backend/src/napms/
  contexts/
    access_policy/
    application_deployment/
    application_catalogue/       # ACC target + current compatibility implementation
    business_connectivity/
    authority_management/
    resource_catalogue/
    ...
  workflows/
    policy_export/
  platform/
    bootstrap/
    database/
    auth/
    http/
```

`access_governance/` is not a target context package. If any implementation-only package with that name exists during migration, it is compatibility code and must not own new target state.

## Application Deployment realization

### New target context package

Create `contexts/application_deployment/` as the semantic owner of target ComponentDeployment state:

```text
application_deployment/
  domain/
    model.py
  application/
    ports.py
    establish_component_deployment.py
    retire_component_deployment.py
    read_component_deployments.py
  infrastructure/
    persistence/postgres/
    integrations/
  presentation/http/
```

Exact file splitting may vary during S4 while preserving these responsibilities.

### Application use cases

Minimum target use cases:

```text
EstablishComponentDeployment
RetireComponentDeployment
GetComponentDeployment
ListComponentDeployments
ResolveComponentDeployment
FindActiveComponentDeploymentsByResource   # required by evidence recognition, not first export UI
```

The first implementation slice need only expose the mutation/read surface required to establish the concrete deployments used by policy creation/export. Evidence-recognition-specific reads may remain a later adapter if that capability is not implemented in the slice.

### Consumer-owned outbound ports

AD application code owns narrow ports for:

```text
ComponentCataloguePort
    resolve_component(ComponentRef)

ResourceCataloguePort
    resolve_resource(ResourceRef)

AuthorityPort
    check(actor, CurateApplicationDeployment, scope, time)
```

These ports validate referenced owner truth without importing ACC/RC/AM domain models.

### Persistence

Target ComponentDeployment state has AD-owned persistence. It must not reuse the ACC compatibility ComponentDeployment table as its authoritative store.

Minimum persistence constraints:

- stable `component_deployment_id` primary semantic identity;
- exactly one `component_ref` and one `resource_ref` per row/aggregate state;
- terminal lifecycle state sufficient for `Active -> Retired`;
- concurrency/version protection for mutations;
- no SQL foreign key from AD tables into ACC/RC-owned tables; references are opaque semantic values;
- indexes supporting lookup by ComponentDeploymentId, ComponentRef and ResourceRef.

No uniqueness constraint is added for `resource_ref` alone because the domain does not prohibit several ComponentDeployments on one Resource.

## Access Policy realization

### Evolve the existing `contexts/access_policy/` owner

Do not create a second policy context/package. Replace target-facing application/domain behavior inside the existing semantic owner while retaining compatibility adapters needed by the as-built runtime.

Target domain state:

```text
PolicyRule
  policyRuleId
  sourceComponentDeploymentRef
  destinationComponentDeploymentRef
  lifecycle
  effectiveRevisionRef?
  RuleChange[]
  authorization/withdrawal history
```

### Target application use cases

Minimum first-MVP application surface:

```text
SubmitInitialRuleChange
SubmitRuleChange
ApproveRuleChangeSide
RejectRuleChangeSide
WithdrawCurrentAuthorization
GetPolicyRule
ListPolicyRules
ListCurrentEffectivePolicy
```

`SubmitInitialRuleChange` resolves the directed pair and reuses the existing non-Retired Rule when one exists; it does not create duplicate Rules for the same pair.

The first MVP invariant of at most one Pending RuleChange per Active Rule is checked by the aggregate and reinforced by persistence/concurrency protection.

### Consumer-owned ports

Access Policy application code owns narrow semantic ports; concrete adapters may call BC/ACC/AD/RC/AM application contracts.

```text
BusinessNeedPort
    resolve_current_need(ConnectivityNeedRef)

InteractionRevisionPort
    resolve_revision(InteractionContractRevisionRef)
    -> endpoint ComponentRefs + immutable traffic metadata/provenance

ComponentDeploymentPort
    resolve(ComponentDeploymentRef)
    -> ComponentRef + ResourceRef + lifecycle/currentness

ResourceScopePort
    resolve_effective_scopes(ResourceRef, time)
    -> ResponsibilityScopeRef[] + provenance

AuthorityPort
    check(actor, action, ResponsibilityScopeRef, time)
```

AP never reads BC/ACC/AD/RC/AM tables directly.

### Aggregate transaction boundary

One PolicyRule aggregate, including its RuleChanges and authorization/withdrawal history needed to preserve invariants, is persisted in one AP-owned transaction per mutation.

No distributed transaction is required with BC/ACC/AD/RC/AM. Their facts are read before the AP commit and the exact references/provenance/basis used for the decision are persisted with the RuleChange.

If a required owner read is Unknown/Unavailable/Ambiguous, submission/decision fails closed and no successful AP mutation is reported.

### Optimistic concurrency

PolicyRule writes use an AP-owned aggregate version/optimistic concurrency check. This is required to prevent:

- two concurrent initial submissions from creating two current Rules for the same directed pair;
- two RuleChanges becoming Pending concurrently despite the MVP invariant;
- approval of a stale change after another transition changed the aggregate.

The repository enforces one non-Retired Rule per directed pair. The concrete database mechanism may be a partial unique index or equivalent PostgreSQL constraint chosen in S4, but it must enforce the accepted uniqueness under races.

### Mutation idempotency and uncertain commits

RuleChange identity distinguishes semantic attempts; transport retries must not accidentally create new attempts.

Mutation presentation therefore accepts an application-level idempotency key for create/change commands. The AP infrastructure stores command outcome correlation atomically with the aggregate mutation or provides an equivalent retry-safe mechanism.

If commit outcome cannot be established, return an explicit uncertain/conflict outcome; do not blindly retry as a new RuleChange.

Exact HTTP header/field spelling may follow the repository's existing mutation conventions in S4, but the retry-safe semantic is mandatory.

### Rule-change decisions

Source/destination approval operations re-resolve current AM authority for the applicable stored approval basis/scope and preserve the authority evidence used for the decision.

Approval does not require a peer AG service. The AP application service invokes the PolicyRule aggregate after owner facts/authority have been resolved.

When both sides are approved, activation of the RuleChange and update of `effectiveRevisionRef` happen in the same AP aggregate transaction.

### Withdrawal

Withdrawal is an AP mutation that clears current effectiveness and records provenance. It is not retirement and does not delete Rule/change history.

A later reauthorization is a new RuleChange.

## Target policy export workflow

### Reuse `workflows/policy_export/`

The existing workflow package already represents the correct architectural kind: a cross-context read composition with no authoritative policy truth. Evolve it with a **target current-policy export path** rather than creating another top-level workflow.

As-built `GET /api/v1/normalized-policy` and its logical-`asOf` compatibility implementation remain reconstructable until separately retired. The target path must not silently change that endpoint's established semantics.

### Workflow input contracts

The target workflow application layer owns consumer-side ports:

```text
EffectivePolicyPort
    list_current_effective_policy(...)
    -> complete EffectivePolicyRule[] | denied | unknown | unavailable

RevisionProjectionPort
    resolve_revision(revisionRef)
    -> endpoint ComponentRefs + complete trafficAlternatives + provenance

ComponentDeploymentProjectionPort
    resolve_component_deployment(ref)
    -> ComponentRef + ResourceRef + lifecycle/currentness

ResourceRealizationPort
    resolve_current_resource(ref)
    -> AddressSpace? + provenance/currentness
```

Adapters translate AP/ACC/AD/RC public application contracts into workflow-owned immutable projection values. The workflow imports no peer domain classes.

### Materialization algorithm

For every Rule returned by the complete current-effective-policy read:

1. resolve its exact revision through ACC;
2. resolve source/destination ComponentDeployments through AD;
3. verify deployment Components match the ACC revision endpoints;
4. resolve each deployment's one Resource through RC;
5. require a current Resource AddressSpace on both sides;
6. emit one row per traffic alternative;
7. preserve `PolicyRuleRef`, revision, ComponentDeployment and Resource provenance.

There is no source/destination placement Cartesian product.

### Output model

The workflow returns one immutable result:

```text
VendorNeutralPolicyExport {
    capturedAt
    rows[]
    sourceSnapshotProvenance
}

VendorNeutralPolicyRow {
    sourceAddressSpace
    destinationAddressSpace
    protocol/service semantics
    sourcePortRange?
    destinationPortRange?
    policyRuleRef
    revisionRef
    sourceComponentDeploymentRef
    destinationComponentDeploymentRef
    sourceResourceRef
    destinationResourceRef
}
```

`HostAddress` and `Prefix` are preserved as typed/source-neutral AddressSpace values. Export does not depend on NEP, Firewall, ACL locator, provider rendering or configured-state types.

### Complete-or-unresolved

One requested export has only these top-level semantic outcomes:

```text
Success(complete VendorNeutralPolicyExport)
Denied
Unknown/Unavailable authority/input
Unresolved(diagnostics)
```

If any selected effective Rule cannot be materialized completely, the workflow does not publish a partial successful row set. Diagnostics may identify the failed Rule/input.

### Coherent current read

The selected target MVP is current-state, not historical `asOf` export.

For the supported local PostgreSQL runtime, compose the target export inside one read-only `REPEATABLE READ` database transaction/snapshot shared by the owner adapters used by that workflow request. Each adapter still reads only its owner repository/schema contract; shared connection/snapshot is a consistency mechanism, not shared ownership.

If a future owner moves to an external source that cannot participate in the transaction, its adapter must provide a version/currentness token sufficient for the workflow to establish one coherent capture; otherwise the export is Unresolved. S3 does not require distributed transactions.

The workflow records a capture timestamp plus source provenance/version references sufficient to explain the successful result.

### JSON/table and CSV

One application result feeds both presentation forms:

```text
VendorNeutralPolicyExport
    -> JSON DTO used by Web table
    -> CSV serializer/download
```

The CSV adapter must serialize the already-materialized result and must not re-query owner contexts. Therefore table and CSV cannot diverge semantically because of a second live read.

For the Web flow, the client obtains one export result/identifier or payload and downloads CSV for that same materialization. If implementation uses stateless immediate serialization, the JSON and CSV endpoints must share the exact captured result within one request flow rather than independently rebuilding policy.

The concrete choice between short-lived server-side export result storage and same-request CSV streaming is S4 only if it does not change this same-result guarantee. For the first local MVP, prefer no durable export aggregate; a short-lived/non-authoritative application result is sufficient.

## HTTP/API boundary

Keep the existing `/api/v1/normalized-policy` endpoint as as-built compatibility.

Introduce target-facing resources under a distinct surface so target semantics are not confused with the old `scope + asOf` contract:

```text
/api/v1/component-deployments
/api/v1/policy-rules
/api/v1/policy-rules/{policyRuleId}/changes
/api/v1/policy-rules/{policyRuleId}/changes/{ruleChangeId}/source-decision
/api/v1/policy-rules/{policyRuleId}/changes/{ruleChangeId}/destination-decision
/api/v1/policy-rules/{policyRuleId}/withdrawal
/api/v1/vendor-neutral-policy
/api/v1/vendor-neutral-policy.csv
```

Exact HTTP verbs, DTO field spelling and pagination parameters are S4 engineering-contract work, but these resource/use-case boundaries are S3 constraints.

Authenticated actor identity and command time are server-owned values. Request payloads cannot supply trusted actor identity or authority evidence.

## Web boundary

Target Web features remain outer adapters:

```text
features/component-deployments/
features/policy-rules/
features/policy-export/
```

The UI may guide the user through Component Deployment creation, RuleChange submission/approval and policy export, but it never evaluates authority or effective-policy truth locally.

The policy export table is server-produced semantic data. CSV is downloaded from the backend export surface rather than reconstructed from potentially paged/filterable browser rows.

## Evidence Access Recognition

Evidence Access Recognition is accepted target domain composition but is **not required to implement the selected first vendor-neutral policy-export vertical** unless explicitly included by a later G4 scope.

When implemented, place it under an explicit workflow/application composition (for example `workflows/evidence_access_recognition/`) consuming TAE/RC/AD/ACC public ports and producing non-authoritative candidate values for AP. It must not write AP tables directly.

This deferral prevents TAE/Evidence scope from widening the first implementation slice merely because the target model supports it.

## As-built compatibility and migration

### Do not reinterpret compatibility ComponentDeployment IDs

Current ACC compatibility `ComponentDeployment` identities are unique per DeploymentInteraction side and may represent Resource sets. Target AD ComponentDeployment means one concrete Component on one Resource.

Therefore:

- never cast/relabel old ACC compatibility IDs as target AD IDs;
- never use the existing ACC compatibility table as target AD authoritative persistence;
- no automatic one-to-one migration is assumed;
- new target authoring creates AD-owned ComponentDeployment identities only.

### Existing AccessRule rows

Current Access Policy rows use a semantic identity containing source compatibility ComponentDeployment + destination compatibility ComponentDeployment + DCS revision. That differs from target PolicyRule sameness where revision is state and ComponentDeployment meaning is different.

Therefore old rows remain as-built compatibility truth. Do not silently migrate them into target PolicyRules without a lossless mapping accepted by migration design.

The first target vertical may coexist with legacy rows/tables and expose the target API/read model from target-owned records only. Existing normalized-policy endpoint continues using its compatibility path.

### Removal condition

Compatibility paths may be removed only when:

- no current product/API/UI contract requires the old semantics;
- all retained historical references remain explainable or have an explicitly accepted lossless migration;
- engineering/current-state and as-built reconstruction docs are updated accordingly.

## Persistence/data ownership summary

```text
ACC tables: ACC only
AD target tables: AD only
RC tables: RC only
AP target tables: AP only
legacy ACC/AP compatibility tables: compatibility owners only until migration
policy_export: no authoritative business tables
```

A single PostgreSQL server may host all schemas/tables. Physical colocation never permits direct peer-table access.

## Failure and authority semantics

- `Denied` and `Unknown` authority remain distinct and fail closed for protected mutations/reads.
- Missing/ambiguous BC/ACC/AD/RC/AM input is never interpreted as a permissive default.
- Unresolved target export is not an empty or partial successful export.
- persistence commit uncertainty is explicit; mutation retry must be idempotent rather than producing duplicate RuleChanges/Rules.
- compatibility adapter failures are explicit and may not manufacture target meaning from incomplete legacy data.

## Observability

Operational logs/metrics may record use-case name, correlation/idempotency key, opaque Rule/Change/Deployment refs and outcome class. They must not become business provenance or leak secrets/raw credentials.

Domain/business provenance required for audit is persisted in the owning context, not reconstructed from logs.

## Mechanical architecture checks

Add/extend architecture tests so they can prove at least:

1. target `application_deployment.domain` imports no ACC/RC framework/persistence/domain implementation;
2. `access_policy.domain` imports no BC/ACC/AD/RC/AM package outside its own domain primitives;
3. AP application dependencies on peers are through AP-owned ports/contracts;
4. policy-export application imports workflow-owned projection types/ports, not AP/ACC/AD/RC domain models;
5. policy export has no imports from NEP/APR/NEO/provider packages for the vendor-neutral target path;
6. contexts do not read/write peer persistence adapters/tables;
7. no target `access_governance` package is introduced as an authoritative owner;
8. old ACC compatibility ComponentDeployment types are not imported into target AD/AP domain code;
9. target API serializers remain presentation adapters rather than domain dependencies.

## S3 decisions left to S4

S4 may choose only implementation-local details that do not change the architecture above, including:

- exact file decomposition inside accepted packages;
- concrete PostgreSQL table/column/index names while preserving required constraints;
- exact HTTP verbs/DTO field casing/error codes consistent with the engineering error model;
- exact transaction helper implementation for shared read snapshot;
- exact short-lived representation used to guarantee JSON/CSV same-result serialization;
- exact test file layout.

S4 may not decide semantic identity, owner boundaries, whether revision belongs to Rule identity, whether to reuse compatibility IDs, or whether export may return partial success.
