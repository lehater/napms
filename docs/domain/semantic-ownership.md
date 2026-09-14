# Semantic Ownership

Status: `S2 revalidated through required-policy materialization`.

This file defines semantic ownership, not runtime/service ownership.

## Ownership map

| Knowledge / decision | Semantic owner | Upstream authority / source | Primary result |
|---|---|---|---|
| Business Process meaning/responsibility and application-semantic Connectivity Need | **Business Connectivity** | business/stakeholder inputs + ACC Interaction meaning | Business Process / Connectivity Need |
| concrete Access Request, side obligations/decisions, bilateral grant/withdrawal | **Access Governance** | Process-backed Need + deployed Interaction + Authority Management | governance history / Authorization Granted or Withdrawn |
| current authoritative Policy Rule truth and effective semantic authorization | **Access Policy** | Access Governance + trusted ACC subject | Policy Rule / effective authorized policy |
| scoped actor/action authority | **Authority Management** | group/role/scope assignment semantics | Effective Authority |
| Resource/Endpoint identity, current corporate-visible address realization and scope affiliation | **Resource Catalogue** | trusted catalogue/network inventory facts | Resource / ResourceEndpoint / current realization |
| application/component/ComponentDeployment/Interaction contract | **Application Communication Catalogue** | authorized catalogue sources | deployed Interaction subject + immutable traffic contract |
| normalized required technical predicate derived from one or more effective Policy Rules | **non-peer Required Policy Materialization composition** | Access Policy + ACC + Resource Catalogue | derived normalized predicate + contributing Rule refs |
| candidate enforcement target and policy locator for technical pair | **Network Enforcement Placement** | routing/interface state + overrides + locator bindings | candidate Firewall / policy locators |
| target-specific aggregate required effective policy | **non-peer Required Policy Materialization composition** | normalized required predicates + NEP result | TargetRequiredPolicy or unresolved materialization |
| normalized source-qualified technical access evidence | **Technical Access Evidence** | device/traffic/import sources | Technical Access Evidence |
| effective-policy realization assessment, semantic delta, change design and proposed-result verification | **Access Policy Realization** | TargetRequiredPolicy + comparable configured effective policy | Assessment / Delta / Change Design / Verification |
| provider-specific rendering | `DIRTY` / owner under revalidation | verified vendor-neutral intent + provider semantics | target representation |
| provider/device mutation lifecycle and execution provenance | **Network Environment Operations** | target representation + Authority Management + provider observations | Network Operation Result |

## Required Policy Materialization ownership

Required Policy Materialization is explicitly **not a peer Bounded Context**. It is derived composition that owns only the meaning of its derived result and provenance, never the source truths used to compute it.

Conceptual derivation:

```text
Effective Policy Rule
    -> source/destination ComponentDeployment refs
    -> exactly one Resource per Deployment
    -> every current ResourceEndpoint
    -> current corporate-visible address/prefix when present
    + immutable Interaction traffic semantics
    => normalized required technical predicates

technical address pair
    -> NEP
    -> candidate firewall + policy locator

all predicates for same comparable target/locator
    => TargetRequiredPolicy
```

### Derived-result invariants

- materialization must be deterministic for an explicit set of upstream facts/logical time;
- it does not reinterpret whether a Policy Rule is authorized;
- it does not own Deployment, Resource, Endpoint, address, Interaction or NEP target identity;
- deduplicating the same normalized predicate preserves every contributing semantic Policy Rule reference/provenance;
- revoking one Rule removes only its contribution; a predicate survives when another effective Rule still requires it;
- candidate placement is exactly the NEP result; materialization does not reconstruct routing/path semantics;
- APR receives only comparable target-specific required policy and does not reconstruct this chain itself.

### Unresolved materialization

A semantic authorization may be valid but not technically materializable. Such cases remain explicit `unresolved` when required input is absent/ambiguous, including missing current address realization or missing comparable policy locator.

`unresolved` is not:

```text
empty required policy
APR missing
APR excess
realized
```

APR comparison begins only when the required side and configured side can refer to the same comparable target/scope.

## Resource Catalogue realization authority

Resource Catalogue owns:

```text
Resource
    -> ResourceEndpoint [0..N]
        -> current corporate-visible AddressRealization [0..1]
```

`ResourceEndpoint` is a stable logical L3 presence. Address changes do not change Endpoint identity. Resource/Endpoint may exist before address assignment.

For MVP one Endpoint has at most one current address/prefix. Resource Catalogue records the address/prefix meaningful in corporate access-management space; NAT discovery/calculation is external.

Canonical target contract: `docs/domain/resource-catalogue/target-realization-model.md`.

## Governance ownership

Business Connectivity owns Need, Access Governance owns bilateral consent history/current grant-withdrawal semantics, Authority Management owns effective action authority, and Access Policy owns current Policy Rule truth. None of these truths imply another.

## Network Enforcement Placement authority

NEP owns candidate target/policy-locator relevance for supplied technical source/destination pairs. Candidate relevance is not proof of end-to-end traversal. Materialization and APR must not second-guess this decision.

A candidate Firewall with no policy locator remains a real NEP result but is unresolved for a concrete target-policy comparison.

## Access Policy Realization authority

APR owns normalized comparison of `TargetRequiredPolicy` against comparable configured effective policy, including exact:

```text
common  = required ∩ configured
missing = required - configured
excess  = configured - required
```

It also owns vendor-neutral change design and semantic verification of the proposed result. Provider rendering remains a separate unresolved boundary.

## Independent truth dimensions

```text
Observed
Recognized
Needed
Requested
Side consent/rejection history
Authorization granted/withdrawn
Policy Rule effective
Technical materialization resolved/unresolved
Target relevance established
TargetRequiredPolicy available
Configured effective policy available
Realization common/missing/excess
Change designed
Proposed result verified
Target representation rendered
Network operation attempted
Convergence post-check observed
```

No dimension silently becomes another context's authoritative truth.
