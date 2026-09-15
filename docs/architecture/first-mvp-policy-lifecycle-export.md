# First MVP — Policy lifecycle and vendor-neutral export architecture

Status: `S3 target architecture accepted; G3 review candidate 2026-09-16`.

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
all current effective target PolicyRules
        + ACC + AD + RC
        |
        v
Full Vendor-Neutral Policy Export
        -> immutable short-lived ExportResult
        -> JSON/table
        -> CSV from the same ExportResult
```

This architecture is for the target path. Existing normalized-policy export and ACC compatibility deployment semantics remain as-built contracts until explicitly migrated.

## Architecture style

Keep the modular monolith and Clean Architecture/Ports-and-Adapters direction:

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

`access_governance/` is not a target context package. Any implementation-only package with that name during migration is compatibility code and cannot own new target state.

## Application Deployment realization

### New target context package

Create `contexts/application_deployment/` as semantic owner of target ComponentDeployment state:

```text
application_deployment/
  domain/
  application/
  infrastructure/
    persistence/postgres/
    integrations/
  presentation/http/
```

### Application use cases

Minimum target use cases:

```text
EstablishComponentDeployment
RetireComponentDeployment
GetComponentDeployment
ListComponentDeployments
ResolveComponentDeployment
```

`FindActiveComponentDeploymentsByResource` belongs to the future Evidence Access Recognition adapter and is not required by the selected first export implementation slice.

### Consumer-owned outbound ports

AD application code owns narrow ports equivalent to:

```text
ComponentCataloguePort
    resolve_component(ComponentRef)

ResourceCataloguePort
    resolve_resource(ResourceRef)

AuthorityPort
    check(actor, CurateApplicationDeployment, server-selected scope, time)
```

These ports validate owner truth without importing ACC/RC/AM domain models.

### Persistence

Target ComponentDeployment state has AD-owned persistence. It must not reuse the ACC compatibility ComponentDeployment table as authoritative target storage.

Required constraints:

- stable `component_deployment_id` semantic identity;
- exactly one `component_ref` and one `resource_ref` per aggregate;
- terminal lifecycle sufficient for `Active -> Retired`;
- optimistic/concurrency versioning for mutation;
- no SQL foreign keys into ACC/RC-owned tables;
- indexes for lookup by ComponentDeploymentId, ComponentRef and ResourceRef;
- no uniqueness constraint on ResourceRef alone, because multiple ComponentDeployments on one Resource are not prohibited by accepted domain truth.

## Access Policy realization

### Evolve the existing owner

Evolve `contexts/access_policy/`; do not create a second policy context/package.

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

Minimum first-MVP surface:

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

`SubmitInitialRuleChange` resolves the directed pair and reuses the existing non-Retired Rule if one exists; it never creates a second current Rule for the same pair.

### Consumer-owned ports

AP application owns narrow semantic ports, implemented by adapters to BC/ACC/AD/RC/AM application contracts:

```text
BusinessNeedPort
    resolve_current_need(ConnectivityNeedRef)

InteractionRevisionPort
    resolve_revision(InteractionContractRevisionRef)
    -> endpoint ComponentRefs + immutable traffic/provenance

ComponentDeploymentPort
    resolve(ComponentDeploymentRef)
    -> ComponentRef + ResourceRef + lifecycle/currentness

ResourceScopePort
    resolve_effective_scopes(ResourceRef, time)
    -> ResponsibilityScopeRef[] + provenance

AuthorityPort
    check(actor, action, ResponsibilityScopeRef, time)
```

AP never reads peer tables directly.

### Aggregate transaction boundary

One PolicyRule aggregate, including RuleChanges and authorization/withdrawal history needed by its invariants, is persisted in one AP-owned transaction per mutation.

No distributed transaction with BC/ACC/AD/RC/AM is required. Required owner facts are resolved before the AP commit and the exact references/provenance/approval basis used are persisted with the RuleChange.

Missing, Unknown, Unavailable or Ambiguous required input fails closed and produces no successful AP mutation.

### Optimistic concurrency and uniqueness

PolicyRule writes use AP-owned optimistic concurrency.

The repository must enforce:

- at most one non-Retired PolicyRule per directed ComponentDeployment pair under races;
- at most one Pending RuleChange per Active Rule for the MVP;
- stale approval/change operations cannot overwrite a newer aggregate version.

A PostgreSQL partial unique index or equivalent mechanism may be selected in S4, but implementation must mechanically enforce the accepted invariants.

### Mutation idempotency and uncertain commits

RuleChange identity distinguishes semantic attempts; transport retries must not create another attempt.

Create/change HTTP mutations use an application-level idempotency key. AP stores command/outcome correlation atomically with the aggregate change or provides an equivalent retry-safe mechanism.

If commit outcome cannot be established, return explicit uncertainty/conflict and permit retry only with the same idempotency identity. Never retry as a new RuleChange automatically.

Exact header/field spelling follows the engineering error/mutation conventions in S4.

### Decisions and activation

Source/destination decisions re-check current AM authority for the stored applicable approval scope and preserve authority evidence.

When both sides are approved and the change remains applicable, `RuleChange -> Approved` and `effectiveRevisionRef` update occur in the same AP transaction.

No peer Access Governance service exists in the target.

### Withdrawal

Withdrawal clears current effectiveness and appends provenance/history in the same aggregate. It is not retirement and does not delete Rule/RuleChange history.

A later reauthorization is a new RuleChange.

## Full current effective-policy read

The selected target export means **the complete current effective target PolicyRule set**, not a per-rule placement subset and not the legacy `scope + asOf` export.

The target full-policy read is a privileged operation. Before the workflow reads target PolicyRules, the authenticated actor must be admitted by Authority Management for the existing `ReadEffectiveDesiredPolicy` action against a **server-selected application-level policy-read scope**. The scope is not client-supplied and is not part of PolicyRule identity or selection.

After that admission, AP's `ListCurrentEffectivePolicy` returns all current effective target PolicyRules as one complete set. Failure/unknown authority yields no policy data and no partial scope-filtered export.

The local bootstrap must provision the server-selected policy-read scope/action for authorized operators; exact seeded identifier text belongs to S4/engineering configuration, not request payloads.

This target read contract is separate from the as-built endpoint's client-selected Rule Governance Scope contract.

## Target policy export workflow

### Reuse `workflows/policy_export/`

The existing package is the correct architectural kind: cross-context read composition with no authoritative policy truth. Add a target current-policy export path there rather than creating another top-level workflow.

Keep as-built `GET /api/v1/normalized-policy` and its `scope + asOf` semantics unchanged until separately retired.

### Workflow-owned ports

Target policy-export application owns projection ports equivalent to:

```text
ExportAuthorityPort
    check_full_policy_read(actor, current_time)
    -> permitted | denied | unknown

EffectivePolicyPort
    list_all_current_effective_policy()
    -> complete EffectivePolicyRule[] | unavailable

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

Adapters translate AM/AP/ACC/AD/RC public application contracts into workflow-owned immutable projection values. Workflow application code imports no peer domain classes.

AM participates only as a security guard; policy-row semantics remain AP + ACC + AD + RC.

### Materialization algorithm

For every Rule in the complete current-effective-policy set:

1. resolve exact revision through ACC;
2. resolve source/destination ComponentDeployments through AD;
3. verify deployment Components match revision Interaction endpoints;
4. resolve each deployment's one Resource through RC;
5. require a current AddressSpace for both Resources;
6. emit one row per complete traffic alternative;
7. preserve PolicyRuleRef, revision, ComponentDeployment and Resource provenance.

There is no source/destination placement Cartesian product.

### Vendor-neutral row model

```text
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

`HostAddress` and `Prefix` remain source-neutral typed values. The target export core has no dependency on NEP, Firewall, ACL locator, APR, provider renderer, NEO or configured-state types.

### Complete-or-unresolved

One export creation attempt has only:

```text
Success(complete immutable ExportResult)
Denied
AuthorityUnknown
Unresolved(diagnostics)
Unavailable
```

Any unresolved selected Rule prevents a successful export result. Partial rows may exist only as internal diagnostics and are never published as a successful full policy.

## Coherent current snapshot

The target MVP is current-state, not historical `asOf`.

For the supported local PostgreSQL runtime, materialization runs inside one read-only `REPEATABLE READ` database snapshot shared by the AM/AP/ACC/AD/RC adapters used for the request. Each adapter still reads only its owner repository/schema; shared connection/snapshot is a consistency mechanism, not shared ownership.

The workflow captures:

- capture time;
- source owner/version/provenance references sufficient to explain the result;
- complete materialized rows.

If a future external owner cannot join this snapshot, its adapter must provide a version/currentness token sufficient to establish one coherent capture; otherwise export is Unresolved. No distributed transaction is required.

## Same-result table and CSV architecture

The requirement that the displayed table and downloaded CSV represent the **same materialization result** is realized explicitly.

A successful export creation stores a short-lived immutable workflow-owned artifact:

```text
VendorNeutralPolicyExportResult {
    exportId               # workflow/application identity, not domain identity
    createdAt
    expiresAt
    rows[]
    sourceSnapshotProvenance
}
```

This is a non-authoritative read artifact owned by `workflows/policy_export`, not a Bounded Context or business aggregate.

Store the result in workflow-owned PostgreSQL persistence after successful snapshot assembly. It may be removed by TTL/cleanup because AP/ACC/AD/RC remain authoritative and the result is reproducible from a later current snapshot.

Both table JSON and CSV read the stored result by `exportId`; neither re-queries owner contexts:

```text
POST /api/v1/vendor-neutral-policy-exports
    -> assemble coherent full current policy
    -> persist immutable short-lived ExportResult
    -> return exportId + rows/metadata

GET /api/v1/vendor-neutral-policy-exports/{exportId}
    -> same stored rows for table/reload

GET /api/v1/vendor-neutral-policy-exports/{exportId}.csv
    -> serialize same stored rows
```

Expired/missing exportId is an explicit not-found/expired result and never triggers silent re-materialization under the same ID.

This removes the prior S3 ambiguity around two live-read endpoints.

## HTTP/API boundary

Keep `/api/v1/normalized-policy` unchanged as an as-built compatibility endpoint.

Target resource/use-case boundaries are:

```text
/api/v1/component-deployments
/api/v1/policy-rules
/api/v1/policy-rules/{policyRuleId}/changes
/api/v1/policy-rules/{policyRuleId}/changes/{ruleChangeId}/source-decision
/api/v1/policy-rules/{policyRuleId}/changes/{ruleChangeId}/destination-decision
/api/v1/policy-rules/{policyRuleId}/withdrawal
/api/v1/vendor-neutral-policy-exports
/api/v1/vendor-neutral-policy-exports/{exportId}
/api/v1/vendor-neutral-policy-exports/{exportId}.csv
```

Exact HTTP verbs, DTO casing, pagination and error-code spelling belong to S4 engineering contracts while preserving these use-case/resource boundaries.

Authenticated actor identity and command/current time are server-owned. Client payloads cannot supply trusted actor identity, trusted authority evidence or the server-selected full-policy read scope.

## Web boundary

Target Web features remain outer adapters:

```text
features/component-deployments/
features/policy-rules/
features/policy-export/
```

The UI may guide users through deployment creation, RuleChange submission/approval and export, but never evaluates authority or effective-policy truth locally.

The policy table renders backend ExportResult rows. CSV is downloaded by `exportId`; it is not reconstructed from browser state or separately materialized.

## Evidence Access Recognition

Evidence Access Recognition is accepted target composition but is outside the selected first vendor-neutral export implementation scope unless a later G4 explicitly includes it.

When implemented, place it under an explicit workflow such as `workflows/evidence_access_recognition/`, consuming TAE/RC/AD/ACC public ports and producing non-authoritative candidates for AP. It never writes AP persistence directly.

## As-built compatibility and migration

### Compatibility ComponentDeployment IDs are not target AD IDs

Current ACC compatibility ComponentDeployment identities are unique per DeploymentInteraction side and may represent Resource sets. Target AD ComponentDeployment means one concrete Component on one Resource.

Therefore:

- never cast/relabel old ACC compatibility IDs as target AD IDs;
- never use ACC compatibility tables as target AD authoritative persistence;
- no automatic one-to-one migration is assumed;
- new target authoring creates AD-owned ComponentDeployment identities only.

### Existing AccessRule rows remain legacy unless explicitly migrated

Current AccessRule semantic identity includes source compatibility ComponentDeployment + destination compatibility ComponentDeployment + DCS revision. Target PolicyRule sameness differs: concrete AD deployment pair is stable and revision is state.

Old rows therefore remain as-built compatibility truth. Do not silently migrate them into target PolicyRules without a separately accepted lossless mapping.

The first target vertical may coexist with legacy rows/tables and its new APIs/read models operate on target-owned records. Existing normalized-policy continues through the compatibility path.

### Removal condition

Compatibility paths may be removed only when:

- no current API/UI/product contract requires the old semantics;
- retained historical references remain explainable or have an accepted lossless migration;
- as-built engineering/architecture documentation is updated accordingly.

## Persistence/data ownership summary

```text
ACC tables                 -> ACC only
AD target tables           -> AD only
RC tables                  -> RC only
AP target tables           -> AP only
legacy ACC/AP tables       -> compatibility owners only
policy_export_result table -> workflow-owned, non-authoritative, TTL/read artifact only
```

One PostgreSQL server may host all. Physical colocation never permits direct peer-table access.

## Failure and security semantics

- protected mutation/read uses server-authenticated actor identity;
- Denied and Unknown authority remain distinct and fail closed;
- client cannot select the privileged full-policy read scope;
- missing/ambiguous BC/ACC/AD/RC/AM input is never a permissive default;
- Unresolved export is not empty or partial success;
- expired export result is not silently re-created under the same ID;
- persistence commit uncertainty is explicit and mutations are retry-safe;
- compatibility adapters may not manufacture target meaning from incomplete legacy state.

## Observability

Operational telemetry may contain use-case name, correlation/idempotency key, opaque Rule/Change/Deployment/export refs and outcome class. It must not substitute for domain provenance or leak credentials/secrets.

Business provenance remains persisted in its semantic owner.

## Mechanical architecture checks

Add/extend tests to prove at least:

1. `application_deployment.domain` imports no ACC/RC framework/persistence/private domain implementation;
2. `access_policy.domain` imports no BC/ACC/AD/RC/AM package;
3. AP application peer dependencies are through AP-owned ports/contracts;
4. policy-export application imports workflow-owned projection contracts, not peer domain models;
5. target vendor-neutral export has no NEP/APR/NEO/provider dependency;
6. contexts do not read/write peer persistence adapters/tables;
7. no authoritative target `access_governance` package is introduced;
8. old ACC compatibility ComponentDeployment types are not imported into target AD/AP domain code;
9. `/api/v1/normalized-policy` compatibility behavior remains isolated from target export contracts;
10. JSON and CSV serializers consume stored ExportResult rows and cannot initiate owner reads.

## S3 decisions left to S4

S4 may choose implementation-local details only, including:

- exact file decomposition within accepted packages;
- concrete table/column/index names while preserving constraints;
- exact HTTP verbs/DTO field casing/error-code spelling;
- exact helper implementation for the shared `REPEATABLE READ` snapshot;
- ExportResult TTL duration/cleanup scheduling within an operationally safe bound;
- exact test file layout.

S4 may not decide semantic identity, owner boundaries, whether revision belongs to Rule identity, whether compatibility IDs can be reused, whether export may return partial success, or whether table/CSV may rematerialize independently.
