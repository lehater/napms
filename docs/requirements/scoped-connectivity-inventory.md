# Scoped Connectivity Inventory requirements

Status: `accepted I16A WP-02 semantic contract baseline`.

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

I16A closes the relation as:

```text
Resource Catalogue:
Resource --Resource Scope Affiliation--> Responsibility Scope

Authority Management:
Actor --Responsibility Assignment(action,time)--> Responsibility Scope
```

Resource Catalogue owns effective Resource membership in the selected Responsibility Scope. Authority Management independently owns actor/action authority for the same stable scope reference.

The inventory-specific authority action is `ReadScopedConnectivity`.

Rules:
- scope selection is admitted only by one unambiguous effective `ReadScopedConnectivity` authority at the same logical `asOf`;
- local Resources are those with an effective Resource Scope Affiliation to the selected scope at `asOf`;
- one Resource may be local to multiple responsibility scopes;
- Resource Scope Affiliation is temporal and non-identity;
- Resource membership does not imply mutation authority;
- actor authority for a scope does not imply that every Resource belongs to that scope;
- catalogue visibility is independent from both;
- existing Requirement/Decision/Rule governance scopes are not silently rebound when Resource affiliation changes.

Do not model this as `Resource.owner_id` or an identity-defining `Resource.scope_id`.

## Scope discovery and admission

Semantic queries:

```text
DiscoverScopedConnectivityScopes(actor, asOf)
ReadScopedConnectivityInventory(actor, selectedScope, asOf, ...)
```

`DiscoverScopedConnectivityScopes` uses Authority Management action `ReadScopedConnectivity`.

- unambiguous effective assignments produce selectable Responsibility Scopes;
- ambiguous scopes are not selectable and expose no local inventory data;
- absence of a selectable scope is distinct from technical failure;
- `ReadScopedConnectivity` does not imply any mutation or protected business-detail read.

`ReadScopedConnectivityInventory` re-checks the selected scope at the same explicit `asOf`. Caller-supplied actor identity is never trusted.

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

Top-level completeness is defined over Resource Catalogue membership: every Resource effectively affiliated with the selected scope at `asOf` is eligible for the inventory even when it has no current endpoint realization, no Component Deployment binding or no interaction.

Component Deployment membership under a Resource is derived from effective ACC DeploymentResourceBinding at the same `asOf`.

A Component Deployment bound to multiple local Resources may appear under each Resource. This is presentation of the same Component Deployment identity, not duplicated domain identity.

The workspace must therefore distinguish:

1. Resource with no bound Component Deployment;
2. Resource with Component Deployment but no connectivity;
3. known exact interaction with unresolved remote Resource realization;
4. known requirement with no current policy coverage;
5. policy interaction without a current requirement;
6. complete covered interaction.

## Local Component interaction expansion

For each local Resource -> Component Deployment binding, the inventory expands ACC-known exact directed interactions involving that Component Deployment.

Projection rule:

```text
local component == Source      -> outgoing; remote = Destination
local component == Destination -> incoming; remote = Source
```

If both participants are local to the selected scope, the same exact interaction may legitimately appear under both local component paths: outgoing under the source side and incoming under the destination side. The underlying interaction identity remains one exact ACC subject.

Self-interaction or other direction semantics not covered by this rule remain deferred until accepted evidence requires them.

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

## Safe coarse summary contract

`ReadScopedConnectivity` independently admits the coarse overview needed for the workspace. It does not admit protected details.

For each exact interaction row, the composition may return:

### Requirement summary for selected scope

Scope: exact interaction + selected Responsibility Scope + `asOf`.

Structured meaning:

```text
current = Required | None | Unknown
historicalOnly = true | false | unknown
coverage = Covered | Uncovered | NotCurrent | Unknown | NotApplicable
```

Rules:
- `Required` means at least one Active Requirement stored under the selected scope is applicable at `asOf` for the exact interaction;
- `None` means the authoritative query establishes no current Requirement under the selected scope;
- historical/non-current Requirements may cause `historicalOnly=true`;
- coverage uses the accepted I14 exact interaction matching and `asOf` semantics;
- `NotApplicable` means there is no Requirement for which alignment is meaningful;
- no Requirement ID, justification, audit, dependent detail or provenance is exposed by this coarse contract.

### Decision summary for selected scope

Scope: exact RuleSemanticIdentity + selected Responsibility Scope + `asOf`.

```text
Allowed
NotAllowed
NoFinalDecision
Unknown
```

`NoFinalDecision` is an application/read absence result, not a third Connectivity Decision business outcome.

No Decision ID, reason, evidence reference, deciding actor or provenance is exposed without `ReadConnectivityDecision`.

### Policy summary

Scope: exact RuleSemanticIdentity + `asOf`.

Return structured fields rather than inventing one new policy status:

```text
ruleExists = Yes | No | Unknown
operationalState = Active | Inactive | Unavailable
effectiveAtAsOf = Yes | No | Unknown
```

When `ruleExists=No`, operational/effective fields are unavailable rather than fabricated.

No Rule ID, Rule Governance Scope, EffectiveWindow value, decision correlation, properties or Rule audit is exposed without `ReadAccessRule`.

### Detail authority

Detailed Requirement, Decision and Rule sections continue to use their existing independent read authorities.

This coarse contract exists specifically so a resource owner/responsible user can understand the connectivity landscape without being granted policy/security detail access.

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

The table-level Need presentation is derived from the safe Requirement summary for the selected responsibility scope.

Primary user labels may render:
- `Required` when current=Required;
- `—` / `No current need` when current=None and no historical-only fact is useful;
- `Not current` when only non-current matching Requirements exist;
- `Unknown` when authoritative Requirement state cannot be established.

Requirement lifecycle remains `Active | Retired`; these labels are a read projection, not a new Requirement lifecycle.

### Decision

Source: Connectivity Decision.

Final business outcome remains exactly:

```text
Allowed | NotAllowed
```

The overview may also show `No final decision` or `Unknown` as read/application results. Neither is a Connectivity Decision outcome.

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

The overview uses the structured safe Policy summary and may render compact text such as `Active / effective`, `Active / not effective`, `Inactive`, `No rule` or `Unknown`. These are presentation combinations of existing facts, not a new authoritative policy lifecycle.

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
resource page/pageSize
search/filter/sort as needed
```

The UI never supplies trusted actor identity.

One explicit offset-aware `asOf` is used for:
- `ReadScopedConnectivity` authority;
- Resource Scope Affiliation;
- Resource realization;
- DeploymentResourceBinding;
- Requirement currentness/alignment;
- Decision effectiveness;
- Rule effective-state evaluation.

Top-level paging is over the effective local Resource set so Resource group rows are not split across pages. Child collections may be independently bounded, but any truncation must be explicit; silently dropping Component/interaction children is prohibited.

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

- Authority Management: `ReadScopedConnectivity` scope admission and all other independent action authority.
- Resource Catalogue: Resource Scope Affiliation plus Resource/Endpoint identity and realization.
- Application Communication Catalogue: Component Deployment, DeploymentResourceBinding, DCS interaction/traffic semantics.
- Connectivity Requirements: need truth.
- Requirement-to-Policy Alignment: safe requirement-centric coverage.
- Connectivity Decision: final permission truth.
- Access Policy: authoritative Rule/state/effective policy.
- Later: Technical Access Evidence, Access Policy Realization, Network Enforcement Placement.

The composition owns no copied business truth.

## Remaining semantic gates

### P0 — asynchronous decision-process semantics

Required only if the I16A Add Connectivity flow must persist across user interactions before a final Decision exists.

Do not introduce a durable waiting state until this is closed. It does not block the read-only inventory.

### P1 — later fine-grained catalogue visibility

Current global foreign-catalogue read visibility is accepted. Fine-grained visibility remains deferred and does not block I16A.

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
