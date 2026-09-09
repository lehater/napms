# Scoped Connectivity Inventory requirements

Status: `accepted product direction; I16A semantic closure required before implementation`.

Date: 2026-09-09.

## Purpose

Define the resource-centric owner workspace that lets an authenticated actor understand the connectivity landscape of one selected responsibility scope without knowing NAPMS bounded-context boundaries.

The workspace is a cross-context read composition. It is not a new Bounded Context, aggregate or source of business truth.

The primary user question is:

> What resources are in my selected area of responsibility, what application components run on them, with whom do they communicate, what access is required/decided/authorized, and later how is that access realized?

## Product model

```text
authenticated actor
    -> selected responsibility scope
    -> local Resources
    -> bound Component Deployments
    -> Connectivity Relationships
         -> remote Component Deployment
         -> remote Resource(s)
         -> Need
         -> Decision
         -> Policy
         -> Realization (later)
```

The user starts from the managed landscape rather than from `ConnectivityRequirement`, `AccessRuleProposal` or `AccessRule`.

## Scope and local-side semantics

The selected scope is the workspace responsibility context. It determines which Resources are presented as the user's local/my side and which actions may be admitted for those objects.

Accepted product requirement:

```text
selected responsibility scope
    -> derive local Resources
```

The exact domain relation and semantic owner that derive local Resources from a scope are not yet accepted in the executable model. I16A must close that question before implementation.

Do not solve the gap by adding `owner_id` or `scope_id` to Resource identity without DDD closure.

A Resource may remain the same Resource when ownership, responsibility, custody, authority or scope relations change.

## Current catalogue visibility baseline

For the current product increment:

- authenticated users may discover/read Resource Catalogue Resources and Resource Endpoints needed to understand connectivity;
- authenticated users may discover/read Application Communication Catalogue Applications, Components, Component Deployments, DCS display/traffic semantics and DeploymentResourceBindings needed to understand connectivity;
- foreign catalogue objects are read-only unless a separate admitted domain action permits mutation;
- the selected responsibility scope determines the local side and admitted actions, not remote catalogue discoverability;
- remote Resources/Components are therefore visible in the first implementation.

This baseline applies to catalogue/domain-description data only. It does not grant global read access to protected Connectivity Requirement, Connectivity Decision or Access Rule details.

The backend remains authoritative for all domain-action admission. Client-side disabling/hiding is presentation only.

## Deferred fine-grained visibility

Fine-grained Resource/Component/Deployment visibility is deferred.

Future semantics must keep these concerns independent:

```text
Visibility = who may discover/read a subject
Authority  = who may perform a domain action
```

A future visibility policy must not redefine Resource, Component or Component Deployment identity.

Revisit trigger: a concrete accepted requirement to restrict catalogue discoverability or metadata exposure.

## Local and remote sides

The workspace uses user-relative terminology:

- **Local/My side**: Resource/Component Deployment derived from the selected responsibility scope.
- **Remote side**: the opposite participant in the exact directed interaction, regardless of its responsibility scope.

Local side is not synonymous with network/source side.

Example:

```text
Web API -> Orders DB
```

If the selected scope owns the DB side, the workspace presents the interaction as incoming:

```text
Orders DB <- Web API
```

Canonical Source Component Deployment and Destination Component Deployment remain available in technical details.

## Resource -> Component -> connectivity hierarchy

The first required presentation is a hierarchical inventory:

```text
Resource
    -> Component Deployment
        -> Connectivity Relationship
```

Resources and Components with zero declared/current connectivity must still appear.

The workspace must therefore distinguish:

1. Resource with no bound Component Deployment;
2. Resource with Component Deployment but no connectivity;
3. known exact interaction with unresolved remote Resource realization;
4. known requirement with no current policy coverage;
5. policy interaction without a current requirement;
6. complete covered interaction.

## Connectivity Relationship

A workspace row is a read projection over an exact directed application interaction plus related independent truths.

Minimum interaction identity:

```text
Source Component Deployment
+ Destination Component Deployment
+ immutable DCS revision
```

The workspace does not create another identity for the same semantic interaction merely for presentation.

## Required row information

### Local Resource

Show:

- human-readable Resource label/reference when available;
- current/effective Resource Endpoint/address as secondary technical information;
- stable Resource reference in details.

Technical address is not Resource identity.

### Local Component Deployment

Show:

- catalogue display label as primary text when available;
- stable Component Deployment ID as secondary/technical identity.

### Direction

Show relative to local side:

```text
-> outgoing
<- incoming
```

Use another direction vocabulary only after accepted semantics require it.

### Access

Primary presentation is the DCS/service-level meaning, for example:

```text
HTTPS
PostgreSQL
DNS
AMQP
```

Protocol/ports are secondary technical information, for example:

```text
TCP 443
TCP 5432
UDP 53
```

Network/security users must be able to expose technical columns/details. Application owners should not be forced to parse firewall-style rows as the primary representation.

### Remote Component

Show the remote Component Deployment using catalogue labels first and stable identity second.

### Remote Resource

Resolve through effective ACC DeploymentResourceBinding plus Resource Catalogue realization for the requested `asOf`.

One Component Deployment may resolve to one or more Resource references. The UI must not assume one-to-one deployment/resource cardinality.

If the remote Component is known but its Resource binding/realization is unknown, show an explicit unresolved technical realization state. Do not present that condition as "no connectivity".

## Independent truth/status dimensions

Do not introduce one generic `Status` for a connectivity relationship.

Keep at least these dimensions independent:

```text
Need
Decision
Policy
Realization
```

### Need

Source: Connectivity Requirements.

Relevant facts may include:

- no current Requirement;
- Required/current;
- NotCurrent;
- Unknown.

Requirement lifecycle remains `Active | Retired`; derived applicability/alignment is not lifecycle.

### Decision

Source: Connectivity Decision.

Final business outcome remains exactly:

```text
Allowed | NotAllowed
```

Absence, inaccessible data, ambiguity and runtime uncertainty are not third business outcomes.

### Decision process

A user requirement exists to understand connectivity that has been submitted but is still awaiting a final decision.

This state is **not** accepted as a Connectivity Decision state.

Before UI values such as `Waiting` or `Under review` become durable product semantics, I16A/I16B must determine whether the process is:

- an application workflow with no independent business identity; or
- a distinct domain process/entity with its own lifecycle and semantic owner.

The frontend must not invent this lifecycle.

### Policy

Source: Access Policy / Requirement-to-Policy Alignment.

Keep distinct:

- Rule existence;
- Rule operational state `Active | Inactive`;
- effective contribution at explicit `asOf`;
- Requirement coverage `Covered | Uncovered | NotCurrent | Unknown`.

`Uncovered` must never be relabelled `Denied`.

### Realization

Planned for Technical Access Evidence / Access Policy Realization / Network Enforcement Placement increments.

No configured/satisfied status is shown before accepted semantics exist.

## Protected business-detail reads

Current global catalogue visibility must not bypass existing business read authority.

The inventory may expose a coarse cross-context summary only through an explicitly accepted safe read contract.

Examples:

- Requirement reason/history requires the applicable Requirement read contract;
- Decision reason/provenance requires `ReadConnectivityDecision`;
- Rule identity/properties/history requires `ReadAccessRule`.

If a coarse status can be safely exposed without the detail authority, that must be defined by the composition contract, similarly to the accepted I14 alignment behavior. It must not happen accidentally through repository joins.

## Add Connectivity entry point

A Component Deployment with no required relationship, or an existing uncovered need, may expose a contextual action:

```text
+ Add connectivity
```

The action is part of the Connectivity workspace, not a primary navigation destination.

Known context is reused and must not be requested again:

- selected scope;
- local Resource;
- local Component Deployment;
- local-side direction context.

The user supplies/selects only missing business intent:

- remote side;
- structurally valid DCS/access;
- applicability/validity when required;
- business justification/reason.

### Trusted selection

Remote Component/DCS choices come from backend-provided ACC data and structural validation. The client does not assemble arbitrary UUID combinations.

### User-level operation

The UX may call the action `Request access` or `Add connectivity`.

The backend/application flow may compose multiple accepted domain stages:

```text
declare/resolve Connectivity Requirement
    -> exact proposed Rule semantic subject
    -> proposal
    -> decision
    -> Allowed
    -> Access Rule materialization/resolution
```

This composition must preserve the invariants:

```text
Required != Authorized
Proposal != Decision
Decision != Access Rule
```

The UI must not force the user to navigate manually through Needs -> Compose Connectivity -> Rules merely because backend ownership is split.

## Interaction details

Opening one relationship should provide progressively disclosed sections:

- Need;
- Decision;
- Policy;
- Local side;
- Remote side;
- Technical details;
- Provenance/history where separately admitted;
- Realization later.

Stable IDs and canonical DDD terminology are secondary to readable labels in the normal workflow.

## Query input

The inventory query is conceptually:

```text
actor from authenticated session
selected responsibility scope
explicit asOf
page/search/filter/sort as needed
```

The UI never supplies trusted actor identity.

`asOf` is explicit at the composition boundary when temporal facts are evaluated.

## Conceptual composition output

```text
ScopedConnectivityInventory
    scope
    localResources[]
        resource
        endpoints[]
        componentDeployments[]
            component
            relationships[]
                direction
                exactInteraction
                accessSummary
                remoteComponent
                remoteResources[]
                requirementSummary
                alignmentSummary
                decisionSummary
                policySummary
                realizationSummary?   // later
```

This shape is conceptual product meaning, not an API/DTO/database contract.

## Semantic contributors

- Authority Management: scope/action authority and the future accepted local-resource responsibility relation.
- Resource Catalogue: Resource/Endpoint identity and realization.
- Application Communication Catalogue: Component Deployment, DeploymentResourceBinding, DCS interaction/traffic semantics.
- Connectivity Requirements: need truth.
- Requirement-to-Policy Alignment: safe requirement-centric coverage.
- Connectivity Decision: final permission truth.
- Access Policy: authoritative Rule/state/effective policy.
- Later: Technical Access Evidence, Access Policy Realization, Network Enforcement Placement.

The composition owns no copied business truth.

## Unknowns blocking implementation

### P0 — responsibility scope -> Resource relation

Must decide:

- semantic owner;
- relation identity;
- temporal semantics;
- cardinality;
- whether one Resource may participate in multiple responsibility scopes;
- how changes affect authority without changing Resource identity.

### P0 — asynchronous decision-process semantics

Required only if the real I16 decision flow can remain pending across user interactions.

Do not introduce a durable waiting state until this is closed.

### P1 — coarse status exposure

Define which cross-context summaries are safe to expose when the actor lacks detailed read authority for the underlying Requirement/Decision/Rule.

## Non-goals

- generic CMDB/application-portfolio administration;
- a new `Connectivity Overview` bounded context;
- duplicating domain truth into a UI aggregate;
- adding `Pending` to Connectivity Decision;
- fine-grained foreign catalogue visibility in the first slice;
- graph visualization as the first implementation;
- configured/reconciliation claims before I17-I20;
- vendor/device execution.

## Acceptance examples

### A — resource with no connectivity

Given a selected responsibility scope contains Resource R and ACC binds Component Deployment A to R, and A has no known required/policy interactions, the inventory still shows R -> A with `No connectivity declared` and an admitted `Add connectivity` action.

### B — outgoing covered access

Given local A -> remote B / HTTPS, a current Requirement and an effective Active Rule, show the local/remote Resources and Components, access summary, `Required`, and `Covered/Active` without requiring the user to open separate Needs and Rules pages.

### C — incoming relationship

Given remote B -> local A, show the row from A's responsibility perspective as incoming while preserving canonical source/destination identities in details.

### D — unresolved remote realization

Given A -> B / HTTPS is structurally known but B has no trustworthy Resource realization at `asOf`, show B as the remote Component and `Remote resource: unresolved`. Do not offer "Add connectivity" merely because technical realization is unresolved.

### E — foreign remote catalogue object

Given remote B belongs to another responsibility scope, show its catalogue Resource/Component/endpoint data read-only under the current global catalogue visibility baseline.

### F — protected decision details

Given a coarse decision summary is allowed by an accepted inventory contract but the actor lacks `ReadConnectivityDecision`, the row may show only the admitted coarse summary; reason/provenance/details remain unavailable.

### G — no invented waiting state

Given proposal submission has no final Decision and no accepted persistent workflow model exists, the UI must not persist/display `Pending`, `Approved`, `Rejected` or `Under review` as business state.
