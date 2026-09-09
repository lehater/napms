# Access Policy Realization Reconciliation Boundary — I20

Status: `accepted I20 WP-0 architecture contract`.

Date: 2026-09-09.

## Purpose

Define the module/dependency boundary for desired enforcement derivation and desired-vs-configured reconciliation while preserving Access Policy, RC/ACC, NEP and TAE ownership and keeping I21 rendering/I22 execution downstream.

## Target module

I20 extends the existing module:

```text
src/napms/access_policy_realization/
    domain/
        model.py              # existing I18 values
        algebra.py            # shared exact technical algebra
        realization.py        # I20 desired/configured policy values + pure decisions
    application/
        ports.py              # APR-owned owner projections
        resolve.py            # existing I18 resolver
        derive.py             # desired enforcement derivation
        reconcile.py          # configured comparison
    adapters/
        catalogues.py         # existing I18 RC/ACC adapter
        technical_access_evidence.py
        desired_policy.py
        placement.py
        configured_evidence.py
```

Exact file factoring may stay smaller when one file remains cohesive; the semantic/dependency boundaries are mandatory, not the directory count.

No APR persistence package/schema is required by I20 WP-0.

## Dependency direction

```text
APR Domain
    ^
    |
APR Application + APR-owned ports
    ^
    |
outer APR adapters / composition
    |
    +--> Access Policy desired-policy application/repository boundary
    +--> RC + ACC owner boundaries
    +--> NEP SelectEnforcement application boundary
    +--> TAE evidence read boundary
    +--> configured source/scope contract
```

Rules:
- APR Domain imports no peer bounded context, framework, database, transport, configuration or logging type;
- APR Application imports only APR Domain plus APR-owned protocols and existing APR application/domain code;
- I20 reuses the existing I18 resolution capability rather than copying its matcher;
- outer adapters may depend on peer application/domain contracts needed to translate authoritative facts;
- peer contexts never import APR to make the consumer work;
- no peer-owned SQL/table is read directly.

## Desired-policy port

Minimum source-neutral shape:

```text
load_effective(scope, asOf)
    -> DesiredPolicySnapshot
         desiredInteractions[]
         rows[]
         provenance
         complete
```

Each row provides:
- Rule/Rule Semantic Identity reference;
- exact source/destination endpoint address;
- exact supported transport/port region;
- RC/ACC/Rule provenance.

The concrete adapter may reuse the existing coherent policy-export snapshot/normalization machinery as an **outer implementation helper**. APR Domain/Application shall not import policy-export result types or treat that composition as a semantic owner.

If an existing projection cannot be translated exactly to APR Technical Region semantics, the adapter returns an explicit gap rather than broadening/narrowing.

## Shared domain-resolution capability

I20 Application composes the existing `ResolveTechnicalAccess` capability with the same APR domain knowledge port used by I18.

Uses:
- validate desired technical fragments against the complete desired Domain Interaction set;
- attribute configured effective Permit regions.

No I20 consumer flag changes I18 correspondence/status/remainder semantics.

## Placement port

APR owns a projection port such as:

```text
select_for(sourceIp, destinationIp, asOf)
    -> PlacementProjection
```

The outer adapter invokes NEP `SelectEnforcement` and translates:
- `Placed`;
- `NoEnforcement`;
- `NoForwardingPath`;
- `Ambiguous`;
- `Unknown`;
- Logical Firewall + Enforcement Attachment identity;
- provider/path/traversal provenance and knowledge gaps.

APR Domain/Application does not import NEP core types.

The I20 Enforcement Target is Logical Firewall + Enforcement Attachment. Provider realization/path attachment remain provenance.

## Managed reconciliation scope contract

A complete configured comparison requires an explicit source/integration contract projected into an APR-owned value.

Minimum shape:

```text
ManagedReconciliationScopeContract
    policyGovernanceScope
    logicalFirewallId
    enforcementAttachmentId
    evidenceSourceReference
    evidenceSourceScopeReference
    effectivePolicySemantics
    completenessClaim
    provenanceReference
```

The contract proves exact policy-partition correlation for the comparison.

It is not inferred by:
- matching strings;
- provider/device names;
- TAE Source Scope alone;
- NEP provider realization alone;
- Authority Management scope equality alone.

The first slice need not persist this contract. A trusted local/integration composition may supply it explicitly. If later production operation requires independent lifecycle/administration, re-enter the domain/architecture decision before adding persistence.

## Configured-evidence port

Minimum APR-owned shape:

```text
load_configured(evidenceSetId, managedScope, asOf)
    -> ConfiguredEnforcementSnapshot
         effectivePermitRegions[]
         attribution[]
         evidenceProvenance
         sourceContractProvenance
         completeForManagedScope
         knowledgeGaps[]
```

The adapter:
1. reads exactly the explicitly selected TAE Evidence Set;
2. requires `EvidenceKind.Configured`;
3. requires first-slice `EvidenceTime.Instant == asOf` for a complete comparison;
4. validates source/scope correlation through the managed-scope contract;
5. obtains **effective Permit regions** only from a trusted source evaluator/contract;
6. never interprets arbitrary Block/order/default/zone semantics inside generic APR code;
7. invokes/reuses I18 resolution for domain attribution.

TAE itself is unchanged as an owner: it still stores source-qualified evidence and does not become a universal current/complete-policy service.

## Effective configured-policy source contract

The first local proof may use a strict contract where:
- entries are already exact unordered effective Permit regions;
- the capture is complete for one exact Managed Reconciliation Scope;
- the capture instant equals `asOf`.

If a source exposes raw ordered Permit/Block rules, implicit defaults, zones or other evaluation mechanics, a source-specific outer adapter must normalize them exactly before the configured snapshot can be complete.

Unsupported source evaluation -> explicit gap -> reconciliation Unknown.

## Domain algebra boundary

I20 uses the existing exact APR Technical Region algebra for:
- canonical union;
- intersection;
- set difference;
- containment/equivalence;
- exact witnesses.

For one complete comparable target:

```text
common  = desired ∩ configured
missing = desired - configured
extra   = configured - desired
```

No vendor object/grouping/ordering abstraction enters this layer.

`Add | Remove | Replace | No-op` is derived from missing/extra emptiness only after completeness/ambiguity gates pass.

## Application flow

One bounded first-slice flow:

```text
explicit scope + asOf + EvidenceSetId + managed-scope contract
    |
    +--> load coherent effective desired policy
    |      -> I18 desired-domain quality check
    |      -> NEP placement per exact endpoint row
    |      -> canonical Desired Enforcement Intents
    |
    +--> load selected configured evidence
           -> source-specific effective-Permit projection
           -> I18 configured-domain attribution
           -> Configured Enforcement Snapshot
    |
    +--> pure APR reconciliation algebra
           -> Satisfied | Drift | Ambiguous | Unknown
           -> common/missing/extra
           -> Add | Remove | Replace | No-op when complete
```

## Persistence/runtime boundary

I20 requires no:
- APR migration/table/repository/UoW;
- stored “current reconciliation” state;
- background scheduler;
- public HTTP route;
- Web page;
- new Authority Management action.

The durable acceptance proof may compose existing PostgreSQL-backed Access Policy, RC/ACC, TAE and NEP owner repositories through their application/adapter boundaries.

## Failure semantics

- invalid APR input invariant -> explicit domain/application error;
- desired owner snapshot incoherence -> fail closed / Unknown, never partial success reported as complete;
- desired I18/NEP relevant uncertainty -> Unknown;
- policy-level technical/domain non-uniqueness -> Ambiguous;
- missing managed-scope correlation -> Unknown;
- unsupported configured evaluation semantics -> Unknown;
- incomplete configured capture -> Unknown;
- evidence temporal mismatch -> Unknown;
- configured I18 Unknown -> Unknown;
- configured I18 relevant ambiguity -> Ambiguous;
- complete exact delta -> Satisfied/Drift + Required Semantic Change.

Known witnesses may remain diagnostic under Unknown/Ambiguous but must carry `complete = false`.

## Validation

Required executable proof:
- APR Domain/Application dependency boundaries;
- existing I18 resolution tests remain unchanged and consumer-independent;
- desired-domain collision with non-desired interaction fails closed;
- distinct Enforcement Attachments are not collapsed;
- exact canonical common/missing/extra algebra;
- all four complete semantic changes: No-op/Add/Remove/Replace;
- incomplete configured capture cannot infer absence;
- shared-firewall/source-scope mismatch cannot infer Remove;
- temporal evidence mismatch is Unknown;
- raw unsupported Block/order/default semantics are Unknown;
- NEP ambiguity/Unknown selects no target;
- no cross-context SQL;
- no Access Policy/Decision/TAE/NEP mutation side effects;
- no I21 rendering or I22 execution dependency.
