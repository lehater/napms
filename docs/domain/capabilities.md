# Domain capability ownership map

Status: `accepted DDD-BDM-010 eight-BC Strategic DDD baseline`.

A capability is not automatically a Bounded Context, service or deployment unit.

## Current capabilities

| Capability | Business question / outcome | Semantic owner / disposition |
|---|---|---|
| Connectivity Requirement Management | what semantic connectivity is needed by an identified dependent concern under defined applicability conditions? | **Connectivity Requirements** |
| Access Rule governance | what concrete Access Rule exists, with what state/authorization? | Access Policy |
| Desired-policy projections | which Rules are authorized/effective? | Access Policy |
| Domain Responsibility Assignment | who may perform which access-domain responsibility? | AM |
| Resource knowledge | what access-domain Resource/Endpoint/current realization exists? | RC |
| Application communication contract | what application/component/deployment/DCS semantics exist? | Application Communication Catalogue |
| Network / Forwarding State | where can traffic traverse? | NEP |
| Enforcement Selection | where is traffic evaluated? | NEP |
| Technical Access Evidence Management | what normalized source-qualified technical access list was observed/derived/imported? | Technical Access Evidence |
| Technical-to-Domain Access Resolution | what domain interaction(s) does a technical predicate represent/cover? | Access Policy Realization |
| Enforcement Policy Derivation / Quality / Optimization | what enforcement policy does the domain consider correct/preferred? | Access Policy Realization |
| Desired-vs-Configured Reconciliation | does configured evidence realize desired access and what semantic delta remains? | Access Policy Realization |
| Requirement-to-Policy Alignment | is required connectivity authorized, denied, uncovered or orphaned relative to current policy? | non-peer composition over Connectivity Requirements + AP (+ AM for command authority) |
| Access Rule Proposal Derivation | which resolved interactions not already represented should be surfaced as proposals? | non-peer application composition over APR + AP |
| Connectivity Impact Analysis | what depends on connectivity and what is the consequence of loss under a scenario? | cross-context analysis; no peer BC accepted |
| Source acquisition/parsing | obtain/parse traffic/device/file sources | adapter/mechanism |

## Connectivity Requirement Management

Domain-owner confirmed on 2026-09-08:

- system/resource owners may declare connectivity need for their owned scope;
- declaring need does not authorize access;
- a different user with corresponding policy/security authority must approve or deny access.

Strategic invariants:

```text
Required != Authorized
Required != Configured/Observed
Authority-to-declare != Requirement
ConnectivityRequirement != AccessRequest/ticket
```

Current identity hypothesis (not a Tactical DDD natural key):

```text
ConnectivityRequirement ~= Dependent x RequiredSemanticInteraction x Applicability
```

Exact aggregate identity/lifecycle and advanced alternative/conditional requirement semantics are intentionally left outside the Strategic DDD baseline.

## Technical Access Evidence identity

Configured, TrafficDerived and Imported evidence are `SAME_CAPABILITY` at the normalized evidence level. They share normalized predicate semantics, provenance, effective time/window, scope and freshness/coverage/confidence vocabulary. Evidence does not authorize desired access.

## Technical-to-Domain Access Resolution identity

Proposal-side and Reconciliation-side matching are `SAME_CAPABILITY`.

> same Technical Access Predicate + same RC/Application Communication Catalogue/effective-time knowledge -> same Domain Access Resolution, independent of consumer.

No consumer-specific resolution mode may change domain meaning.

## Access Rule Proposal Derivation

Proposal remains useful but non-peer while it has no independent identity, lifecycle, acceptance/rejection policy or authority.

## Access Policy Realization

This BC combines Technical-to-Domain Access Resolution, Enforcement Policy Derivation / Quality / Optimization and Desired-vs-Configured Reconciliation because one exact technical/domain coverage algebra must be used consistently in both directions.

Requirement-to-Policy Alignment is deliberately outside APR: it compares `NEEDED` with `AUTHORIZED`; APR compares authorized/desired policy with technical realization/evidence.

## Source acquisition and firewall semantics

NetFlow/syslog capture, vendor polling/parsers, CSV/XLSX import and raw config storage remain adapters/mechanisms. Zones/interfaces/default deny belong to NEP/firewall interpretation, not Technical Access Evidence.

## Strategic DDD closure

`DDD-BDM-010 / P-010-EIGHT-BC` is the accepted current Strategic DDD baseline. `docs/ddd/connectivity-requirements-evidence.md` records the eighth-context evidence and `docs/ddd/bdm-010-delta.json` records the accepted delta.

The deterministic scorer rerun for DDD-BDM-010 was explicitly waived by architectural/domain-owner decision. No DDD-BDM-010 scorer metrics are claimed; the previously generated DDD-BDM-009 metrics remain historical evidence only.

Strategic DDD is closed for the current scope. This statement does not start or imply Tactical DDD.
