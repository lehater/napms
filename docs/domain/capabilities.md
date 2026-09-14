# Domain capability ownership map

Status: `S2 strategic revalidation in progress`.

A capability is not automatically a Bounded Context, service or deployment unit. The current target ownership follows the 2026-09-14 G1 revalidation and ADR-019.

## Current target capabilities

| Capability | Business question / outcome | Semantic owner / disposition |
|---|---|---|
| Business Process Management | what business process supplies the context/responsibility for connectivity need? | **Business Connectivity** |
| Connectivity Need Management | what application-semantic connectivity does a business process need, independently of authorization? | **Business Connectivity** |
| Business Attribution | which known Process/Need explains an observed or authorized interaction? | **Business Connectivity** |
| Business Justification Reconciliation | which authorization/observed interaction lacks current known business justification, or which Need lacks concrete authorization? | **Business Connectivity** supplies business truth; cross-context composition may derive findings |
| Access Request Submission | what concrete deployed interaction is requesting authorization under which business justification? | **Access Governance** |
| Approval Obligation Determination | which source/destination consent obligations must be satisfied? | **Access Governance** |
| Side Approval / Rejection | what did the authorized representative of one side decide, when and on what authority basis? | **Access Governance** |
| Bilateral Approval Evaluation | have all required side-consent obligations been satisfied? | **Access Governance** |
| Authorization Grant / Withdrawal | is current consent granted for the exact subject, and has either side withdrawn it? | **Access Governance** |
| Governance History | what Requests, side decisions, grants and withdrawals explain current/past authorization? | **Access Governance** |
| Effective Authority Evaluation | may actor A perform action X for scope S at time T? | **Authority Management** |
| Group / Role / Scope Assignment | how is actor/action/scope authority established and administered? | **Authority Management** |
| Current Policy Rule Governance | what authoritative semantic Policy Rule currently exists for an authorized subject? | **Access Policy** |
| Effective Authorized Policy | which semantic Policy Rules are currently effective? | **Access Policy** |
| Resource Scope Affiliation | which access-domain Resources belong to responsibility scope S at time T? | **Resource Catalogue** |
| Resource / Endpoint Knowledge | what Resource exists and how is it currently technically realized? | **Resource Catalogue** |
| Application Communication Contract | what application/component interaction semantics and immutable traffic contract exist? | **Application Communication Catalogue** |
| Component Deployment Knowledge | which concrete Component is deployed on which Resource? | **Application Communication Catalogue**; exactly one Resource per ComponentDeployment in MVP |
| Enforcement Target Relevance | which Firewalls/policy locators are relevant for supplied technical traffic pairs? | **Network Enforcement Placement** |
| Technical Access Evidence Management | what normalized source-qualified technical access material was observed/derived/imported? | **Technical Access Evidence** |
| Policy Realization Assessment | how does configured effective access realize required effective access on a supplied comparable target? | **Access Policy Realization** |
| Semantic Policy Reconciliation | what effective access is common, missing and excessive for a comparable target policy? | **Access Policy Realization** |
| Policy Change Design | what vendor-neutral policy change removes the semantic delta? | **Access Policy Realization** |
| Proposed Change Verification | would the proposed resulting effective policy exactly satisfy the required policy without unintended access? | **Access Policy Realization** |
| Target Policy Rendering | how is verified intent represented for a concrete provider/target? | ownership `DIRTY`; must be revalidated before APR target closure |
| Technical Access Attribution / Explanation | what domain/business meaning can be attributed to technical access for explanation/diagnostics? | cross-context/supporting capability; final owner depends on the consuming explanation use case |
| Scoped Connectivity Inventory | what Resources are local to a selected admitted scope and what independent Need/Governance/Policy/Realization truth can be summarized? | non-peer application/read composition over AM + RC + ACC + Business Connectivity + Access Governance + Access Policy + realization sources |
| Connectivity Impact Analysis | what depends on connectivity and what is the consequence of loss under a scenario? | cross-context analysis; no peer BC accepted |
| Source acquisition/parsing | obtain/parse traffic/device/file sources | adapter/mechanism |

## Business Connectivity

Business Connectivity owns enduring business-purpose truth, not permission.

Strategic invariants:

```text
Needed != Authorized
Needed != Realized
ConnectivityNeed != AccessRequest
```

A Connectivity Need:

- is application-semantic rather than Deployment/IP-semantic;
- is backed by a Business Process;
- may survive concrete deployment/address replacement;
- may lead to several concrete Access Requests;
- may coexist with no current authorization;
- may disappear without rewriting request/approval history.

Observed brownfield traffic may be recognized before Process/Need attribution exists; Business Connectivity may later provide attribution without fabricating a Process during ingestion.

## Access Governance

Access Governance owns concrete consent workflow/history, not business Need or current Policy Rule state.

Strategic invariants:

```text
Grant = source consent AND destination consent
Revoke = source withdrawal OR destination withdrawal
Need != Grant
Grant/Withdrawal != PolicyRule
```

The same actor may satisfy both approval obligations only when Authority Management independently admits that actor for both side/scope actions.

A rejected Request remains governance history and does not create a deny Policy Rule.

Access Governance publishes grant/withdrawal semantics for an exact deployed interaction subject to Access Policy.

## Authority Management

Authority Management owns effective actor/action/scope/time authority and the private mechanics that establish it.

Resource owner/administrator facts do not automatically grant security actions. Consumers such as Access Governance depend on an effective admission result and sufficient authority provenance, not on role/group internals.

## Access Policy

Access Policy owns current authoritative Policy Rule truth and effective authorized-policy projection.

It consumes Access Governance grant/withdrawal semantics and trusted ACC subject identity. It does not run bilateral approval workflow and does not convert rejection into desired deny policy.

Several Needs/Requests may provide provenance for one semantic current Rule.

## Responsibility scope and Resource affiliation

Two independent capabilities use a stable Responsibility Scope reference:

```text
Resource Scope Affiliation
    Resource Catalogue
    -> which Resources belong to scope S at time T?

Effective Authority Evaluation
    Authority Management
    -> may actor A perform action X for scope S at time T?
```

Resource affiliation is non-identity and does not grant authority. Actor authority does not manufacture Resource membership.

## Governance-chain contracts

```text
Business Connectivity
    -- Process-backed Need / justification --> Access Governance

Authority Management
    -- effective actor/action/scope authority --> Access Governance

Application Communication Catalogue
    -- exact deployed Interaction subject --> Access Governance / Access Policy

Access Governance
    -- AuthorizationGranted / AuthorizationWithdrawn --> Access Policy
```

Each consumer must use the published semantic result rather than re-derive the provider's decision from peer-private entities/state.

## Legacy CR/CD disposition

`Connectivity Requirements` and `Connectivity Decision` remain historical/current-runtime concepts but are not current target semantic owners.

Useful capability content has moved as follows:

```text
Connectivity Requirements
    -> Business Connectivity / Connectivity Need Management

Connectivity Decision
    -> Access Governance / side consent + bilateral grant/revocation
```

Legacy Requirement-to-Policy Alignment terminology must be revalidated against the new `Needed` vs `Authorized` owners before target reuse.

## Network Enforcement Placement

NEP determines relevant Firewalls and policy/ACL locators for supplied technical traffic pairs from current collected network state plus explicit active overrides. APR consumes this result and does not re-run placement relevance reasoning.

## Technical Access Evidence

Configured, TrafficDerived and Imported evidence are source-qualified technical evidence. Evidence does not authorize desired access. Completeness/currentness required for a comparison must come from an explicit source/consumer contract.

## Access Policy Realization

APR remains a separate Bounded Context for target-specific required-vs-configured semantic reconciliation and policy-change reasoning.

Current stable direction:

```text
supplied comparable target
+ normalized required effective policy
+ normalized configured effective policy
        -> realization assessment
        -> common / missing / excess
        -> vendor-neutral change design
        -> proposed-result semantic verification
```

Provider-specific rendering ownership is still `DIRTY` and must be resolved before APR strategic/tactical closure. Network mutation execution remains downstream.

## Strategic DDD status

ADR-019 establishes Business Connectivity and Access Governance as separate target Bounded Contexts and leaves Authority Management and Access Policy independent.

Remaining strategic questions include semantic-to-technical required-policy materialization ownership and provider-specific normalization/rendering boundaries. Strategic DDD continues only for those affected edges; the old CR/CD grouping is no longer an open alternative.
