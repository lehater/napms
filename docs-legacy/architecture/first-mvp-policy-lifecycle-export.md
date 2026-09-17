# First MVP — Policy lifecycle and vendor-neutral export architecture

Status: `S3 target architecture candidate aligned to simplified G2 baseline 2026-09-16`.

## Purpose

Realize the accepted first-MVP semantics without transferring ownership or embedding customer-specific approval workflow:

```text
ACC Application / Component / Interaction / immutable revision
RC Resource / AddressSpace
AD concrete ComponentDeployment(ComponentRef, ResourceRef)
BC Process / ConnectivityNeed
AM optional protected-action authority
        |
        v
AP PolicyRule + RuleChange(Pending -> Accepted | Rejected)
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

Existing normalized-policy export, legacy AccessRule and ACC compatibility deployment semantics remain as-built contracts until explicitly migrated.

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

No service-per-context distribution, broker or saga is required by the first MVP.

## Target backend ownership

```text
backend/src/napms/
  contexts/
    access_policy/
    application_deployment/
    application_catalogue/
    business_connectivity/
    authority_management/
    resource_catalogue/
    ...
  workflows/
    policy_export/
  platform/
```

`access_governance/` is not a target context package. Any such migration package is compatibility-only and cannot own new target state.

## Application Deployment realization

Introduce `contexts/application_deployment/` as semantic owner of target ComponentDeployment state.

Minimum application surface:

```text
EstablishComponentDeployment
RetireComponentDeployment
GetComponentDeployment
ListComponentDeployments
ResolveComponentDeployment
```

AD application owns narrow outbound ports to validate opaque ACC ComponentRef, RC ResourceRef and protected mutation authority when configured. It never imports ACC/RC/AM private domain/persistence models.

Target persistence requirements:

- stable `component_deployment_id`;
- exactly one `component_ref` and one `resource_ref`;
- `Active -> Retired` lifecycle;
- optimistic/concurrency versioning;
- no cross-context SQL foreign keys;
- lookup indexes by deployment/component/resource;
- no uniqueness constraint on ResourceRef alone because the domain does not prohibit several ComponentDeployments on one Resource.

ACC compatibility ComponentDeployment records are not target AD records and are never reinterpreted by ID cast.

## Access Policy realization

### Side-by-side target model

Evolve the existing `contexts/access_policy/` BC. Preserve current legacy `AccessRule` behavior for as-built APIs while adding mechanically distinct target PolicyRule/RuleChange code and persistence.

Target aggregate:

```text
PolicyRule {
    policyRuleId
    sourceComponentDeploymentRef
    destinationComponentDeploymentRef
    lifecycle
    effectiveRevisionRef?
    changes[]
    withdrawalHistory[]
}

RuleChange {
    ruleChangeId
    revisionRef
    origin
    connectivityNeedRef
    business/evidence provenance
    state: Pending | Accepted | Rejected
    submittedBy / submittedAt
    decidedBy? / decidedAt?
    decisionProvenanceRef?
}
```

Minimum target use cases:

```text
SubmitInitialRuleChange
SubmitRuleChange
DecideRuleChange(Accepted | Rejected)
WithdrawPolicyRule
GetPolicyRule
ListPolicyRules
ListCurrentEffectivePolicy
```

There are no target `ApproveRuleChangeSide`, `source-decision`, `destination-decision`, ApprovalBasis or approval-obligation APIs in the MVP.

### AP consumer-owned ports

AP application needs only owner truth required by accepted semantics:

```text
BusinessNeedPort
    resolve_current_need(ConnectivityNeedRef)

InteractionRevisionPort
    resolve_revision(InteractionContractRevisionRef)
    -> endpoint ComponentRefs + immutable traffic/provenance

ComponentDeploymentPort
    resolve(ComponentDeploymentRef)
    -> ComponentRef + ResourceRef + lifecycle/currentness

ActionAuthorityPort                 # only when the deployment protects the action via AM
    check(actor, action, configured authority context, time)
```

Baseline `DecideRuleChange` has no `ResourceScopePort`. RC ResourceScopeAffiliation is not consulted merely to accept/reject a change.

The authority port protects an application action; it does not describe how the organization reached the decision. External approval/ticket systems may perform their own procedures and call `DecideRuleChange` once a final result exists.

### Transaction, uniqueness and concurrency

One PolicyRule aggregate mutation is one AP-owned transaction.

Required concurrency constraints:

- at most one non-Retired PolicyRule per directed target ComponentDeployment pair;
- at most one Pending RuleChange per Active Rule;
- stale decisions cannot overwrite a newer aggregate version;
- acceptance and `effectiveRevisionRef` update are atomic;
- rejection never changes `effectiveRevisionRef`.

A partial unique index or equivalent PostgreSQL mechanism may realize pair uniqueness in S4.

### Idempotency / uncertain commit

RuleChange identity distinguishes semantic attempts; transport retry cannot manufacture another attempt.

Create/change/decision mutations use the repository's accepted idempotency mechanism. An uncertain commit outcome is explicit and may be retried only with the same idempotency identity, never as a new RuleChange.

### Decision and withdrawal

Formal decision:

```text
Pending -> Accepted
Pending -> Rejected
```

The server owns authenticated actor and decision time. A trusted external integration may attach an external ticket/workflow reference as decision provenance; AP does not persist that system's workflow internals.

Withdrawal atomically clears `effectiveRevisionRef` and appends actor/time/provenance. It is not retirement and history remains intact. Reauthorization requires a new RuleChange and a new Accepted decision.

## Full current effective-policy read

The target export reads the **complete current effective target PolicyRule set**, not the legacy client-selected `scope + asOf` projection.

The full-policy read is privileged. Authority Management may guard it via the existing effective-policy read capability using a server-selected application-level authority context. The client cannot choose a scope that changes which Rule rows are exported.

After admission, AP returns all current effective target Rules as one complete set. Denied/Unknown authority returns no policy data.

This security guard is not part of PolicyRule identity or RuleChange decision semantics.

## Target policy export workflow

Reuse `workflows/policy_export/`; do not create another semantic owner.

Keep `GET /api/v1/normalized-policy` unchanged as an as-built compatibility path. Add a target path consuming target AP/ACC/AD/RC public contracts.

Workflow-owned ports:

```text
ExportAuthorityPort
    check_full_policy_read(actor, current_time)

EffectivePolicyPort
    list_all_current_effective_policy()

RevisionProjectionPort
    resolve_revision(revisionRef)

ComponentDeploymentProjectionPort
    resolve_component_deployment(ref)

ResourceRealizationPort
    resolve_current_resource(ref)
```

Workflow application code imports workflow-owned projection values, not peer domain models or peer persistence.

### Materialization

For each current effective Rule:

1. resolve exact ACC revision;
2. resolve source/destination target ComponentDeployments;
3. verify deployment Components match revision endpoints;
4. resolve each deployment's one Resource through RC;
5. require current AddressSpace for both Resources;
6. emit one row per complete traffic alternative;
7. preserve PolicyRule/revision/deployment/resource provenance.

No source/destination replica Cartesian product exists.

Vendor-neutral output row:

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

The export core has no dependency on NEP, Firewall/ACL, APR, provider renderer, NEO or configured-policy types.

### Complete-or-unresolved

An export creation attempt yields only:

```text
Success(complete ExportResult)
Denied
AuthorityUnknown
Unresolved(diagnostics)
Unavailable
```

Any unresolved selected Rule prevents successful publication of a partial full-policy result.

## Coherent current snapshot

For the supported local PostgreSQL runtime, assemble target export within one read-only `REPEATABLE READ` snapshot shared by the owner adapters for that workflow request. Each adapter still reads only its owner repository/schema.

A future external owner that cannot join the snapshot must provide sufficient currentness/version evidence; otherwise the export is Unresolved. No distributed transaction is introduced.

## Same-result table and CSV

A successful materialization stores a short-lived immutable workflow-owned read artifact:

```text
VendorNeutralPolicyExportResult {
    exportId
    createdAt
    expiresAt
    rows[]
    sourceSnapshotProvenance
}
```

This is not a domain aggregate or authoritative business state.

Both JSON/table and CSV read the same stored artifact:

```text
POST /api/v1/vendor-neutral-policy-exports
GET  /api/v1/vendor-neutral-policy-exports/{exportId}
GET  /api/v1/vendor-neutral-policy-exports/{exportId}.csv
```

CSV never re-runs live materialization. Expired/missing IDs are explicit and are not silently rebuilt under the same ID.

## Target HTTP boundaries

Target resource/use-case surface is conceptually:

```text
/api/v1/component-deployments
/api/v1/policy-rules
/api/v1/policy-rules/{policyRuleId}/changes
/api/v1/policy-rules/{policyRuleId}/changes/{ruleChangeId}/decision
/api/v1/policy-rules/{policyRuleId}/withdrawal
/api/v1/vendor-neutral-policy-exports
/api/v1/vendor-neutral-policy-exports/{exportId}
/api/v1/vendor-neutral-policy-exports/{exportId}.csv
```

Exact HTTP verbs, DTO casing and error names belong to S4. The decision resource accepts one formal Accepted/Rejected outcome, not endpoint-side approvals.

Authenticated actor identity and current/command time are server-owned. Caller payloads cannot supply trusted actor identity/authority evidence.

## Web boundary

Target Web features remain outer adapters:

```text
features/component-deployments/
features/policy-rules/
features/policy-export/
```

Policy UI displays RuleChange state (`Pending | Accepted | Rejected`) and exposes a formal decision action to admitted users/integrations. It does not hard-code source/destination approval workflow.

The policy-export table renders backend ExportResult rows and CSV downloads by `exportId`.

## Evidence Access Recognition

Evidence Access Recognition is accepted target composition but remains outside the selected first vendor-neutral export implementation scope unless a later G4 includes it.

When implemented, it consumes TAE/RC/AD/ACC public contracts and produces non-authoritative candidates for AP. It never writes AP persistence directly.

## Compatibility and migration

- legacy ACC compatibility ComponentDeployment IDs are not target AD IDs;
- legacy AccessRule rows keep legacy semantic identity and are not silently converted to target PolicyRules;
- target AP and legacy AccessRule persistence are separate and there is no dual write;
- legacy `/api/v1/normalized-policy` continues on the compatibility path;
- migration requires exact, lossless identity/provenance mapping and is a separate accepted plan;
- as-built reconstruction docs remain until the corresponding runtime is actually removed.

## Persistence ownership

```text
ACC tables                 -> ACC only
AD target tables           -> AD only
RC tables                  -> RC only
AP target tables           -> AP only
legacy ACC/AP tables       -> compatibility owners only
policy_export_result       -> workflow-owned non-authoritative TTL read artifact
```

Physical PostgreSQL colocation never permits peer-private table access.

## Failure / security semantics

- protected operations use server-authenticated actor identity;
- Denied and Unknown authority fail closed where authority is required;
- AP formal decision does not depend on RC scope resolution;
- missing/ambiguous BC/ACC/AD owner input is never a permissive default;
- Unresolved export is not empty/partial success;
- expired export result is not silently recreated under the same ID;
- commit uncertainty is explicit and retry-safe;
- compatibility adapters may not manufacture target meaning from incomplete legacy state.

## Mechanical architecture checks

Architecture tests should prove at least:

1. `application_deployment.domain` imports no ACC/RC private implementation;
2. `access_policy.domain` imports no BC/ACC/AD/RC/AM implementation package;
3. AP peer dependencies are AP-owned application ports;
4. target AP contains no source/destination approval-side or ApprovalBasis dependency;
5. target decision path has no RC ResourceScopeAffiliation dependency;
6. policy-export application imports workflow-owned projection contracts, not peer domain models;
7. vendor-neutral export has no NEP/APR/NEO/provider dependency;
8. contexts do not read/write peer persistence;
9. no target `access_governance` authoritative package is introduced;
10. ACC compatibility ComponentDeployment types do not enter target AD/AP domain code.

## G3 review focus

Before G3 PASS, independently challenge:

- target-vs-legacy persistence separation;
- concurrency/idempotency for Rule/RuleChange decisions;
- action-authority placement without rebuilding approval workflow;
- coherent complete export snapshots;
- same-result JSON/CSV guarantee;
- dependency isolation and migration seams.

No production-code implementation is authorized until later S4/G4.
