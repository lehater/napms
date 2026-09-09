# I14 WP1 — Requirement-to-Policy Alignment decision packet

Status: `working decision packet`

Date: 2026-09-09.

## Decision scope

Close only the semantic/authority choices required for I14. Do not design Connectivity Decision workflow or configured-state reconciliation.

## Accepted/known

### Disposition

Requirement-to-Policy Alignment is a **non-peer application composition** over Connectivity Requirements + Access Policy.

It has no accepted independent aggregate identity/lifecycle and therefore no persistence by default.

### Matching subject

Both contexts already use the same exact immutable application-semantic triple:

```text
SourceComponentDeploymentId
+ DestinationComponentDeploymentId
+ DcsContractRevisionId
```

Therefore the simplest evidence-supported I14 match is exact equality:

```text
ConnectivityRequirement.RequiredSemanticInteraction
    == AccessRule.RuleSemanticIdentity
```

Not part of the match:
- Dependent Component Deployment;
- Requirement Governance Scope;
- Rule Governance Scope;
- actor;
- justification;
- technical addresses;
- Requirement applicability;
- Rule EffectiveWindow.

Those facts affect currentness/authority/explanation, not semantic interaction identity.

### Time

Alignment uses one explicit offset-aware `asOf`.

Requirement currentness at `asOf`:

```text
LifecycleState == Active
AND
(
  Applicability == Ongoing
  OR applicability.start <= asOf < applicability.end
)
```

Policy coverage at the same `asOf`:

```text
matching AccessRule exists
AND AccessRule.contributes_effect_at(asOf)
```

No hidden wall-clock time.

### Outcome vocabulary supported now

Recommended I14 Requirement-centric vocabulary:

- `Covered` — Requirement is current and exact matching Access Rule contributes effective desired policy at `asOf`;
- `Uncovered` — Requirement is current and no exact matching Access Rule contributes effective desired policy at `asOf`;
- `NotCurrent` — Requirement is Retired or its absolute applicability does not include `asOf`;
- `Unknown` — comparison cannot safely establish coverage because an authoritative dependency/result is ambiguous or unavailable.

`Denied` is **not** admitted in I14.

Reason:
- Access Policy authoritative truth contains Allowed-materialized Rules;
- current product does not persist a durable NotAllowed decision as policy truth;
- absence/non-effectiveness of a Rule proves `Uncovered`, not `Denied`;
- durable decision denial semantics belong to I15/I16.

### Orphan policy

A policy-centric `OrphanPolicy` conclusion is not required for the first I14 owner journey.

Why:
- roadmap says expose policy-without-requirement only where the selected view needs it;
- global absence of Requirement is authority-sensitive when Requirement scopes differ;
- first slice is Requirement-centric and already satisfies the owner-facing product goal.

Revisit orphan policy only if a concrete operator view requires it and its cross-scope read semantics are accepted.

### Persistence

Recommended: no Alignment table/event/audit aggregate.

Alignment is recomputed from current authoritative CR/AP truth at explicit `asOf`.

## One blocking owner choice — status visibility

### Problem

RequirementGovernanceScope and matching RuleGovernanceScope are independent and may differ.

The Requirement owner needs a useful answer in `My Connectivity Needs`, but existing AP read authority is scoped to the Rule governance scope.

I14 must decide whether the owner may see the **derived coverage status** without being allowed to inspect the Rule itself.

### Option A — Requirement read admits derived status; Rule details remain protected

If actor can `ReadConnectivityRequirement` for the Requirement's stored scope:
- Alignment may return `Covered | Uncovered | NotCurrent | Unknown`;
- the composition may inspect Access Policy internally to derive only that status;
- no Rule ID, Rule governance scope, decision reference, policy provenance or Rule properties are exposed unless the actor independently has the corresponding AP read authority.

Consequences:
- directly supports the accepted owner/responsible-user personal-cabinet goal;
- least privilege: status visibility does not grant policy inspection;
- differing governance scopes are supported;
- `Uncovered` is meaningful for the Requirement owner;
- requires canonically accepting that coverage status is part of the Requirement-facing composition read surface.

**Recommendation: Option A.**

### Option B — Require both Requirement read and matching policy read

Return `Covered/Uncovered` only when the actor also has AP read authority for the relevant Rule scope.

Problem:
- when no Rule exists there is no RuleGovernanceScope against which to authorize the negative conclusion;
- the system cannot reliably distinguish true `Uncovered` from `Unknown` for the exact use case that matters most;
- owner workspace becomes much less useful unless owners also receive policy-read authority.

### Option C — Add a new `ReadRequirementPolicyAlignment` authority action

Scope it to RequirementGovernanceScope.

Consequences:
- clean explicit permission;
- but introduces a new authority concept with no current evidence that status visibility needs separate delegation from Requirement read;
- more IAM/configuration surface for the same owner workspace.

Use only if the owner wants status visibility independently assignable from `ReadConnectivityRequirement`.

## Recommended accepted truth table if Option A is chosen

| Requirement at asOf | Exact Rule | Rule effect at asOf | Result |
|---|---|---|---|
| Retired / outside applicability | any | any | `NotCurrent` |
| current | exists | effective | `Covered` |
| current | exists | not effective | `Uncovered` |
| current | absent | n/a | `Uncovered` |
| current | AP dependency ambiguous/unavailable | unknown | `Unknown` |

Rule-level evidence is optional enrichment only under independent AP read admission.

## Consequences for architecture

With Option A:
- create a framework-free alignment application/composition module, not a BC aggregate;
- CR authoritative read establishes the actor may inspect that Requirement;
- AP is consumed through a narrow alignment port returning only exact coverage facts needed for the result;
- optional Rule evidence enrichment uses existing AP read authority independently;
- CR core does not import AP;
- AP core does not import CR;
- no database schema is added for Alignment.

## Revisit triggers

Revisit this packet when:
- I15/I16 admits durable NotAllowed decision truth;
- a policy-centric orphan operator view is selected;
- product requires separate delegation of alignment-status visibility;
- requirements become abstract/alternative rather than exact one-interaction needs.
