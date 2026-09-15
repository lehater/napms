# Semantic Ownership

Status: `S2 affected ownership aligned 2026-09-16; Tactical DDD pending revalidation`.

Canonical relationships: `context-map.md`.

| Knowledge / decision | Semantic owner |
|---|---|
| Business Process / Connectivity Need | **Business Connectivity** |
| Policy Rule identity/current effective revision | **Access Policy** |
| rule-change proposal/request history, bilateral approval/rejection/withdrawal, current effective policy transition | **Access Policy** |
| effective actor/action/scope authority | **Authority Management** |
| Resource identity/lifecycle and effective `HostAddress | Prefix` realization | **Resource Catalogue** |
| Resource Scope Affiliation / Resource Responsibility | **Resource Catalogue** |
| Application / Component / Interaction / immutable InteractionContractRevision | **Application Communication Catalogue** |
| concrete ComponentDeployment -> ComponentRef + ResourceRef truth | **Application Deployment** |
| normalized required technical predicates / target required policy | **non-peer Required Policy Materialization** |
| evidence-to-access candidate correlation | **non-peer Evidence Access Recognition composition** |
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
AD:  ComponentDeployment(ComponentRef, ResourceRef)
RC:  Resource -> effective AddressSpace [0..1] = HostAddress | Prefix
```

ACC owns no concrete deployment placement. AD owns no Resource address/scope semantics. RC owns no Application/Component deployment semantics.

For the first MVP:

- one Component Deployment references exactly one Component and exactly one Resource;
- deploying the same Component on another Resource creates another Component Deployment;
- several Component Deployments of the same Component may coexist and are independently addressable by policy;
- changing only the Resource AddressSpace does not change ComponentDeployment identity;
- provider/container/pod identity is not part of the accepted target.

Whether several different Component Deployments may share one Resource is not constrained by current policy/export behavior and remains intentionally undecided.

## Access Policy lifecycle ownership

Access Policy is the single owner of the concrete access lifecycle:

```text
PolicyRule
    sourceComponentDeploymentRef
    destinationComponentDeploymentRef
    current/effective revisionRef?

+ proposal/change attempts
+ bilateral approval/rejection decisions
+ withdrawal/regrant history
+ decision/business/evidence provenance
```

The former Access Governance Bounded Context is removed from the target model. Its still-required governance semantics remain inside Access Policy because they directly control the same Rule's current effective revision/state.

This does **not** collapse historical and current truth:

- pending/rejected changes remain historical/proposed facts and do not overwrite current effective policy;
- an accepted change may update the current effective revision of the same concrete Rule;
- withdrawal makes the Rule non-effective without rewriting history;
- old approvals cannot silently reactivate a withdrawn Rule.

Business Connectivity remains separate because business Need is not authorization and may outlive one concrete deployment pair or revision. Authority Management remains separate because authority evaluation is reusable and independently owned.

## Concrete policy subject

The concrete directed connection is identified by:

```text
sourceComponentDeploymentRef
+ destinationComponentDeploymentRef
```

The current/proposed `InteractionContractRevisionRef` supplies exact traffic semantics for that connection and is not by itself the connection identity.

The revision's owning Interaction supplies the endpoint Component definitions. Access Policy verifies the concrete Component Deployments match those endpoints; no duplicate `InteractionRef` is required solely for that purpose.

## Responsibility-scope correlation

`ResponsibilityScopeRef` remains a stable correlation value, not a Bounded Context.

- AD identifies each concrete Component Deployment's Resource;
- RC owns Resource-to-Scope affiliation;
- AM owns Actor/action authority to the same scope reference;
- Access Policy owns how those independent truths establish source/destination approval obligations.

Resource responsibility/contact metadata does not grant actor authority.

For MVP, each side must resolve to exactly one distinct applicable Responsibility Scope. Zero or several fail closed.

## Authority semantics

AM evaluates authority for an exact:

```text
ActorRef + ActionRef + ResponsibilityScopeRef + effectiveTime
```

using effective membership/role/scope facts. `Denied` and `Unknown` fail closed for protected actions. Historical decisions retain authority evidence valid at decision time; later assignment changes do not rewrite old decisions.

## Technical evidence ownership and recognition

```text
source-specific collectors/adapters
    -> faithful normalization into TAE published language
    -> TAE immutable evidence history
    -> Evidence Access Recognition composition
    -> RecognizedAccessCandidate | unresolved
    -> Access Policy proposal lifecycle
```

TAE owns evidence meaning/invariants only. It does not create desired policy or authorization.

Evidence Access Recognition may correlate TAE predicates with RC Resources, AD Component Deployments and ACC revision semantics. It owns no authoritative Resource/deployment/application/policy truth and must fail closed on ambiguous correlation.

A recognized candidate may carry evidence provenance into the same Access Policy change lifecycle as manual creation. It cannot bypass Process/Need submission requirements or approval authority.

## Realization chain

```text
Access Policy current effective Rule
+ ACC exact immutable traffic revision
+ AD concrete source/destination ComponentDeployment -> ResourceRef
+ RC Resource AddressSpace
+ NEP target relevance
-> RPM TargetRequiredPolicy
-> APR comparison with ConfiguredEffectivePolicySnapshot
-> VerifiedChangeIntent(ENSURE-PERMIT) when missing access exists
-> provider renderer
-> NEO controlled execution
```

One effective Rule already names one concrete source and destination Component Deployment; materialization does not expand all replicas of the same Component.

Configured evidence stored by TAE may separately be one input to Provider Policy Interpreter under an explicit source contract.

Unresolved input is not empty policy. `excess` is not automatic removal authority. Apply success is not convergence proof.

## Guardrail

This artifact records problem-space ownership and semantic boundaries. It does not prescribe synchronous transport, database topology, package layout, persistence schema or service decomposition.
