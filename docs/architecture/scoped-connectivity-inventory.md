# Scoped Connectivity Inventory architecture boundary

Status: `accepted I16A WP-02 application-composition boundary`.

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
4. A selected responsibility scope is admitted by Authority Management action `ReadScopedConnectivity`.
5. Resource Catalogue owns effective `Resource Scope Affiliation` and therefore resolves local Resources for the admitted scope.
6. Remote Resource/Component catalogue data is readable under the current product visibility baseline.
7. Protected Requirement/Decision/Rule details remain governed by their existing read semantics.
8. Coarse cross-context statuses require an explicit safe-read rule and must not be obtained by accidental data leakage.
9. Temporal facts are correlated for one explicit logical asOf.
10. Missing/stale/ambiguous contributor data produces explicit partial/unknown presentation semantics; it must not be silently converted to false absence.

## Local-side derivation

Accepted I16A model:

    actor
      -> Authority Management: ReadScopedConnectivity(scope, asOf)
      -> Resource Catalogue: effective Resource Scope Affiliations(scope, asOf)
      -> local Resources

Rules:
- ambiguous/unknown scope authority fails closed before local inventory data is returned;
- Resource Scope Affiliation is temporal, non-identity and may be many-to-many;
- actor authority does not manufacture Resource membership;
- Resource membership does not manufacture actor authority;
- catalogue visibility is independent;
- stored Requirement/Decision/Rule governance scopes are not rewritten when Resource affiliation changes.

No standalone Scope aggregate/hierarchy is required by I16A. The stable Responsibility Scope reference is the correlation value shared across owner contracts.

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

The composition has one explicit coarse-read authority boundary: `ReadScopedConnectivity`.

After scope admission, consumer-owned ports may return only the safe summaries accepted by `docs/requirements/scoped-connectivity-inventory.md`:

- selected-scope Requirement currentness/alignment without Requirement identity/reason/history;
- selected-scope final Decision outcome/absence without Decision identity/reason/provenance;
- exact-interaction Rule existence/state/effectiveness without Rule identity/governance scope/provenance.

Detailed reads remain independently protected by `ReadConnectivityRequirement`, `ReadConnectivityDecision` and `ReadAccessRule`.

Catalogue global visibility is never used as a substitute for those protected read contracts.

## Consumer-owned ports

The application composition should depend on narrow consumer-owned ports with semantics equivalent to:

- scope admission/discovery: list/check effective `ReadScopedConnectivity` scopes;
- Resource membership: page effective Resource Scope Affiliations for one scope/asOf and batch resolve Resource presentation/realization;
- ACC correlation: batch resolve Component Deployments bound to returned Resources and list exact DCS interactions involving those deployments;
- Requirement summary: batch coarse selected-scope need/alignment by exact interaction/asOf;
- Decision summary: batch coarse selected-scope effective Decision by exact subject/asOf;
- Policy summary: batch coarse Rule existence/operational/effective facts by exact subject/asOf.

Names above describe responsibilities, not mandatory class/API names.

No composition adapter may bypass these contracts with cross-module SQL joins.

## Evaluation order

Recommended read order:

1. authenticate actor outside the composition;
2. validate offset-aware `asOf`;
3. admit selected scope through `ReadScopedConnectivity`;
4. page local Resources from Resource Catalogue scope affiliation;
5. enrich local Resource realization;
6. correlate effective ACC deployment bindings;
7. expand exact ACC interactions for local Component Deployments;
8. resolve remote Resource bindings/realization;
9. enrich Need / Decision / Policy summaries independently.

Failure before step 4 returns no local inventory data.

Failures in later independent enrichments should preserve trustworthy base rows and mark only affected dimensions unresolved/unknown where the requirement contract permits partial results.

## Query shape

Conceptual query:

    actor from authenticated session
    selected responsibility scope
    explicit offset-aware asOf
    top-level Resource paging
    search/filter/sort

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
- top-level paging is over effective local Resources;
- Resource group rows are never split across top-level pages;
- child collections may be separately bounded only with explicit truncation/continuation metadata;
- server-side search/filter for potentially unbounded catalogues;
- stable paging semantics at one asOf;
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

1. implement Resource Scope Affiliation + ReadScopedConnectivity core contracts from accepted WP-01 semantics;
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
