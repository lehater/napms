# Connectivity Requirements Core requirements — I13

Status: `accepted I13 WP2 behavioral baseline`.

Date: 2026-09-09.

## Purpose

Define the first executable product behavior for the Connectivity Requirements bounded context without choosing transport, database or deployment mechanics.

## Scope

I13 supports:
- declaring one exact semantic connectivity need;
- reading/listing authorized Requirements;
- changing applicability;
- changing justification;
- retiring a Requirement;
- preserving business audit/provenance;
- active semantic uniqueness and idempotent retries.

I13 does not:
- approve/deny connectivity;
- materialize Access Rules;
- calculate Requirement-to-Policy Alignment;
- inspect configured/observed access;
- create ticket/request lifecycle states.

## CR-001 — Declare exact semantic need

An actor with effective `DeclareConnectivityRequirement` authority for one scope/time may declare a Requirement containing:
- Dependent Component Deployment;
- exact Required Semantic Interaction;
- Requirement Applicability;
- non-empty Requirement Justification.

The exact Required Semantic Interaction is:
- Source Component Deployment;
- Destination Component Deployment;
- immutable DCS revision.

The selected DCS must structurally describe the exact directed interaction through trusted ACC facts.

The Dependent must be one of the two participating Component Deployments.

## CR-002 — Declaration authority does not authorize access

Successful declaration creates/resolves only a Connectivity Requirement.

It must not by itself:
- produce `Allowed`;
- call a Connectivity Decision workflow;
- create/materialize/activate an Access Rule;
- assert configured access.

## CR-003 — Stable Requirement identity and active semantic uniqueness

Each authoritative Requirement has a stable `ConnectivityRequirementId`.

At most one Active Requirement exists for:

```text
RequirementGovernanceScope
+ Dependent Component Deployment
+ exact Required Semantic Interaction
```

Repeated/concurrent declaration of the same active semantic key resolves one authoritative Requirement ID.

Applicability and Justification are not members of the semantic uniqueness key.

## CR-004 — Governance scope is authoritative stored context

Declaration stores the accepted authority scope as `RequirementGovernanceScope`.

Later read/mutation authorization uses the stored scope.

A caller cannot replace trusted scope on an existing Requirement.

Responsibility/assignment changes may change who is authorized without changing Requirement identity or stored governance scope.

## CR-005 — Applicability

Requirement Applicability is either:
- `Ongoing`;
- `AbsoluteWindow(start,end)`.

Absolute window rules:
- both instants offset-aware;
- `start < end`;
- half-open `[start,end)`.

An authorized actor may change applicability on an Active Requirement without changing Requirement ID.

Same-value request is an explicit no-op and creates no accepted-change audit.

## CR-006 — Justification

Requirement Justification is mandatory and non-empty.

An authorized actor may change it on an Active Requirement without changing Requirement ID.

Same-value request is a no-op and creates no accepted-change audit.

Connectivity Decision/approval reasons are not stored as Requirement Justification.

## CR-007 — Lifecycle

I13 lifecycle:

```text
Active -> Retired
```

Retired is terminal.

Retirement preserves:
- Requirement ID;
- governance scope;
- Dependent;
- Required Semantic Interaction;
- historical applicability/justification/audit.

Mutation of applicability/justification on Retired is rejected.

Repeated retirement is an explicit no-op.

## CR-008 — New semantic subject means another Requirement

Changing either:
- Dependent Component Deployment;
- Source Component Deployment;
- Destination Component Deployment;
- DCS revision

does not mutate the existing Requirement identity.

The resulting semantic need is declared as another Requirement.

If appropriate, the old Requirement may be retired separately.

## CR-009 — Re-declaration after retirement

A Retired Requirement does not permanently reserve its prior active semantic key.

A later declaration of the same scope + dependent + exact interaction creates a new lifecycle episode with a new Requirement ID.

Historical Requirement records remain intact.

## CR-010 — Authority actions

I13 uses distinct Authority Management actions:
- `DeclareConnectivityRequirement`;
- `ReadConnectivityRequirement`;
- `SetConnectivityRequirementApplicability`;
- `SetConnectivityRequirementJustification`;
- `RetireConnectivityRequirement`.

No broad `ManageConnectivityRequirement` action is introduced.

Denied, unknown or ambiguous required authority fails closed.

## CR-011 — Authorized workspace read

List:
- discovers unambiguous effective `ReadConnectivityRequirement` scopes;
- returns only Requirements whose stored governance scope is permitted;
- ambiguous scopes expose no Requirement data.

Detail:
- loads one Requirement;
- checks `ReadConnectivityRequirement` against its stored governance scope;
- denied/unknown authority returns no Requirement data.

Read permission does not imply mutation permission.

## CR-012 — Business audit/provenance

Declaration records at least:
- Requirement ID;
- actor;
- effective business action time;
- stored governance scope;
- Authority reference;
- exact semantic interaction;
- ACC validation/provenance reference where available;
- initial applicability;
- initial justification.

Accepted applicability/justification/lifecycle changes record:
- previous/new business value or transition;
- actor;
- effective time;
- stored scope;
- Authority reference.

Technical request logs do not replace business audit.

## CR-013 — Concurrency and uncertain persistence

Declaration and mutation must not report a successful authoritative result unless the authoritative outcome is established.

Concurrent declaration of the same active semantic key converges to one Requirement.

Stale conflicting property/lifecycle mutations cannot silently last-write-win.

Persistence/commit uncertainty must be represented explicitly and safely.

## CR-014 — Catalogue failures

Unknown/invalid Required Semantic Interaction or subject mismatch produces no Requirement.

Presentation labels are optional and do not define semantic validity; stable ACC identities remain authoritative.

## CR-015 — No hidden owner authorization

The Requirement does not grant rights from a stored `owner` field.

Who may act is determined by Authority Management for the Requirement Governance Scope and effective time.

Historical action actors remain provenance only.

## Trace

Tactical semantics:
- `docs/domain/connectivity-requirements/tactical-model.md`.

Executable examples:
- `docs/requirements/connectivity-requirements-acceptance-examples.md`.
