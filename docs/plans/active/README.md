# Active execution

Current: first implementation MVP — global Required Access Matrix.

Lifecycle stage: `S2`
Stage state: `ACCEPTED`
Lifecycle basis: `docs/requirements/first-mvp-required-access-matrix.md`, `docs/requirements/application-catalogue-domain-target.md`, canonical `docs/domain/strategic-model.md`, `docs/domain/context-map.md`, accepted ACC/AD/RC Tactical models, and `docs/domain/mvp-ddd-convergence-checkpoint.md` as the wider target-domain baseline.
Implementation authorization: `none`
Authorized scope: `none`
Authorization basis: `none`

## Selected first implementation MVP

Project-owner decision on 2026-09-15 narrows the first implemented vertical to the smallest useful policy-output journey:

```text
ACC
  InteractionContractRevision
        |
        v
AD
  ApplicationDeployment
  Component -> Resource placements
        |
        v
RC
  Resource -> AddressSpace
        |
        v
Required Access Matrix materialization
        |
        +--> tabular view
        `--> downloadable vendor-neutral export
```

The materialization is an application/workflow composition, not a new Bounded Context.

One policy-selection item identifies:

```text
InteractionContractRevisionRef
+ sourceApplicationDeploymentRef
+ destinationApplicationDeploymentRef
```

Every applicable source placement × destination placement × traffic alternative participates in the result. Missing required owner truth produces explicit `Unresolved`; it must not silently become an empty or partial successful policy.

The output is global for this MVP. It is not partitioned by firewall, device, ACL or `ComparisonScope`.

## Deliberately outside the first implementation MVP

Business Connectivity, Access Governance, Authority Management, Access Policy authorization, Network Enforcement Placement, Technical Access Evidence, Provider Policy Interpreter, Access Policy Realization configured-state comparison, Provider Policy Renderer and Network Environment Operations remain part of the wider target model but are not prerequisites for this first implementation vertical.

The first MVP therefore does not require governance/approval, actor authority, firewall selection, configured-state comparison, drift/remediation, vendor configuration generation or network execution.

`docs/requirements/policy-export-core.md` describes a broader authorized/as-of export capability and must not widen this selected MVP.

## S2 disposition

```text
G1: PASS — first implementation MVP behavior explicitly selected by project owner
G2: PASS — selected scope uses already accepted ACC/AD/RC ownership and adds only a non-owning derived workflow composition
```

The wider 11-context G2 baseline remains valid target-domain truth. Narrowing the first implementation slice does not delete or redefine those later contexts.

No new domain owner, aggregate or authorization semantics are introduced by this MVP selection.

## Next

Enter `S3 Architecture` only for this narrow Required Access Matrix vertical: define application/use-case boundaries, public ACC/AD/RC read contracts, consistency/unresolved behavior, presentation/export boundary and migration from current runtime structures where required.

No implementation work is authorized until that scope reaches `G4 PASS`.
