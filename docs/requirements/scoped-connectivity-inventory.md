# Scoped Connectivity Inventory requirements

Status: `accepted current product contract`.

Date: 2026-09-09.

## Purpose

Define the resource-centric owner workspace that lets an authenticated actor understand the connectivity landscape of one selected responsibility scope without learning NAPMS bounded-context boundaries.

The workspace is a cross-context read composition. It is not a new Bounded Context, aggregate, lifecycle or source of business truth.

Primary user question:

> What Resources are in my selected area of responsibility, what application Components run on them, with whom do they communicate, what access is required/decided/authorized, and later how is that access realized?

## Product model

```text
authenticated actor
    -> selected Responsibility Scope
    -> local Resources
    -> bound Component Deployments
    -> exact Connectivity Relationships
         -> remote Component Deployment
         -> remote Resource(s)
         -> Need
         -> Decision
         -> Policy
         -> Realization later
```

Need, Decision, Policy and later Realization remain independent dimensions. The workspace must not invent one generic connectivity status.

## Responsibility scope and local Resources

The selected Responsibility Scope is the workspace context.

Two independent truths use the same stable scope reference:

```text
Resource Catalogue:
Resource --Resource Scope Affiliation--> Responsibility Scope

Authority Management:
Actor --Responsibility Assignment(action,time)--> Responsibility Scope
```

Resource Catalogue owns effective Resource membership in a Responsibility Scope. Authority Management independently owns actor/action authority for that scope.

The inventory-specific authority action is `ReadScopedConnectivity`.

Requirements:
- scope discovery exposes only scopes with one unambiguous effective `ReadScopedConnectivity` admission;
- reading a selected scope re-evaluates that admission for the requested logical time;
- ambiguous/denied/unknown admission exposes no local inventory data;
- local Resources are those with an effective Resource Scope Affiliation to the selected scope at the same logical time;
- one Resource may be affiliated with multiple scopes;
- Resource Scope Affiliation is temporal and non-identity;
- Resource membership does not imply actor authority;
- actor authority does not manufacture Resource membership;
- affiliation changes do not rewrite Resource identity or stored Requirement/Decision/Rule governance scope;
- caller-supplied actor identity is never trusted.

Do not model the relationship as `Resource.owner_id` or an identity-defining `Resource.scope_id`.

## Catalogue visibility

Current product baseline:
- authenticated users may read Resource Catalogue Resources/Endpoints needed to understand connectivity;
- authenticated users may read ACC Applications, Components, Component Deployments, DCS display/traffic semantics and DeploymentResourceBindings needed to understand connectivity;
- foreign catalogue objects may therefore be shown as remote-side context;
- foreign catalogue objects are read-only unless a separate admitted action permits mutation.

Catalogue visibility is independent from domain-action authority and from protected Requirement/Decision/Rule detail reads.

Fine-grained foreign catalogue visibility remains deferred. A future visibility policy must not redefine catalogue object identity or imply domain-action permission.

## Inventory completeness

The primary hierarchy is:

```text
Resource
    -> Component Deployment
        -> Connectivity Relationship
```

Every Resource effectively affiliated with the selected scope at the requested logical time is eligible for the inventory even when it has:
- no current endpoint realization;
- no bound Component Deployment;
- a Component Deployment with no exact ACC interaction.

A missing child fact must not cause the local Resource itself to disappear.

Component Deployment membership under a Resource is derived from effective ACC DeploymentResourceBinding for the same logical time.

A Component Deployment bound to multiple local Resources may appear under each Resource. This is repeated presentation of one Component Deployment identity.

## Local-relative interaction projection

Exact connectivity identity remains:

```text
Source Component Deployment
+ Destination Component Deployment
+ immutable DCS revision
```

For each local Component Deployment, expand ACC-known exact directed interactions involving it.

Presentation direction is relative to the selected local side:

```text
local == Source       -> outgoing; remote = Destination
local == Destination  -> incoming; remote = Source
```

If both participants are local to the selected scope, the same exact interaction may appear under both local Component paths. This does not create a second domain interaction or Access Rule identity.

Canonical source/destination identities remain available in technical details.

## Row presentation

### Local Resource

Show:
- readable Resource label/reference;
- current/effective endpoint/address as secondary technical data where known;
- stable Resource reference in details.

Technical address is not Resource identity.

### Local Component Deployment

Show catalogue display label first and stable Component Deployment ID as secondary identity.

### Access

Show DCS/service meaning as primary text. Protocol/ports are secondary technical information.

### Remote side

Show the remote Component Deployment and zero/one/many Resource realizations derived through effective DeploymentResourceBinding plus Resource Catalogue realization.

If the remote Component is known but Resource realization is unresolved, present that explicitly. Do not describe it as absence of connectivity.

## Safe coarse summaries

`ReadScopedConnectivity` admits the coarse owner overview only. It does not admit protected business details.

### Requirement summary

Scope: exact interaction + selected Responsibility Scope + logical time.

Conceptual fields:

```text
current = Required | None | Unknown
historicalOnly = true | false | unknown
coverage = Covered | Uncovered | NotCurrent | Unknown | NotApplicable
```

Rules:
- `Required` means a current applicable Requirement exists for the exact interaction under the selected scope;
- `None` means authoritative Requirement truth establishes no current Requirement;
- `Unknown` preserves unavailable/ambiguous Requirement truth;
- coverage follows the accepted Requirement-to-Policy Alignment semantics;
- no Requirement ID, justification, dependent detail, audit or provenance is exposed by this coarse summary.

### Decision summary

Scope: exact RuleSemanticIdentity + selected Responsibility Scope + logical time.

Conceptual values:

```text
Allowed
NotAllowed
NoFinalDecision
Unknown
```

`Allowed | NotAllowed` are final Connectivity Decision outcomes.

`NoFinalDecision` and `Unknown` are read/application results, not additional Connectivity Decision states.

No Decision ID, reason, evidence, deciding actor or provenance is exposed without `ReadConnectivityDecision`.

### Policy summary

Scope: exact RuleSemanticIdentity + logical time.

Conceptual fields:

```text
ruleExists = Yes | No | Unknown
operationalState = Active | Inactive | Unavailable
effectiveAtAsOf = Yes | No | Unknown
```

No Rule ID, Rule Governance Scope, EffectiveWindow value, Decision correlation, properties or Rule audit is exposed without `ReadAccessRule`.

### Protected details

Detailed Requirement, Decision and Rule sections continue to use their own read authorities.

The overview may expose only explicitly accepted coarse results. Catalogue visibility must never be used to bypass protected read contracts.

## Current Request access capability

The current executable contextual action requires an existing exact ACC-known interaction.

```text
selected scope
  -> local Resource
  -> local Component Deployment
  -> existing exact ACC interaction
  -> Request access
```

Known context is reused:
- selected Responsibility Scope;
- local Resource;
- local Component Deployment;
- exact source Component Deployment;
- exact destination Component Deployment;
- immutable DCS revision.

The user supplies only missing intent such as applicability/validity and justification when a new Requirement is needed.

Behavior:
- if a current Requirement already exists, reuse it rather than rewriting it;
- if no current Requirement exists and no historical/non-current state blocks the simple path, declare the Requirement first;
- then submit the exact Access Rule Proposal using the existing accepted proposal flow;
- `Allowed` may materialize/resolve an Access Rule;
- `NotAllowed` creates no Access Rule;
- if Requirement declaration succeeds and a later proposal step fails, the Requirement remains authoritative and the partial outcome is reported explicitly.

This orchestration does not create a persistent Access Request identity or lifecycle.

The invariants remain:

```text
Required != Authorized
Proposal != Decision
Decision != Access Rule
```

## Zero-interaction Components

A Component Deployment with no ACC-known exact interaction has no trusted remote Component/DCS subject that NAPMS can currently propose.

Current behavior:
- show the local Resource/Component;
- state that no catalogued communication interaction is known;
- do not show a fake Add Connectivity / Request access action from that row.

Revisit when ACC or another accepted application-owned capability can author/select a new exact communication contract for that Component without arbitrary UUID/port construction.

## Decision-process state

Connectivity Decision remains a final business result:

```text
Allowed | NotAllowed
```

A product need exists to represent submitted connectivity awaiting a final Decision, but no persistent waiting lifecycle is accepted yet.

Until an owning application/domain process and lifecycle are explicitly accepted:
- do not add `Pending`, `Approved`, `Rejected`, `UnderReview` or `Revoked` to Connectivity Decision;
- do not persist/display a waiting business state merely for UI convenience.

This remains a gate for future Decision workflow work, not for the current read inventory.

## Query semantics and bounded results

Conceptual query input:
- authenticated actor from server/session;
- selected Responsibility Scope;
- explicit offset-aware logical `asOf`;
- bounded Resource paging;
- search/filter/sort as supported.

Use the same logical `asOf` for:
- `ReadScopedConnectivity` admission;
- Resource Scope Affiliation;
- Resource realization;
- DeploymentResourceBinding;
- Requirement currentness/alignment;
- Decision effectiveness;
- Rule effective-state evaluation.

Top-level paging is over the effective local Resource set so Resource groups are not split across pages.

Child collections may be independently bounded only with explicit truncation/continuation or explicit partial/unavailable semantics. Silently dropping Component/interaction children is prohibited.

## Partial results

After scope admission and trustworthy local catalogue topology are established, failure of an independent enrichment may preserve the base row while marking only the affected dimension `Unknown`/unavailable where the contract permits it.

Examples:
- Decision summary unavailable while Need/Policy remain trustworthy;
- remote Resource realization unresolved while the exact ACC interaction remains known.

Unknown/unavailable must never be converted into false absence.

## Non-goals

- generic CMDB/application-portfolio administration;
- a new Connectivity Overview Bounded Context;
- copied cross-context business truth or independent inventory persistence by default;
- arbitrary remote/DCS composition from client-entered identifiers;
- fine-grained foreign catalogue visibility in the current baseline;
- graph visualization as the primary implementation;
- configured/reconciliation claims before their later contexts exist;
- vendor/device rendering or execution.

## Canonical references

- semantic ownership: `docs/domain/semantic-ownership.md`, `docs/domain/resource-role-model.md`;
- detailed examples: `docs/requirements/scoped-connectivity-inventory-acceptance-examples.md`;
- architecture: `docs/architecture/scoped-connectivity-inventory.md`;
- Web product requirements: `docs/requirements/web-ui-requirements.md`;
- runtime/API contract: `docs/engineering/http-api-contract.md`.
