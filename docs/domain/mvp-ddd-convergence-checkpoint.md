# First MVP DDD Convergence Checkpoint

Status: `G2 PASS for the revalidated first-MVP target DDD baseline 2026-09-16`.

## Purpose

Record Domain Design closure after the selected first-MVP requirements were reopened and revalidated around concrete Component Deployment endpoints, a unified Policy Rule/governance lifecycle, and evidence-derived access candidates.

This is a design gate only. It does not authorize Architecture, Implementation Readiness or production-code changes.

## Scope

```text
Business Connectivity
    -> business Need / justification

Application Communication Catalogue
    -> Application / Component / Interaction / immutable revision

Application Deployment
    -> concrete ComponentDeployment(ComponentRef, ResourceRef)

Resource Catalogue
    -> Resource / AddressSpace / ResponsibilityScope affiliation

Authority Management
    -> protected action authority

TAE + RC + AD + ACC
    -> Evidence Access Recognition
    -> RecognizedAccessCandidate

Business basis + concrete endpoints + exact revision + authority/scope
    -> Access Policy PolicyRule lifecycle
    -> current effective PolicyRule

Access Policy + ACC + AD + RC + NEP
    -> Required Policy Materialization
    -> Access Policy Realization
    -> Provider rendering
    -> Network Environment Operations
```

Evidence Access Recognition and Required Policy Materialization are non-peer compositions. Provider Policy Interpreter/Renderer and Technical Evidence Acquisition/Collectors remain integration/application capabilities rather than Bounded Contexts.

## Target Bounded Context matrix

| Bounded Context | Canonical Tactical owner | MVP Tactical disposition |
|---|---|---|
| Business Connectivity | `business-connectivity/target-tactical-model.md` | PASS — Process/Need identity/currentness remains application-semantic and deployment-independent |
| Access Policy | `access-policy/tactical-model.md` | PASS — one durable PolicyRule lifecycle owns concrete subject, RuleChange governance history, current effective revision and withdrawal |
| Authority Management | `authority-management/tactical-model.md` | PASS — actor/action/scope/time authority remains separate |
| Resource Catalogue | `resource-catalogue/tactical-model.md` | PASS — stable Resource identity, AddressSpace, scope affiliation/responsibility explicit |
| Application Communication Catalogue | `application-communication-catalogue/target-tactical-model.md` | PASS — intra-Application Interaction identity and immutable revisions explicit |
| Application Deployment | `application-deployment/tactical-model.md` | PASS — one concrete ComponentDeployment identity per Component-on-Resource instance |
| Network Enforcement Placement | `network-enforcement-placement/target-tactical-model.md` | PASS — candidate Firewall/policy-locator relevance unchanged |
| Technical Access Evidence | `technical-access-evidence/tactical-model.md` | PASS — evidence remains source-qualified facts only; recognition is downstream composition |
| Access Policy Realization | `access-policy-realization/tactical-model.md` | PASS — comparison/delta/additive intent ownership unchanged |
| Network Environment Operations | `network-environment-operations/tactical-model.md` | PASS — controlled mutation ownership unchanged |

`Access Governance` is no longer a separate target Bounded Context. Its bilateral proposal/approval/rejection/withdrawal semantics have been absorbed into the Access Policy Rule lifecycle. The former target-only AG Tactical document was removed after those current semantics were preserved in `access-policy/tactical-model.md`.

Implemented/current-state documents that still contain Connectivity Decision, ApplicationDeployment, DeploymentInteraction, DCS or compatibility ComponentDeployment semantics remain as-built reconstruction truth and do not redefine this target baseline.

## Cross-context coherence checks

### Business Need versus concrete Rule

```text
Business Connectivity Need
    -> stable InteractionRef

PolicyRule
    -> sourceComponentDeploymentRef
    -> destinationComponentDeploymentRef
    -> current effective revisionRef?
```

PASS.

A Need may outlive one concrete deployment pair or one traffic revision. Deliberate RuleChange submission requires current Process-backed business justification, while recognized brownfield traffic may exist before attribution.

### ACC communication semantics

PASS.

- Interaction endpoints are Components of the same Application;
- cross-Application Interaction is invalid;
- Interaction identity is the stable directed Component pair;
- material traffic change creates a new immutable InteractionContractRevision;
- an exact revision resolves its owning Interaction/endpoints and complete traffic alternatives;
- ACC-current revision changes do not silently modify existing Policy Rules.

### Concrete Application Deployment semantics

PASS.

```text
ComponentDeployment
    ComponentDeploymentId
    ComponentRef
    ResourceRef
    Active | Retired
```

- one ComponentDeployment is one concrete independently addressable deployed Component instance;
- exactly one Component and one Resource are referenced for the first MVP;
- deploying the same Component on another Resource creates another ComponentDeployment;
- redeployment to another Resource is not an in-place move of one identity;
- Resource AddressSpace change leaves ComponentDeployment identity unchanged;
- several ComponentDeployments may reference the same Component;
- the current MVP does not invent a rule forbidding several ComponentDeployments on one Resource;
- no whole-Application `ApplicationDeployment` aggregate is required by target policy semantics.

### Resource semantics

PASS.

```text
Resource
    -> effective AddressSpace [0..1] = HostAddress | Prefix
    -> ResourceScopeAffiliation[]
```

RC owns Resource/address/scope truth. AD references ResourceRef only. Address changes do not alter Resource, ComponentDeployment or PolicyRule identity.

### Policy Rule identity and change lifecycle

PASS.

```text
PolicyRuleId               // AP-owned identity
PolicyRuleRef              // external opaque reference

business uniqueness:
    sourceComponentDeploymentRef
  + destinationComponentDeploymentRef

effectiveRevisionRef?     // current traffic semantics, not Rule identity
```

For one non-Retired directed ComponentDeployment pair there is at most one PolicyRule.

A Rule may exist before first approval with no effective revision. Rejection or withdrawal never deletes the Rule or rewrites history.

### RuleChange rather than parallel Proposal aggregate

PASS.

```text
PolicyRule
    -> RuleChange[]

RuleChange
    ruleChangeId
    revisionRef
    origin
    Need/business basis
    approval basis
    source/destination decisions
    Pending | Approved | Rejected
```

RuleChange is a child entity because separate attempts — including repeated attempts for the same revision — require distinct decision/provenance identity.

It is not a second Aggregate Root or separate proposal lifecycle owner.

The first MVP permits at most one Pending RuleChange per Active PolicyRule, avoiding an otherwise undefined concurrent-proposal ordering rule.

### Current versus proposed policy

PASS.

For an effective Rule on R1:

```text
Rule.effectiveRevisionRef = R1
RuleChange(R2) = Pending
```

R1 remains effective while R2 is Pending or if R2 is Rejected. Only an applicable approved R2 change advances the same Rule to R2.

Withdrawal clears current effectiveness but preserves Rule/change/decision history. Old approved attempts cannot silently reactivate it; a new change under current obligations is required.

### Approval obligations / authority

PASS.

```text
ComponentDeploymentRef -> ResourceRef
RC ResourceRef -> ResponsibilityScopeRef affiliation
AM Actor + Action + ResponsibilityScope + time -> EffectiveAuthority
```

Access Policy owns how these public facts establish source/destination obligations.

The MVP requires exactly one distinct applicable Responsibility Scope per side. Zero or several fail closed. Source and destination approvals are independent and both are required.

Resource responsibility/contact metadata never substitutes for AM authority.

### Evidence Access Recognition

PASS.

```text
TAE technical evidence
+ RC address/Resource correlation
+ AD Resource/ComponentDeployment correlation
+ ACC Component/Interaction/revision semantics
-> RecognizedAccessCandidate | unresolved
```

`RecognizedAccessCandidate` is a derived value, not an authoritative entity or BC.

It may carry concrete source/destination ComponentDeployment refs, exact revision ref and evidence provenance into the same Access Policy submission path as manual creation.

Ambiguous/missing correlation fails closed. Evidence alone never creates an effective Rule, business Need or authorization.

### Access Policy -> materialization

PASS.

```text
EffectivePolicyRule
    policyRuleRef
    sourceComponentDeploymentRef
    destinationComponentDeploymentRef
    revisionRef
```

RPM verifies deployment Components against ACC revision endpoints, resolves exactly one Resource for each concrete deployment and resolves those Resources through RC.

The old source-placement × destination-placement Cartesian expansion is removed from target semantics. Replicas are separate ComponentDeployments and require their own effective policy relationships.

### RC / NEP technical edge

PASS with existing explicit MVP boundary.

RC preserves HostAddress | Prefix. The first target-specific NEP path accepts HostAddress -> HostAddress; Prefix produces unresolved rather than host expansion.

### TAE / configured-state interpretation

PASS.

TAE remains evidence-only. Provider Policy Interpreter separately derives configured effective policy for APR under explicit source/completeness semantics.

Evidence Access Recognition and provider-configured interpretation are separate consumers of TAE and neither transfers policy authority into TAE.

### APR / renderer / NEO

PASS for affected scope.

APR comparison/additive intent, provider rendering and controlled execution semantics are unchanged by the concrete deployment/policy lifecycle revalidation. They consume new upstream published references rather than old ApplicationDeployment placement-set semantics.

## Superseded target assumptions closed by this revalidation

The following are no longer target truth:

- logical whole-Application `ApplicationDeployment` as the policy endpoint identity;
- `ComponentPlacement` set with zero/one/many Resources as target access endpoint semantics;
- source-placement × destination-placement expansion for one Policy Rule;
- `GovernedInteractionSubject = revision + sourceApplicationDeployment + destinationApplicationDeployment`;
- revision identity as part of Policy Rule sameness;
- separate `Access Governance.GovernedAuthorization` and `Access Policy.PolicyRule` owners for the same current authorization fact;
- AG -> AP `AuthorizationGranted / AuthorizationWithdrawn` as a target cross-context handoff;
- a separate top-level Proposal aggregate merely to establish/change one Rule;
- automatic rule multiplication across replicas of one Component.

Git history retains the replaced target baseline. Current as-built compatibility documentation remains where required to reconstruct implemented behavior.

## Explicit non-blocking deferrals

The revalidated first MVP deliberately does not solve:

- several simultaneous Pending RuleChanges and their conflict/ordering semantics;
- generalized several-scope approval algebra;
- nested groups, role inheritance, explicit deny/ABAC/quorum authority rules;
- whether several different ComponentDeployments may share one Resource as a product restriction;
- provider pod/container/process identity and richer ComponentDeployment lifecycle/history;
- richer ACC draft/publish/version presentation;
- Prefix-aware NEP matching;
- several simultaneous Resource addresses/interfaces/VIPs/deployment-specific exposure;
- managed-policy removal/narrowing semantics for APR excess;
- durable pre-submission drafts;
- concrete persistence/API/transport/package realization.

Each has an explicit revisit trigger and is not required to implement the accepted first-MVP behavior.

## G2 evaluation

`G2 PASS` for the revalidated first-MVP target DDD baseline.

Reasons:

- each authoritative fact/decision in the affected path has one owner;
- the former duplicated AG/AP current-authorization ownership is removed;
- concrete ComponentDeployment identity/lifecycle is explicit;
- PolicyRule identity, business uniqueness, revision state and RuleChange history are explicit;
- manual and evidence-derived proposals converge on one authorization lifecycle without evidence gaining authority;
- current versus pending/rejected policy meaning is unambiguous;
- cross-context references are public opaque semantics rather than private persistence joins;
- downstream materialization can reconstruct source/destination address/protocol/port rows without inventing deployment semantics;
- no known P0/P1 semantic ownership, identity, lifecycle or coupling contradiction remains for the selected slice.

```text
Lifecycle stage: S2
Stage state: ACCEPTED
G2: PASS
Implementation authorization: none
```

S3 Architecture may now rely on this baseline for the selected Full Vendor-Neutral Policy Export and its policy-creation/change handoff. No production-code implementation is authorized by G2.
