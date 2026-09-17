# Scoped Connectivity Inventory requirements

Status: `G1 target contract aligned to concrete ComponentDeployment and formal RuleChange decisions 2026-09-16`.

## Purpose

Define the resource-centric workspace that lets an authenticated actor understand connectivity for one selected Responsibility Scope without exposing NAPMS bounded-context boundaries.

The workspace is a cross-capability read/action composition, not a new source of business truth.

Primary question:

> What Resources are in my selected area of responsibility, which concrete Component Deployments use them, what application interactions/needs/policy relationships exist, and how is current policy realized?

`Needed`, `Proposed`, `Effective` and `Realized` remain independent dimensions.

## Responsibility scope and local Resources

The selected Responsibility Scope is workspace/read context.

Two independent truths may use the same stable scope reference:

```text
RC: Resource --Resource Scope Affiliation--> Responsibility Scope
AM: Actor --effective ReadScopedConnectivity authority--> Responsibility Scope
```

Requirements:

- scope discovery exposes only scopes for which the actor has effective `ReadScopedConnectivity` authority;
- reading a selected scope re-evaluates that read authority;
- ambiguous/denied/unknown read authority exposes no local inventory data;
- local Resources are those effectively affiliated with the selected scope;
- Resource membership does not imply actor authority and actor authority does not manufacture Resource membership;
- caller-supplied actor identity is never trusted.

This inventory scope does **not** imply source/destination PolicyRule approval sides. The baseline AP RuleChange decision is independent from SCI's resource-selection scope.

## Resource -> concrete Component Deployment projection

Current target semantics:

```text
Resource
    -> ComponentDeployment [0..N]
        -> Component
```

Each target ComponentDeployment has one stable identity and references exactly one Component and one Resource.

Consequences:

- the same Component deployed on R1 and R2 appears as two distinct ComponentDeployments;
- moving/redeploying a Component to another Resource creates another ComponentDeployment rather than mutating a whole-Application placement set;
- changing only Resource AddressSpace leaves the ComponentDeployment identity unchanged;
- a Resource remains visible when it has no current AddressSpace or no ComponentDeployment.

## Local-relative interaction projection

ACC Interactions are application-semantic Component-to-Component templates. For each local ComponentDeployment, inventory may project ACC-known directed Interactions involving its Component and correlate concrete remote ComponentDeployment candidates.

Presentation direction is relative to the selected local deployment:

```text
local Component is Interaction source      -> outgoing
local Component is Interaction destination -> incoming
```

One Interaction may correspond to several separate concrete PolicyRule relationships because replicas are separate ComponentDeployments. The inventory must not collapse them into one logical deployment or automatically copy policy between replicas.

Missing/ambiguous remote deployment or Resource realization is shown explicitly rather than treated as absence.

## Business Need summary

The workspace may summarize known current Business Connectivity justification:

```text
Need = Known | None | Unknown
```

Protected Need/Process details require independent read authority where applicable.

`None` does not mean forbidden. `Unknown` is not converted to absence.

## Policy/change summary

For one concrete directed ComponentDeployment pair, inventory may summarize AP truth without exposing protected audit details:

```text
Rule = Exists | None | Unknown
CurrentEffect = Effective | NotEffective | Unknown
PendingChange = Yes | No | Unknown
LatestDecision = Accepted | Rejected | None | Unknown
```

These values derive from Access Policy and are not a new inventory lifecycle.

A Pending RuleChange does not mean access is effective. A Rejected change is not a deny rule. An Accepted change may establish/update current effectiveness.

The MVP does not display required source/destination approval obligations because they are not baseline domain semantics.

## Realization summary

Where trustworthy realization data exists:

```text
Satisfied
MissingRequiredAccess
ExcessUnauthorizedAccess
Unresolved
Unknown
```

These are realization summaries, not policy decisions.

## Request/propose access action

A user may initiate a RuleChange for a concrete connection when the corresponding application action is admitted.

The action reuses trusted semantic context:

- selected source ComponentDeployment;
- selected destination ComponentDeployment;
- exact immutable ACC `InteractionContractRevisionRef` whose endpoints match those deployments;
- Process-backed Connectivity Need required for deliberate submission.

Conceptually:

```text
sourceComponentDeploymentRef
+ destinationComponentDeploymentRef
+ revisionRef
+ ConnectivityNeedRef
    -> create/reuse PolicyRule
    -> create Pending RuleChange
```

The action does not directly make the Rule effective.

A later formal decision is one of:

```text
Accepted
Rejected
```

Customer-specific approval procedure may happen outside NAPMS and then record this formal decision through an authorized action/integration. SCI does not define bilateral approvals, quorum or Responsibility Scope-derived approvers.

Request/proposal, decide, withdraw and network execution may be independently protected actions.

If no valid Process-backed Need exists, the product must establish business justification through Business Connectivity rather than fabricate one inside inventory.

## Zero-interaction Components

A ComponentDeployment whose Component has no ACC-known Interaction has no trusted remote participant/traffic contract that inventory can propose.

Current behavior:

- show local Resource/ComponentDeployment/Component;
- state that no catalogued interaction is known;
- do not construct arbitrary access from client-entered UUIDs/IP/ports.

Authoring a new Interaction belongs to ACC.

## Query semantics and bounded results

Conceptual query input:

- authenticated actor from server/session;
- selected Responsibility Scope for inventory read;
- explicit logical `asOf` where time-qualified RC/AM truth is requested;
- bounded Resource paging;
- search/filter/sort as supported.

Use one coherent logical time where owner contracts support time-qualified truth. Partial enrichment remains explicit; unavailable information is `Unknown`, not false absence.

Top-level paging is over local Resources so Resource groups are not split across pages. Bounded child collections require explicit continuation/truncation semantics.

## Non-goals

- a new Connectivity Overview Bounded Context;
- copied cross-context truth as authoritative inventory state;
- authorization inferred from Resource owner/administrator metadata;
- bilateral PolicyRule approval workflow;
- whole-Application deployment/placement-set semantics;
- automatic policy inheritance across Component replicas;
- arbitrary remote/interaction construction from client-entered technical identifiers;
- vendor/device rendering or execution.

## Canonical target references

- Business Connectivity: `docs/requirements/business-connectivity-g1.md`;
- policy decision behavior: `docs/requirements/access-governance-g1.md`;
- Application/Interaction and AD/RC split: `docs/requirements/application-catalogue-domain-target.md`;
- AD Tactical semantics: `docs/domain/application-deployment/tactical-model.md`;
- Resource Catalogue: `docs/domain/resource-catalogue/tactical-model.md`;
- Authority Management: `docs/domain/authority-management/tactical-model.md`;
- Access Policy: `docs/domain/access-policy/tactical-model.md` and `docs/requirements/access-policy-core.md`.
