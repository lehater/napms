# Scoped Connectivity Inventory architecture boundary

Status: `G1-revalidated target application/read composition; legacy runtime migration pending`.

Date: 2026-09-15.

## Purpose

Define how the resource-centric Connectivity workspace composes current target semantic owners while preserving ownership, authority, temporal meaning and failure boundaries.

Product behavior is owned by `docs/requirements/scoped-connectivity-inventory.md`. This document owns composition, consuming ports, evaluation order, batching and read-model constraints.

Scoped Connectivity Inventory is not a Bounded Context, aggregate, database owner or source of copied business truth.

## Target composition

```text
Authority Management
Resource Catalogue
Application Communication Catalogue
Business Connectivity
Access Governance
Access Policy
Access Policy Realization (when realization summary is requested)
        |
        v
Scoped Connectivity Inventory application/read composition
        |
        v
HTTP / Web outer adapters
```

Technical Access Evidence and Network Enforcement Placement may contribute only through accepted owner-preserving contracts required by a concrete read use case. Their presence does not make the inventory an owner of evidence, path or realization truth.

Legacy Connectivity Requirements, Connectivity Decision and Requirement-to-Policy Alignment runtime modules are migration/current-state implementation details. They are not target semantic providers and must not be used to derive new domain contracts.

## Architectural rules

1. Every contributing fact is obtained through an owner/application contract or a consumer-owned port.
2. The composition does not read peer persistence tables directly.
3. The composition owns orchestration/query semantics only; it creates no copied business truth or lifecycle.
4. One explicit logical `asOf` is propagated to every temporal contributor.
5. Scope admission happens before local inventory data is returned.
6. Independent enrichment failures preserve trustworthy base topology when the product contract permits partial results.
7. Unknown/ambiguous contributor truth is represented explicitly, never converted into false absence.
8. Catalogue visibility never substitutes for protected Business Connectivity, Access Governance, Access Policy or realization read contracts.
9. A persistent composite read store/cache is not required by default; add one only from measured workload/consistency evidence.
10. `Needed`, governance/consent state, `Authorized`, `Materialized` and `Realized` remain distinct dimensions.

## Consumer-owned ports

The composition depends on narrow ports equivalent to:

| Need | Semantic provider |
|---|---|
| discover/admit `ReadScopedConnectivity` scopes | Authority Management |
| page effective local Resource references by scope/asOf | Resource Catalogue |
| batch Resource presentation/endpoint realization | Resource Catalogue |
| batch Component Deployments bound to local Resources | Application Communication Catalogue |
| batch exact interactions for those deployments | Application Communication Catalogue |
| coarse current Business Process / Connectivity Need justification | Business Connectivity |
| coarse Access Request / bilateral governance state | Access Governance |
| coarse current/effective Policy Rule authorization | Access Policy |
| coarse realization/reconciliation result when available | Access Policy Realization |

Port names are implementation-local. Their responsibilities and ownership boundaries are not. No adapter may replace these contracts with cross-module SQL joins.

## Evaluation order

Recommended target read flow:

1. authenticate actor outside the composition;
2. validate offset-aware `asOf`;
3. admit the selected scope through `ReadScopedConnectivity`;
4. page local Resources through Resource Catalogue scope affiliation;
5. batch-enrich local Resource presentation/realization;
6. correlate effective ACC Component Deployments and exact interactions;
7. resolve remote Resource context;
8. enrich Business Need, Access Governance and Policy summaries independently;
9. enrich APR realization summary only when the accepted product contract and authority allow it.

Failure before local Resource admission returns no local inventory data. Failure in a later independent enrichment may keep trustworthy Resource/Component/interaction rows and mark only the affected dimension unavailable/unknown when allowed by the product contract.

## Paging and batching

Top-level paging is over effective local Resources so a Resource group is not split across pages.

Potentially unbounded child/enrichment operations must be server-bounded and batch-oriented. Avoid N+1 owner calls where a bounded batch contract preserves the same semantics.

Search/filter/sort must not change semantic ownership or silently exclude required child data without an explicit product contract.

Implementation-specific safety bounds belong to current-state/engineering documentation, not to this target semantic boundary.

## Read-model strategy

The target composition does not require a persisted composite read model.

A dedicated persisted read model may be introduced only when evidence establishes a material need such as measured query latency/volume, source availability isolation, or repeatable snapshot needs not satisfied by current ports. If introduced, it remains derived projection state with explicit freshness/provenance; it does not become authoritative peer business truth.

## Request access orchestration boundary

The target action starts from a trusted ACC-known exact deployed interaction and a Process-backed Connectivity Need.

The Web/application layer may orchestrate:

```text
reuse selected scope + exact interaction + current Business Need
    -> create/submit Access Request
    -> collect required source-side and destination-side governance decisions
    -> on effective grant, let Access Governance publish authorization
    -> let Access Policy own resulting Policy Rule truth
```

The composition must not bypass Access Governance by materializing an Access Rule directly.

It preserves:

```text
Needed != Authorized
Access Request != Policy Rule
Authorized != Realized
```

Request initiation, each required approval/withdrawal action and later network mutation remain independently authorizable according to their owning contexts.

A Component Deployment with no ACC-known exact interaction cannot enter this command path until ACC supplies a trusted exact remote/interaction contract.

## Runtime migration boundary

The repository still contains executable legacy Connectivity Requirements, Connectivity Decision and Requirement-to-Policy Alignment modules. They are evidence of current implementation and migration work only.

Runtime adapters may temporarily translate target application intent to those modules while migration is incomplete, but:
- legacy aggregate names and state machines do not become target contracts;
- new target requirements must not cite legacy modules as semantic owners;
- migration completion should remove obsolete adapters/modules rather than preserve them as parallel domain truth.

## Non-goals

- new Connectivity Bounded Context;
- cross-module persistence joins;
- generic graph/CMDB engine;
- duplicated owner details;
- generic distributed query platform;
- persistent read store without evidence;
- vendor/device execution semantics;
- preservation of Connectivity Requirements, Connectivity Decision or Requirement-to-Policy Alignment as target concepts.

## Canonical references

- product contract: `docs/requirements/scoped-connectivity-inventory.md`;
- context relationships: `docs/domain/context-map.md`;
- strategic ownership: `docs/domain/strategic-model.md`;
- Business Connectivity: `docs/requirements/business-connectivity-g1.md`;
- Access Governance: `docs/requirements/access-governance-g1.md`;
- Access Policy: `docs/requirements/access-policy-core.md`;
- realization/reconciliation: `docs/requirements/policy-realization-reconciliation-g1.md`;
- runtime/current-state details: `docs/engineering/current-state.md` and `docs/engineering/http-api-contract.md`.
