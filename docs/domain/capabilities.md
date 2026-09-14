# Domain capability ownership map

Status: `S2 revalidated through required-policy materialization`.

A capability is not automatically a Bounded Context, service or deployment unit. Current target ownership follows the 2026-09-14 G1 revalidation, ADR-019 and ADR-020.

## Current target capabilities

| Capability | Business question / outcome | Semantic owner / disposition |
|---|---|---|
| Business Process Management | what business process supplies context/responsibility for connectivity need? | **Business Connectivity** |
| Connectivity Need Management | what application-semantic connectivity does a business process need? | **Business Connectivity** |
| Business Attribution / Justification Reconciliation | which interaction is justified by which Process/Need and where is justification missing? | **Business Connectivity** supplies truth; derived composition may correlate it |
| Access Request / Approval Obligations / Side Decisions | what concrete deployed interaction seeks consent and what did each authorized side decide? | **Access Governance** |
| Bilateral Grant / Withdrawal / Governance History | is current consent granted or withdrawn and what history explains it? | **Access Governance** |
| Effective Authority Evaluation / Group-Role-Scope Assignment | may actor A perform X for scope S at T and how is that authority established? | **Authority Management** |
| Current Policy Rule Governance / Effective Authorized Policy | what semantic network access is currently authorized? | **Access Policy** |
| Resource Scope Affiliation | which Resources belong to scope S at time T? | **Resource Catalogue** |
| Resource / Endpoint / Address Realization | what Resource/Endpoint exists and what corporate-visible address/prefix currently realizes it? | **Resource Catalogue** |
| Application Communication Contract | what Component Interaction and immutable protocol/port contract exists? | **Application Communication Catalogue** |
| Component Deployment Knowledge | which concrete Component is deployed on which Resource? | **Application Communication Catalogue**; exactly one Resource per ComponentDeployment in MVP |
| Required Access Materialization | what normalized technical access follows from current semantic authorization and current catalogue realization? | **non-peer derived composition** over Access Policy + ACC + Resource Catalogue |
| Enforcement Target Relevance | which Firewalls/policy locators are relevant for supplied technical pairs? | **Network Enforcement Placement** |
| Target Required Policy Projection | what aggregate normalized required policy applies to each comparable enforcement target/locator? | **non-peer derived composition** using Required Access Materialization + NEP; ADR-020 |
| Technical Access Evidence Management | what normalized source-qualified technical access material was observed/derived/imported? | **Technical Access Evidence** |
| Policy Realization Assessment / Semantic Reconciliation | how does configured effective access compare with required effective access? | **Access Policy Realization** |
| Policy Change Design / Proposed Change Verification | what vendor-neutral change removes the delta and would its result be semantically exact? | **Access Policy Realization** |
| Target Policy Rendering | how is verified intent represented for a provider/target? | ownership `DIRTY`; revalidate separately |
| Scoped Connectivity Inventory | what independent Need/Governance/Policy/Realization truth can be summarized for an admitted scope? | non-peer application/read composition |
| Connectivity Impact Analysis | what depends on connectivity and what is the consequence of loss? | cross-context analysis; no peer BC accepted |
| Source acquisition/parsing | obtain/parse traffic/device/file sources | adapter/mechanism |

## Governance chain

```text
Business Connectivity
    -- Process-backed Need --> Access Governance

Authority Management
    -- effective actor/action/scope authority --> Access Governance

ACC
    -- deployed Interaction subject --> Access Governance / Access Policy

Access Governance
    -- AuthorizationGranted / AuthorizationWithdrawn --> Access Policy
```

`Needed != Authorized`; a rejected Request is history, not desired deny policy.

## Required Policy Materialization

ADR-020 classifies required-policy materialization as a derived composition because it owns no independent source fact, decision, identity or business lifecycle.

```text
Access Policy effective Rules
+ ACC Interaction traffic contract
+ Resource Catalogue current Endpoint/address realization
        -> normalized required technical predicates
        -> NEP technical source/destination pairs
+ NEP candidate target/policy locators
        -> TargetRequiredPolicy
        -> APR
```

Rules:

- every current source Endpoint address is combined with every current destination Endpoint address for the Rule subject;
- complete immutable Interaction traffic semantics are applied atomically;
- normalized predicates may have many contributing Policy Rules and deduplication preserves provenance;
- target projection groups all required predicates for the same comparable `firewallId + policyLocator`;
- a missing Resource/Endpoint/address/placement/locator produces explicit `unresolved`, not an empty policy and not APR drift;
- revocation recomputes aggregate required policy rather than deleting a historical firewall row;
- the composition uses published context contracts and does not navigate peer-private persistence.

## Resource realization

Resource Catalogue target realization is:

```text
Resource
    -> ResourceEndpoint [0..N]
        -> current corporate-visible address/prefix [0..1]
```

Endpoint identity survives address changes. Resource Catalogue records the corporate-visible realization meaningful for access management and does not calculate NAT.

## Network Enforcement Placement

NEP alone decides candidate Firewall/policy-locator relevance for technical pairs. Materialization and APR must not reinterpret its routing/override reasoning. A candidate without a comparable policy locator remains visible as unresolved for target-policy comparison.

## Access Policy Realization

APR consumes a comparable `TargetRequiredPolicy` plus normalized configured effective policy and owns assessment, exact `common/missing/excess`, vendor-neutral change design and proposed-result semantic verification.

Provider-specific configured-policy normalization/rendering remains the next dirty strategic boundary. Mutation execution remains downstream.

## Legacy disposition

`Connectivity Requirements` and `Connectivity Decision` are historical/current-runtime concepts, not target owners. Legacy Requirement-to-Policy Alignment terminology must not override current `Needed`, `Authorized`, `Materializable` and `Realized` dimensions.
