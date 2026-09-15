# Semantic Ownership

Status: `S2 MVP target ownership aligned with TAE acquisition boundary 2026-09-15`.

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
| canonical normalized source-qualified technical evidence | **Technical Access Evidence** |
| source-specific technical evidence collection / translation into TAE contract | acquisition/collector integration/application capability |
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

## Technical evidence ownership

```text
source-specific collectors/adapters
    -> faithful normalization into TAE published language
    -> TAE immutable evidence history
    -> consumer-specific interpretation
```

TAE owns the meaning/invariants of normalized evidence facts, not collection scheduling, polling cadence, credentials, retries or source transport.

Typical non-BC producers include device/config acquisition, NetFlow/IPFIX/flow collection and import adapters.

TAE evidence remains evidence. It does not itself create authorization, desired policy, access/ACL proposals or network mutation intent.

NEO is not the read/acquisition owner for TAE. NEO owns controlled mutation. Whether collectors and NEO share concrete provider/device access infrastructure is an Architecture concern, not semantic ownership.

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

Configured evidence stored by TAE may be one input source for the Provider Policy Interpreter under an explicit source contract; TAE does not determine current/complete configured-policy truth.

Unresolved input is not empty policy. `excess` is not automatic removal authority. Apply success is not convergence proof. Semantic ownership does not prohibit rebuildable consumer-local projections for computation locality.

## Guardrail

This artifact records problem-space ownership and semantic boundaries. It does not prescribe synchronous transport, database topology, package layout, polling framework, shared device client or persistence schema.
