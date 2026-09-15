# Semantic Ownership

Status: `S2 affected-edge aligned 2026-09-15`.

Canonical relationships: `context-map.md`.

| Knowledge / decision | Semantic owner |
|---|---|
| Business Process / Connectivity Need | **Business Connectivity** |
| bilateral request/consent/grant/withdrawal | **Access Governance** |
| effective actor/action/scope authority | **Authority Management** |
| current semantic authorization | **Access Policy** |
| Resource identity/lifecycle and effective `HostAddress | Prefix` realization | **Resource Catalogue** |
| Resource Scope Affiliation / Resource Responsibility | **Resource Catalogue** |
| Application / Component / Interaction / immutable traffic contract | **Application Communication Catalogue** |
| ApplicationDeployment / ComponentPlacement -> ResourceRef | **Application Deployment** |
| normalized required technical predicates / target required policy | **non-peer Required Policy Materialization** |
| candidate enforcement target/policy locator | **Network Enforcement Placement** |
| source-qualified technical evidence | **Technical Access Evidence** |
| provider configured-policy interpretation | provider integration capability |
| required-vs-configured assessment/change design/verification | **Access Policy Realization** |
| provider target rendering | provider integration capability |
| controlled provider/device mutation lifecycle | **Network Environment Operations** |

## Application / deployment / resource ownership

```text
ACC: Application, Component, InteractionContractRevision
AD:  ApplicationDeployment, ComponentPlacement -> ResourceRef
RC:  Resource -> effective AddressSpace [0..1] = HostAddress | Prefix
```

ACC owns no deployment placement. AD owns no Resource address. RC owns no Component/Application placement. `ResourceEndpoint`, endpoint purpose and deployment-specific network exposure are not current target concepts.

## Governed subject

```text
GovernedInteractionSubject =
    InteractionContractRevisionRef
  + sourceApplicationDeploymentRef
  + destinationApplicationDeploymentRef
```

Technical address/placement realization is not semantic authorization identity. Placement/scope changes may nevertheless alter approval obligations; resulting authorization behavior remains S1-open.

## Responsibility-scope correlation

`ResponsibilityScopeRef` is a stable correlation value, not a BC. RC owns Resource-to-Scope affiliation; AM owns Actor/action authority to the same reference; AG owns how those independent truths establish approval obligations.

## Realization chain

```text
AP effective authorization
+ ACC traffic semantics
+ AD placements
+ RC Resource AddressSpace
+ NEP target relevance
-> RPM TargetRequiredPolicy
-> APR comparison with ConfiguredEffectivePolicySnapshot
-> VerifiedChangeIntent
-> provider renderer
-> NEO execution
```

Unresolved input is not empty policy. Apply success is not convergence proof. Semantic ownership does not prohibit rebuildable consumer-local projections for computation locality.
