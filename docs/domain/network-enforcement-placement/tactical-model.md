# Network Enforcement Placement Tactical Model — I19

Status: `accepted I19 WP-0 Tactical DDD baseline`.

Date: 2026-09-09.

## Purpose

Define the first executable semantics for **Network Enforcement Placement (NEP)**: given one exact source/destination network endpoint pair and explicit logical time, determine and explain the Logical Firewall placement(s) on the normalized forwarding path without interpreting authorization, configured policy, vendor syntax or desired-vs-configured reconciliation.

## Ownership

NEP owns:
- normalized forwarding-path knowledge used for placement;
- stable Logical Firewall identity;
- temporal Logical Firewall <-> provider-realization correspondence;
- Enforcement Attachment semantics;
- Enforcement Selection and its explainability.

NEP does not own:
- Resource or Resource Endpoint identity/realization;
- application interaction/DCS meaning;
- desired Access Rule state;
- configured technical access evidence;
- vendor configuration rendering or provider/device execution;
- I20 realization/reconciliation conclusions.

## First executable Traffic Relation

A **Traffic Relation** is an ephemeral NEP query value, not an aggregate identity.

The first slice contains:
- one exact source IP address;
- one exact destination IP address;
- optional opaque caller provenance used only for explanation.

The first slice deliberately does not claim path invariance across VRF/routing-instance, protocol/port, policy-based-routing, service-chain or other dimensions not represented by the exact endpoint pair.

A path source/adapter may return a complete result only when its source contract can truthfully state that the supplied path semantics are complete for that exact endpoint pair. If another forwarding dimension is required, the adapter returns an explicit knowledge gap and selection is `Unknown`.

Revisit trigger:
- the first accepted environment whose forwarding decision materially depends on a dimension not representable by the endpoint pair; then extend the NEP Traffic Relation before claiming complete placement.

## Normalized Forwarding Path

A **Forwarding Path** is a normalized ordered path fact for one Traffic Relation.

One path is an ordered sequence of **Traversal Points**. Each Traversal Point contains:
- an opaque `ProviderRealizationReference`;
- a normalized `PathAttachmentReference`;
- source-qualified path provenance.

The references are correspondence values, not Logical Firewall identity, Resource identity or vendor syntax.

The first executable slice supports:
- exactly one complete effective path; or
- an explicit complete `NoForwardingPath` fact.

Multiple simultaneous path alternatives/ECMP are not interpreted by the first slice. A source that reports more than one effective path returns `Unknown` with a `MultiplePathSemanticsUnsupported` gap instead of choosing one.

## Path knowledge completeness

The consuming NEP port returns a source-neutral snapshot containing:
- zero or one effective Forwarding Path;
- `noForwardingPath` when absence of a path is positively established;
- `completeForPair`;
- knowledge gaps/provenance.

Semantics:
- missing path knowledge is `Unknown`;
- absence of a path is `NoForwardingPath` only when the source positively establishes that fact for the exact pair/time;
- best-effort or partial path material never becomes a complete placement result.

## Logical Firewall

A **Logical Firewall** is a stable independently configurable enforcement identity.

`LogicalFirewallId` is independent from:
- provider/device realization;
- Resource/Resource Endpoint;
- Path Attachment;
- provider-native policy/configuration identity.

Provider replacement does not replace the Logical Firewall automatically. Logical Firewall retirement and provider-realization retirement are separate facts.

The first slice models Logical Firewall lifecycle as an explicit half-open effective window. A retired/non-effective Logical Firewall cannot be selected at that logical time.

## Provider Realization Correspondence

A **Logical Firewall Correspondence** is a temporal relation:

```text
Logical Firewall
+ ProviderRealizationReference
+ [validFrom, validUntil)
+ provenance
```

Cardinality is intentionally many-to-many across time:
- one Logical Firewall may have several provider realizations;
- one provider realization may host several Logical Firewalls.

For one exact Logical Firewall + provider-realization pair, overlapping effective relation records are an integrity ambiguity unless they are semantically equivalent duplicates that can be provenance-merged.

A provider realization is an external/correspondence reference; NEP does not redefine it as Logical Firewall identity.

## Enforcement Attachment

An **Enforcement Attachment** is the temporal NEP relation that says one Logical Firewall is attached for enforcement at one normalized path attachment on one provider realization:

```text
EnforcementAttachmentId
+ LogicalFirewallId
+ ProviderRealizationReference
+ PathAttachmentReference
+ [validFrom, validUntil)
+ provenance
```

The attachment is its own identity. It is not the Logical Firewall and not the provider realization.

For an attachment to support placement at `asOf`:
- the Logical Firewall must be effective;
- the attachment must be effective;
- an effective Logical Firewall Correspondence must connect that Logical Firewall to the same provider realization;
- the exact provider/path-attachment pair must be traversed by the selected path.

If a relevant effective attachment exists without a trustworthy matching correspondence, placement is `Unknown`, not silently ignored.

## Enforcement Selection

**Enforcement Selection** is a derived, non-persisted result for one Traffic Relation + `asOf`.

Each selected **Enforcement Placement** contains:
- Logical Firewall identity;
- Enforcement Attachment identity;
- provider-realization reference;
- path-attachment reference;
- zero-based traversal position;
- attributable path/correspondence/attachment provenance.

Placements are ordered by path traversal position. Representation order of input facts has no semantic effect.

The same Logical Firewall encountered at distinct traversal positions yields distinct placement occurrences; the path is not deduplicated into one firewall name.

## Selection status

```text
Placed
NoEnforcement
NoForwardingPath
Ambiguous
Unknown
```

### Placed

Use `Placed` only when:
- one complete supported Forwarding Path is established;
- relevant attachment/correspondence knowledge is complete;
- every selected attachment is valid and unambiguous;
- at least one Enforcement Placement exists.

### NoEnforcement

Use `NoEnforcement` only when:
- one complete supported Forwarding Path is established;
- attachment/correspondence knowledge is complete for every traversal point;
- no effective Enforcement Attachment applies.

This is stronger than “none found”.

### NoForwardingPath

Use `NoForwardingPath` only when the forwarding source positively and completely establishes no path for the exact endpoint pair/time.

It is not an authorization or policy-satisfaction conclusion.

### Ambiguous

Use `Ambiguous` when complete supported path knowledge exists but one traversed provider/path-attachment point corresponds to more than one distinct effective Logical Firewall placement after duplicate-equivalent provenance is merged.

All competing placements are preserved; no winner is selected.

### Unknown

Use `Unknown` whenever a truthful complete placement cannot be established, including:
- missing/incomplete forwarding knowledge;
- unsupported forwarding dimensions;
- multiple-path semantics unsupported by the first slice;
- missing/non-unique/corrupt Logical Firewall correspondence;
- missing completeness evidence for attachments;
- invalid temporal state.

Known path/placement witnesses may still be returned for explanation, but completeness is false.

Status precedence:

```text
Unknown > Ambiguous > Placed > NoEnforcement / NoForwardingPath
```

The two terminal “none” states are selected by whether a complete path exists.

## Temporal and correction semantics

Every selection requires an explicit offset-aware `asOf`.

Temporal facts use half-open validity `[validFrom, validUntil)`.

Corrections do not rewrite semantic identity:
- a correction/supersession creates a new fact/version with explicit provenance;
- historical valid facts remain explainable;
- overlapping contradictory effective facts fail closed;
- `RecordedAt` is audit time and does not substitute for effective validity.

The first slice does not infer “latest” from wall-clock order.

## Consumer relationship

I19 keeps NEP consumer-independent.

```text
provider/network source adapters
    -> NEP-owned normalized path/correspondence/attachment facts
    -> Enforcement Selection

Resource/ACC/APR outer composition
    -> may project domain traffic into an NEP Traffic Relation

NEP
    -> never imports APR, Access Policy, TAE, RC or ACC core types
```

I20 may consume NEP placement through an APR-owned projection/port. That later consumer does not change I19 placement meaning.

## Non-goals

I19 does not:
- decide whether traffic is allowed/required;
- decide whether configured rules satisfy desired policy;
- derive Add/Remove/Replace/No-op;
- parse or render vendor policy syntax;
- execute provider/device changes;
- model multipath/ECMP semantics beyond explicit `Unknown`;
- introduce a public operator workflow unless a later accepted product need requires it.
