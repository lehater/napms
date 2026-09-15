# Web UI requirements

Status: `accepted current product/UX direction; target terminology aligned; legacy runtime surfaces are non-normative`.

Date: 2026-09-15.

## Purpose

Define current product-facing Web behavior and information architecture. The Web UI is an outer adapter over accepted NAPMS application/domain capabilities; it is not a second source of catalogue, policy, governance, evidence or realization truth.

Detailed feature semantics remain owned by current requirement/domain/architecture artifacts. HTTP/runtime mechanics and legacy compatibility surfaces remain engineering concerns.

## Primary user model

The normal user journey is responsibility- and resource-centric:

```text
Login
  -> Connectivity / Checker
  -> selected responsibility scope when relevant
  -> Resources and bound application deployments
  -> Business Need / Access Governance / Policy / Realization
```

Catalogue workspaces expose Applications and Resources as task-oriented curation surfaces, not generic CMDB/application-portfolio CRUD.

## Authority, scope and visibility

The authenticated session supplies actor identity. The client never supplies trusted `actorId` or chooses authoritative catalogue curation scopes.

Backend application use cases remain authoritative for every protected read or mutation. UI hiding/disabling is presentation only.

The following remain distinct:

```text
catalogue visibility
!= selected Responsibility Scope
!= Resource Scope Affiliation
!= Resource Responsibility/contact
!= ReadScopedConnectivity
!= catalogue mutation authority
```

Catalogue mutation uses backend-enforced Authority Management actions. Readability does not grant mutation or protected Business Connectivity / Access Governance / Access Policy access.

## Information architecture

Navigation labels are product vocabulary and need not mirror Bounded Context names, but their semantics must map to current target owners.

Current non-APR surfaces may retain compatibility routes while runtime migration is pending. Labels such as `Needs`, `Decisions`, or a legacy `Realization` route must not be interpreted as preserving Connectivity Requirements, Connectivity Decision, or superseded APR stage models as target domain concepts.

Do not present implemented areas as Planned. Future APR navigation may be accepted only after target use cases and read/mutation authority are designed.

## Connectivity

Connectivity is the normal resource-centric workspace.

Purpose: show Resources in the selected responsibility scope, bound Component Deployments, incoming/outgoing connectivity relationships, remote side, Business Need, Access Governance, Access Policy and independently derived realization state.

Canonical hierarchy:

```text
Resource
  -> Component Deployment
      -> Connectivity Relationship
```

Resources/Deployments with zero connectivity remain visible. Direction is relative to the local side. Human-readable interaction/service meaning leads; protocol/ports and stable IDs are secondary technical details.

`Needed`, governance/consent state, `Authorized`, `Materialized` and `Realized` must never be collapsed into one generic status.

Contextual access initiation reuses known local scope/resource/deployment and backend discovery for valid remote/interaction choices. The UI must not assemble arbitrary stable-ID combinations.

## Checker

Checker is the technical-entry workspace for a traffic tuple. It presents owner-preserving Resource/Application context, policy summaries, Network Context information, stored configured Technical Access Evidence and Resource Responsibility/contact information.

It must preserve ambiguous/historical/unknown address attribution and missing evidence. Configured evidence is not shown as authorization. Checker-specific network-context uncertainty does not define APR target-selection semantics.

## Applications catalogue

Applications exposes the accepted hierarchy:

```text
Application
  -> Component
      -> Component Deployment
          -> Resource
          -> Directed Interaction contracts
```

Normal flows use backend discovery for NAPMS-owned references and do not require users to paste UUID combinations. Stable IDs/provenance remain progressively available while readable labels and structure lead normal work.

Interaction semantic correction creates a new immutable contract revision; it does not rewrite a revision already referenced downstream. Component Deployment identity remains bound to one Resource for its lifetime; moving the component creates another deployment.

## Resources catalogue

Resources is an operational catalogue workspace over Resource Catalogue truth.

It supports bounded search/paging, Resource identity/lifecycle, Endpoint realization history, Resource Scope Affiliation and Resource Responsibility/contact facts. Missing current relations are represented explicitly rather than hidden or fabricated.

Responsibility Scope and Person/Team values may be external correlation references where no registry adapter exists. The UI must not imply that entering such a reference creates organization identity or action authority.

## Business need

The product may label a workspace `Needs`, but its target meaning is Business Connectivity truth: Process-backed Connectivity Need, justification/currentness and interaction correlation.

The UI must not expose the superseded `ConnectivityRequirement` aggregate, its `Active | Retired` lifecycle, Requirement Governance Scope, or Requirement-to-Policy Alignment vocabulary as target semantics.

Absence of a current Need does not mean access is denied. Unknown/incomplete justification remains explicit.

## Access governance

The product may temporarily retain a `Decisions` compatibility route, but target semantics come from Access Governance, not the superseded single final `ConnectivityDecision(Allowed | NotAllowed)` model.

The UI must represent the Access Request history and required bilateral source/destination approval obligations without collapsing them into one person's decision. Grant requires the accepted source-side and destination-side consents; withdrawal/revocation follows the accepted Access Governance contract. Actor authority for each action remains independently evaluated by Authority Management.

Protected governance provenance/history is exposed only when independently admitted.

## Access Policy

Policy surfaces present authoritative Access Policy truth. Readable source/destination/interaction meaning leads; stable identity, provenance, operational state and effective time remain available as required.

Access Policy authorization must not be inferred directly from Business Need, catalogue ownership, governance UI state, configured evidence or device state.

## Effective policy and materialization

Effective policy answers what authorized policy applies for a logical scope/time. Required Policy Materialization is a derived composition and is not presented as a new peer source of truth.

Normalized technical materialization preserves correlation, realization inputs, interaction semantics, logical/effective time and provenance. It does not invent configured/device state.

## Access Policy Realization UI

No target APR screen/stage contract is accepted beyond current APR domain/revalidation artifacts.

The eventual UI must be derived from accepted APR use cases such as realization assessment, semantic delta inspection, policy-change design and verification. It must not preserve old stage/status vocabulary merely because current runtime code or a legacy Realization screen contains it.

## Catalogue mutation UX

Forms must use backend discovery for NAPMS-owned relationships, prevent accidental duplicate submission, keep backend/domain validation authoritative, distinguish authorization/validation/conflict/transport failures, and never trust client actor identity, provenance, command time or authority scope.

Rename/retire, create-new-version, end-relation and immutable-revision behavior must remain distinct rather than flattened into generic edit/delete.

## Interaction and layout baseline

The UI remains desktop-first control-plane software with dense operational tables/forms and WCAG 2.2 AA target.

Potentially unbounded data uses server-side paging/filter/search where required; shareable query state belongs in the URL where reasonable. Loading, genuine empty, filtered-empty, authorization-limited and retryable-failure states are distinct. Status must not rely on color alone.

Responsive baseline:
- `>=1280px`: full desktop shell;
- `768..1279px`: compact/collapsed navigation and horizontally scrollable dense tables as needed;
- `<768px`: functional navigation/forms/details; mobile is not the primary optimization target.

## Legacy runtime boundary

The current implementation may still contain routes, DTOs and pages named for Connectivity Requirements, Connectivity Decision and Requirement-to-Policy Alignment. They are migration evidence only.

New product requirements and target UI design must not cite those names/state machines as normative domain vocabulary. During migration an outer adapter may translate target concepts to legacy runtime contracts, but the translation must remain explicit and temporary.

## Non-goals

Current Web direction does not introduce:
- generic CMDB/application portfolio management;
- automatic ownership/responsibility-to-authority mapping;
- fabricated graph/path semantics;
- fake metrics/dashboard data;
- duplicated business truth in frontend state;
- preservation of Connectivity Requirements or Connectivity Decision as target concepts;
- preservation of superseded APR UI stages/statuses as target semantics.

## Canonical references

- context relationships: `docs/domain/context-map.md`;
- strategic ownership: `docs/domain/strategic-model.md`;
- Business Connectivity: `docs/requirements/business-connectivity-g1.md`;
- Access Governance: `docs/requirements/access-governance-g1.md`;
- Scoped Connectivity Inventory: `docs/requirements/scoped-connectivity-inventory.md`;
- Access Policy: `docs/requirements/access-policy-core.md`;
- APR: `docs/domain/access-policy-realization/README.md`;
- current runtime: `docs/engineering/current-state.md`.
