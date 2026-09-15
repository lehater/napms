# Semantic Ownership

Status: `S2 MVP target ownership aligned 2026-09-15`.

Canonical relationships: `context-map.md`.

| Knowledge / decision | Semantic owner |
|---|---|
| Business Process / Connectivity Need | **Business Connectivity** |
| bilateral request/consent/grant/withdrawal | **Access Governance** |
| effective actor/action/scope authority | **Authority Management** |
| current semantic authorization | **Access Policy** |
| Resource identity/lifecycle and effective `HostAddress | Prefix` realization | **Resource Catalogue** |
| Resource Scope Affiliation / Resource Responsibility | **Resource Catalogue** |
| Application / Component / Interaction / immutable InteractionContractRevision | **Application Communication Catalogue** |
| ApplicationDeployment / current ComponentPlacement set -> ResourceRef | **Application Deployment** |
| normalized required technical predicates / target required policy | **non-peer Required Policy Materialization** |
| candidate enforcement target/policy locator | **Network Enforcement Placement** |
| source-qualified technical evidence | **Technical Access Evidence** |
| provider configured-policy interpretation | provider integration capability |
| required-vs-configured assessment/change design/verification | **Access Policy Realization** |
| provider target rendering | provider integration capability |
| controlled provider/device mutation lifecycle | **Network Environment Operations** |

## Application / deployment / resource ownership

```text
ACC: Application, Component, Interaction, InteractionContractRevision
AD:  ApplicationDeployment, Set<(ComponentRef, ResourceRef)>
RC:  Resource -> effective AddressSpace [0..1] = HostAddress | Prefix
```

ACC owns no deployment placement. AD owns no Resource address. RC owns no Component/Application placement. `ResourceEndpoint`, endpoint purpose and deployment-specific network exposure are not current target concepts.

AD placement multiplicity is intentionally zero/one/many Resources per Component. The exact same `(ComponentRef, ResourceRef)` relation is unique within one ApplicationDeployment; all applicable placements remain visible to consumers.

## Governed subject

```text
GovernedInteractionSubject =
    InteractionContractRevisionRef
  + sourceApplicationDeploymentRef
  + destinationApplicationDeploymentRef
```

Technical address/placement realization is not semantic authorization identity.

Placement or Resource Scope Affiliation changes may alter current AG approval obligations without changing this subject. Accepted MVP behavior is explicit:

- materially unchanged source/destination obligations preserve the current grant;
- materially changed obligations cause AG to withdraw current authorization;
- historical approvals do not silently satisfy the changed obligation basis;
- reauthorization of the same subject requires current obligations to be satisfied and a new explicit grant.

## Responsibility-scope correlation

`ResponsibilityScopeRef` is a stable correlation value, not a Bounded Context.

- RC owns Resource-to-Scope affiliation;
- AM owns Actor/action authority to the same reference;
- AG owns how those independent truths establish source/destination approval obligations.

Resource responsibility/contact metadata does not grant actor authority.

## Authority semantics

AM evaluates authority for an exact:

```text
ActorRef + ActionRef + ResponsibilityScopeRef + effectiveTime
```

using effective group membership, role assignment and role-permitted action facts. `Denied` and `Unknown` fail closed for protected actions. Historical consuming decisions retain their authority evidence; later role/membership changes do not rewrite old decisions.

## Realization chain

```text
AP effective authorization
+ ACC immutable traffic revision
+ AD complete applicable placement sets
+ RC Resource AddressSpace
+ NEP target relevance
-> RPM TargetRequiredPolicy
-> APR comparison with ConfiguredEffectivePolicySnapshot
-> VerifiedChangeIntent(ENSURE-PERMIT) when missing access exists
-> provider renderer
-> NEO controlled execution
```

Unresolved input is not empty policy. `excess` is not automatic removal authority. Apply success is not convergence proof. Semantic ownership does not prohibit rebuildable consumer-local projections for computation locality.

## Guardrail

This artifact records problem-space ownership and semantic boundaries. It does not prescribe synchronous transport, database topology, package layout or persistence schema.
