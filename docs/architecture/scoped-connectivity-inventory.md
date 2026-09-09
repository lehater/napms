# Scoped Connectivity Inventory architecture boundary

Status: accepted application-composition direction; responsibility-scope -> Resource semantic owner remains an I16A blocker.

Date: 2026-09-09.

## Purpose

Define the architectural boundary for the resource-centric Connectivity workspace required by docs/requirements/scoped-connectivity-inventory.md.

This boundary is a read/application composition. It is not a new Bounded Context, aggregate, database owner or source of business truth.

## Composition

Conceptual contributors:

    Authority Management
          |
          | responsibility scope / admitted actions
          v
    Scoped Connectivity Inventory
          ^
          |
    Resource Catalogue
    Application Communication Catalogue
    Connectivity Requirements
    Requirement-to-Policy Alignment
    Connectivity Decision
    Access Policy

Later contributors:

    Technical Access Evidence
    Access Policy Realization
    Network Enforcement Placement

## Architectural rules

1. Every contributing fact is obtained through an application/consumer-owned port or an accepted composition boundary.
2. The composition must not read another module's persistence tables directly to bypass semantic ownership.
3. The composition owns no copied business truth and does not create a new lifecycle.
4. A selected responsibility scope must be resolved to local Resources through the semantic owner accepted by I16A WP-01.
5. Until that owner is accepted, implementation of local-resource derivation is gated.
6. Remote Resource/Component catalogue data is readable under the current product visibility baseline.
7. Protected Requirement/Decision/Rule details remain governed by their existing read semantics.
8. Coarse cross-context statuses require an explicit safe-read rule and must not be obtained by accidental data leakage.
9. Temporal facts are correlated for one explicit logical asOf.
10. Missing/stale/ambiguous contributor data produces explicit partial/unknown presentation semantics; it must not be silently converted to false absence.

## Local-side derivation seam

Accepted product need:

    selected responsibility scope
        -> local Resources

Unknown before I16A WP-01:

- semantic owner of the relation;
- relation identity/cardinality;
- temporal semantics;
- relationship to Authority Management assignments;
- whether one Resource may participate in multiple responsibility scopes.

Do not encode this unknown as Resource.owner_id, Resource.scope_id or an equivalent persistence shortcut before domain closure.

## Catalogue correlation

Existing accepted relationships are reused:

    Component Deployment
        -> effective DeploymentResourceBinding
        -> stable Resource reference
        -> Resource Catalogue realization

The composition must not assume one Component Deployment maps to exactly one Resource.

Exact connectivity remains identified by:

    Source Component Deployment
    + Destination Component Deployment
    + immutable DCS revision

The UI-local direction is a projection relative to the selected local side and does not alter canonical interaction identity.

## Protected-status composition

Requirement-to-Policy Alignment already demonstrates the preferred pattern: a composition may expose a safe derived result without exposing protected Rule details.

I16A must define equivalent rules for any inventory summary that includes:

- Requirement presence/currentness;
- Connectivity Decision outcome;
- Rule presence/state/effectiveness.

If the actor lacks the detailed read authority, the composition either returns an explicitly admitted coarse result or withholds/marks the dimension unavailable. It must never infer permission from catalogue visibility.

## Query shape

Conceptual query:

    actor from authenticated session
    selected responsibility scope
    asOf
    paging/search/filter/sort

Conceptual result:

    local Resources
      -> endpoints
      -> Component Deployments
          -> connectivity relationships
              -> remote Component
              -> remote Resources
              -> access summary
              -> Need summary
              -> Decision summary
              -> Policy summary
              -> Realization summary later

This is architecture meaning, not a transport DTO contract.

## Pagination and read-model strategy

The first implementation should optimize for a minimal useful owner workspace, not for a generic graph query engine.

Requirements:

- server-bounded result size;
- server-side search/filter for potentially unbounded catalogues;
- stable paging semantics;
- no N+1 remote owner calls where a bounded batch port can preserve the same semantics;
- fail-soft presentation enrichment may fall back to stable IDs only where the underlying authorized business result is already known;
- no persistent read-store/cache is required by this document. Introduce one only if measured workload or consistency requirements justify it.

## Add Connectivity command boundary

The Connectivity workspace may start Add Connectivity with local scope/Resource/Component already fixed.

The command path must reuse existing accepted application/domain semantics instead of writing directly to Requirements/Decision/Access Policy persistence.

The exact orchestration may evolve, but it must preserve:

    Required != Authorized
    Proposal != Decision
    Decision != Access Rule

If decision acquisition is asynchronous, the persistent/process semantics must be accepted before a waiting state is represented.

## First implementation cut

Recommended I16A cut:

1. close responsibility scope -> Resource semantics;
2. implement read-only Scoped Connectivity Inventory;
3. expose HTTP read contract;
4. build Connectivity tree-grid;
5. add relationship details;
6. add contextual Add Connectivity using accepted existing flows;
7. defer durable waiting workflow to I16B unless semantic closure is completed earlier.

## Non-goals

- cross-context repository joins;
- new Connectivity bounded context;
- generic CMDB graph;
- fine-grained catalogue visibility;
- device/provider execution;
- realization claims before later roadmap contexts.
