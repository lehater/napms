# Web UI requirements

Status: `accepted current product/UX direction; target policy terminology aligned 2026-09-16; legacy runtime surfaces are non-normative`.

## Purpose

Define current product-facing Web behavior and information architecture. The Web UI is an outer adapter over accepted NAPMS application/domain capabilities; it is not a second source of catalogue, policy, evidence, authority or realization truth.

## Primary user model

The normal user journey is responsibility- and resource-centric:

```text
Login
  -> Connectivity / Checker
  -> selected responsibility scope when relevant
  -> Resources and concrete Component Deployments
  -> Business Need / Policy Rule / RuleChange / Realization
```

Navigation labels need not mirror Bounded Context names, but semantics must map to current target owners.

## Authority, scope and visibility

Authenticated session supplies actor identity. The client never supplies trusted actorId, command time or authoritative scope.

Backend application use cases remain authoritative for every protected read/mutation. UI hiding/disabling is presentation only.

These remain distinct:

```text
catalogue visibility
!= selected Responsibility Scope
!= Resource Scope Affiliation
!= Resource Responsibility/contact
!= protected action authority
!= PolicyRule formal decision
```

Resource owner/contact metadata never implies policy decision authority.

## Connectivity

Connectivity is the normal resource-centric workspace:

```text
Resource
  -> Component Deployment
      -> Connectivity Relationship
```

Resources/Deployments with zero connectivity remain visible. Direction is relative to the local side. Human-readable interaction/service meaning leads; stable IDs and technical details remain available progressively.

`Needed`, `Proposed`, `Effective`, `Materialized` and `Realized` must never be collapsed into one status.

Contextual access initiation reuses trusted source/destination ComponentDeployment context plus backend discovery of valid Interaction/revision choices. The UI must not assemble arbitrary UUID/IP/port combinations.

## Checker

Checker is a technical-entry workspace for a traffic tuple. It presents owner-preserving Resource/Application context, policy summaries, Network Context information, stored Technical Access Evidence and Resource Responsibility/contact information.

Configured evidence is not authorization. Unknown/ambiguous attribution remains explicit.

## Applications catalogue

Applications exposes target concepts:

```text
Application
  -> Component
      -> concrete Component Deployment
          -> Resource

Application
  -> Interaction
      -> immutable Interaction Contract Revisions
```

Deploying one Component on another Resource creates another ComponentDeployment. Traffic correction creates a new immutable Interaction Contract Revision and never rewrites a referenced old revision.

## Resources catalogue

Resources is an operational workspace over Resource Catalogue truth: Resource identity/lifecycle, AddressSpace history, Scope Affiliation and Responsibility/contact.

Responsibility Scope and Person/Team values may be external correlation references. UI must not imply that entering them creates authority or PolicyRule approval obligations.

## Business Need

A `Needs` workspace represents Business Connectivity truth: Process-backed Connectivity Need, justification/currentness and Interaction correlation.

Absence of a current Need does not mean access is denied. Unknown/incomplete justification remains explicit.

Legacy `ConnectivityRequirement` aggregate/state vocabulary is compatibility-only.

## Policy Rule / RuleChange

Target policy UI presents one `PolicyRule` per concrete directed ComponentDeployment pair and its RuleChange history.

RuleChange state is exactly:

```text
Pending | Accepted | Rejected
```

For an effective Rule on revision R1, a Pending change to R2 must visibly leave R1 effective. Rejecting R2 leaves R1 unchanged. Accepting R2 changes the same Rule's effective revision.

The first MVP UI does **not** require:

- source-side and destination-side approval panels;
- ApprovalBasis display;
- one approver per Resource Scope;
- quorum/order/CAB stages;
- internal modelling of an external ticket/approval workflow.

An admitted user may perform the formal Accept/Reject action directly, or an external integration may record the same final decision. If decision provenance contains an external ticket/workflow reference, the UI may display it as provenance without reproducing that external workflow state machine.

A legacy `Decisions` compatibility route may remain while migration is pending, but it is not target vocabulary.

## Withdrawal

Policy UI may expose explicit withdrawal to an admitted actor. Withdrawal makes the Rule non-effective without deleting Rule/RuleChange history or changing earlier Accepted decisions to Rejected.

Reauthorization is represented by a new RuleChange and new Accepted decision.

## Effective policy and vendor-neutral export

Policy surfaces present authoritative current Access Policy truth. Current effect must not be inferred from Need, Resource ownership, evidence or device state.

The target Vendor-Neutral Policy Export is a backend-produced complete projection of current effective target PolicyRules through ACC + AD + RC.

The table and downloaded CSV must represent the same immutable export result. Browser code does not reconstruct CSV from visible/paged rows.

## Access Policy Realization UI

Future APR UI must derive from accepted APR use cases such as assessment, semantic delta, change design and verification. Legacy stage/status names are not automatically target semantics.

## Catalogue mutation UX

Forms use backend discovery for NAPMS-owned references, prevent accidental duplicate submission, keep backend/domain validation authoritative and distinguish authorization/validation/conflict/transport failures.

Client fields never manufacture actor identity, provenance, command time or authority decisions.

## Interaction and layout baseline

The UI remains desktop-first control-plane software with dense operational tables/forms and WCAG 2.2 AA target.

Potentially unbounded data uses server-side paging/filter/search. Loading, genuine empty, filtered-empty, authorization-limited and retryable-failure states remain distinct; status never relies on color alone.

Responsive baseline:
- `>=1280px`: full desktop shell;
- `768..1279px`: compact navigation / horizontally scrollable dense tables as needed;
- `<768px`: functional navigation/forms/details; mobile is not primary optimization target.

## Legacy runtime boundary

Current implementation may still contain routes, DTOs/pages named Connectivity Requirements, Connectivity Decision, Requirement-to-Policy Alignment or older deployment semantics. They are migration evidence only.

New target UI must not cite those names/state machines as normative domain vocabulary. Explicit compatibility adapters may translate during migration.

## Non-goals

Current Web direction does not introduce:
- generic CMDB/application portfolio management;
- automatic ownership/responsibility-to-authority mapping;
- bilateral/quorum approval workflow as first-MVP target behavior;
- fabricated graph/path semantics;
- fake metrics/dashboard data;
- duplicated business truth in frontend state;
- preservation of Connectivity Requirements or Connectivity Decision as target concepts;
- preservation of superseded APR UI stages/statuses as target semantics.

## Canonical references

- context relationships: `docs/domain/context-map.md`;
- strategic ownership: `docs/domain/strategic-model.md`;
- Business Connectivity: `docs/requirements/business-connectivity-g1.md`;
- formal RuleChange decision behavior: `docs/requirements/access-governance-g1.md`;
- Scoped Connectivity Inventory: `docs/requirements/scoped-connectivity-inventory.md`;
- Access Policy: `docs/requirements/access-policy-core.md` and `docs/domain/access-policy/tactical-model.md`;
- APR: `docs/domain/access-policy-realization/README.md`;
- current runtime: `docs/engineering/current-state.md`.
