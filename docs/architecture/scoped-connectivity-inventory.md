# Scoped Connectivity Inventory architecture boundary

Status: `accepted current application-composition boundary`.

Date: 2026-09-09.

## Purpose

Define how the resource-centric Connectivity workspace composes existing semantic owners while preserving their ownership, authority and failure boundaries.

Product behavior is owned by `docs/requirements/scoped-connectivity-inventory.md`. This document owns composition, consuming ports, evaluation order, batching and read-model constraints.

Scoped Connectivity Inventory is not a Bounded Context, aggregate, database owner or source of copied business truth.

## Composition

```text
Authority Management
Resource Catalogue
Application Communication Catalogue
Connectivity Requirements
Requirement-to-Policy Alignment
Connectivity Decision
Access Policy
        |
        v
Scoped Connectivity Inventory application/read composition
        |
        v
HTTP / Web outer adapters
```

Later dimensions may add Technical Access Evidence, Access Policy Realization and Network Enforcement Placement through the same owner-preserving pattern.

## Architectural rules

1. Every contributing fact is obtained through an owner/application contract or a consumer-owned port.
2. The composition does not read peer persistence tables directly.
3. The composition owns orchestration/query semantics only; it creates no copied business truth or lifecycle.
4. One explicit logical `asOf` is propagated to every temporal contributor.
5. Scope admission happens before local inventory data is returned.
6. Independent enrichment failures preserve trustworthy base topology when the product contract permits partial results.
7. Unknown/ambiguous contributor truth is represented explicitly, never converted into false absence.
8. Catalogue visibility never substitutes for protected Requirement/Decision/Rule read contracts.
9. A persistent composite read store/cache is not required by default; add one only from measured workload/consistency evidence.

## Consumer-owned ports

The composition depends on narrow ports equivalent to:

| Need | Semantic provider |
|---|---|
| discover/admit `ReadScopedConnectivity` scopes | Authority Management |
| page effective local Resource references by scope/asOf | Resource Catalogue |
| batch Resource presentation/endpoint realization | Resource Catalogue |
| batch Component Deployments bound to local Resources | Application Communication Catalogue |
| batch exact DCS interactions for those deployments | Application Communication Catalogue |
| coarse Requirement/currentness/alignment by exact interaction | Connectivity Requirements / Alignment composition |
| coarse effective final Decision by exact subject/scope/asOf | Connectivity Decision |
| coarse Rule existence/state/effectiveness by exact subject/asOf | Access Policy |

Port names are implementation-local. Their responsibilities and ownership boundaries are not.

No adapter may replace these contracts with cross-module SQL joins.

## Evaluation order

Recommended read flow:

1. authenticate actor outside the composition;
2. validate offset-aware `asOf`;
3. admit the selected scope through `ReadScopedConnectivity`;
4. page local Resources through Resource Catalogue scope affiliation;
5. batch-enrich local Resource presentation/realization;
6. correlate effective ACC deployment bindings;
7. expand exact ACC interactions for local Component Deployments;
8. resolve remote Resource bindings/realization;
9. enrich Need, Decision and Policy summaries independently.

Failure before local Resource admission returns no local inventory data.

Failure in a later independent enrichment may keep trustworthy Resource/Component/interaction rows and mark only the affected dimension unavailable/unknown when allowed by the requirement contract.

## Paging and batching

Top-level paging is over effective local Resources so a Resource group is not split across pages.

Potentially unbounded child/enrichment operations must be server-bounded and batch-oriented.

The current ACC adapter applies a hard safety bound of 2000 rows to each child-enrichment batch. Exceeding that bound yields explicit partial/unavailable enrichment rather than silent truncation.

Avoid N+1 owner calls where a bounded batch contract preserves the same semantics.

Search/filter/sort must not change semantic ownership or silently exclude required child data without an explicit product contract.

## Read-model strategy

The first implementation computes the inventory from owner facts at read time.

A dedicated persisted read model may be introduced only when evidence establishes a material need such as:
- measured query latency/volume;
- source availability isolation;
- repeatable snapshot needs not satisfied by current ports.

If introduced, it remains derived projection state with explicit freshness/provenance; it does not become authoritative peer business truth.

## Request access orchestration boundary

The current executable action starts only from an existing exact ACC-known interaction.

The Web/application layer may orchestrate:

```text
reuse selected scope + exact interaction
    -> declare/reuse Connectivity Requirement
    -> submit exact Access Rule Proposal
    -> consume Decision
    -> materialize/resolve Allowed Rule
```

The orchestration must call existing application/domain commands. It must not write directly to Requirement, Decision or Access Policy persistence.

It preserves:
- `Required != Authorized`;
- Proposal != Decision;
- Decision != Access Rule.

No persistent Access Request/process state is introduced by this composition.

A Component with no ACC-known exact interaction cannot enter this command path until an accepted ACC/application capability supplies a trusted exact remote/DCS subject.

## Runtime boundary

Current runtime realization is:

```text
Web
  -> authenticated FastAPI outer adapter
  -> Scoped Connectivity Inventory application composition
  -> module-owned adapters/ports
  -> module-owned PostgreSQL repositories
```

Transport DTOs, SQL schema and React state do not define the composition's semantic contract.

## Non-goals

- new Connectivity Bounded Context;
- cross-module persistence joins;
- generic graph/CMDB engine;
- duplicated Requirement/Decision/Rule details;
- generic distributed query platform;
- persistent read store without evidence;
- vendor/device execution semantics.

## Canonical references

- product contract: `docs/requirements/scoped-connectivity-inventory.md`;
- owner semantics: `docs/domain/semantic-ownership.md`, `docs/domain/resource-role-model.md`;
- cross-cutting architecture: `docs/architecture/current-architecture.md`;
- runtime/API details: `docs/engineering/http-api-contract.md`.
