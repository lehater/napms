# Network Enforcement Placement Core Requirements

Status: `accepted MVP target by ADR-017; implementation migration pending`.

Date: 2026-09-12.

Decision: `../decisions/ADR-017-nep-candidate-policy-attachment-contract.md`.

## Purpose

Specify observable MVP behavior for Network Enforcement Placement (NEP): for one exact technical source/destination address pair and explicit logical time, return the unordered set of enforcement-device candidates relevant enough to inspect and the source-supported interface/policy attachment information required by downstream consumers.

A proven forwarding path is an optional stronger capability, not an MVP prerequisite.

## REQ-NEP-001 — Evaluate one technical pair at explicit logical time

The domain input is one exact source address, one exact destination address and an offset-aware `asOf`.

An API/application service may batch many pairs for efficiency, but every pair shall be evaluated independently and shall produce its own result.

NAPMS shall not infer `asOf` from wall-clock “now” or persistence recording order.

## REQ-NEP-002 — Candidate set is the primary MVP output

NEP shall return zero or more `EnforcementCandidate` values for the queried pair/time.

Candidate-set semantics:

- candidate membership means the source considers the device/enforcement identity relevant enough to inspect;
- candidates have no semantic order;
- a candidate is not proof that traffic traverses that device;
- the set may be incomplete;
- the set may contain false positives;
- absence of a candidate does not prove no forwarding path or no enforcement;
- source-supported relevance/quality may be preserved as opaque source meaning, but NAPMS shall not manufacture a probability/confidence score.

## REQ-NEP-003 — Keep Logical Firewall identity independent

Where a candidate can be correlated to a stable Logical Firewall, NAPMS shall preserve that identity independently from provider/device realization, Resource identity and policy attachment identity.

Provider replacement shall not automatically create a different Logical Firewall.

## REQ-NEP-004 — Expose candidate device identity

Every candidate shall expose a source-qualified `providerDeviceRef` or equivalent stable provider/device locator sufficient for downstream correlation.

Where available, NEP may additionally expose `logicalFirewallRef` without replacing the provider/device locator required for configured-evidence lookup.

## REQ-NEP-005 — Expose source-supported ingress and egress interface context

For each candidate, NEP may expose:

```text
ingressInterfaceRef?
egressInterfaceRef?
```

These values shall be returned only when supported by source facts.

They describe candidate context and shall not be presented as proof of actual packet traversal.

Missing/ambiguous interface knowledge shall remain explicit rather than be invented.

## REQ-NEP-006 — Expose all known relevant policy attachments

For each candidate, NEP shall expose every policy/ACL attachment known by the source to be relevant for the queried pair/candidate combination.

Cardinality is:

```text
EnforcementCandidate -> PolicyAttachment [0..N]
```

A candidate with no known relevant policy attachment is valid and shall not be silently dropped.

## REQ-NEP-007 — Policy attachment must be locatable downstream

A `PolicyAttachment` shall expose enough source-qualified locator information to retrieve corresponding configured policy evidence where that evidence exists.

The target fields are:

```text
policyRef?
policyName?
attachmentKind
interfaceRef?
direction?
```

At least one source-supported policy locator (`policyRef` and/or `policyName`) shall be present when an attachment is returned.

## REQ-NEP-008 — Preserve vendor-specific attachment topology

NEP shall not require a fixed Cisco-only attachment topology.

A Cisco-like source may expose:

- ingress-interface / inbound policy;
- global policy;
- egress-interface / outbound policy.

Another vendor/source may expose only a global policy or another source-specific set.

Normalized `attachmentKind` may include `ingress`, `global`, `egress` and `vendor-specific`. A global/non-interface policy shall not require an interface reference.

## REQ-NEP-009 — NEP owns policy location, not policy contents

NEP shall return policy locators/attachment metadata only.

NEP shall not copy, parse or own configured ACL/policy entries.

Technical Access Evidence remains the owner of captured/imported/configured policy contents and provenance.

A downstream composition may correlate NEP to Technical Access Evidence using:

```text
providerDeviceRef
+ policyRef and/or policyName
```

## REQ-NEP-010 — Preserve provenance and knowledge gaps

Candidate relevance, interface facts and policy-attachment facts shall preserve attributable source/provenance and explicit effective time where supported by their source contracts.

Missing, ambiguous or contradictory relevant knowledge shall be exposed as knowledge gaps rather than silently resolved by representation order or wall-clock recency.

## REQ-NEP-011 — Candidate completeness is not path completeness

A source may state that its candidate enumeration is complete for the represented pair/time.

Such completeness means only that the source claims to have enumerated its own relevant candidate set. It shall not mean:

- candidates form a route;
- every candidate is a true positive;
- traversal order is known;
- traffic definitely traverses every candidate;
- absence of a candidate proves no forwarding/no enforcement.

## REQ-NEP-012 — Candidate output is independent from policy state

Network relevance and attachment location shall be independent from:

- Access Rule authorization/state;
- Technical Access Evidence action/configured content;
- desired-vs-configured reconciliation;
- vendor rendering/execution.

NEP shall not create or mutate Access Rules, TAE evidence or reconciliation state.

## REQ-NEP-013 — Proven path is optional stronger knowledge

The existing I19 `ForwardingPath` / ordered `TraversalPoint` capability may remain available for sources that can truthfully prove it.

MVP consumers shall not require it and NEP shall never infer a path from an unordered candidate set.

If a source claims proven path semantics but required forwarding dimensions are unavailable or unsupported, that stronger result shall fail closed rather than guess.

## REQ-NEP-014 — Do not convert candidate relevance into route assertions

The following invariants are mandatory:

```text
candidate != proven traversal
candidate set != route
candidate representation order != traversal order
```

UI/API wording shall preserve this distinction.

## REQ-NEP-015 — NEP does not perform reconciliation or configuration generation

NEP shall not:

- decide whether configured policy satisfies desired policy;
- produce Add/Remove/Replace/No-op;
- render vendor configuration;
- execute provider/device changes.

Those capabilities consume NEP output downstream.

## Acceptance examples

1. A pair returns three unordered device candidates; no route order is asserted.
2. One candidate returns an ingress interface, egress interface and three policy attachments: ingress, global and egress.
3. Another vendor candidate returns only one global policy attachment and no interface-bound policy.
4. A candidate with known device relevance but unknown interfaces returns the device plus explicit knowledge gaps, not fabricated interface values.
5. A candidate with zero relevant policy attachments remains in the result.
6. A downstream consumer can use `providerDeviceRef + policyRef/policyName` to query matching Technical Access Evidence without NEP returning ACL entries.
7. An unordered candidate set cannot be promoted to a proven forwarding path.
