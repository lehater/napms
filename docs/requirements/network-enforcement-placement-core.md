# Network Enforcement Placement Core Requirements — I19 + I26 extension

Status: `accepted through I26 Network Context semantic re-entry`.

Date: 2026-09-10.

## Purpose

Specify observable behavior for Network Enforcement Placement (NEP), preserving the original I19 proven-path capability while adding the weaker candidate-set Network Context contract required by Checker.

## REQ-NEP-001 — Select placement at explicit logical time

Given one exact source/destination IP pair and an offset-aware `asOf`, NAPMS may derive an Enforcement Selection from NEP-owned forwarding/path, Logical Firewall correspondence and Enforcement Attachment knowledge when a source can prove the stronger I19 path contract.

It shall not infer `asOf` from wall-clock “now” or persistence recording order.

## REQ-NEP-002 — Keep Logical Firewall identity independent

NAPMS shall preserve Logical Firewall identity independently from provider/device realization, Resource identity and Enforcement Attachment identity.

Provider replacement shall not automatically create a different Logical Firewall.

## REQ-NEP-003 — Require complete forwarding knowledge for proven-path claims

A successful complete I19 path-based selection shall require source knowledge that is complete for the exact source/destination pair under the represented forwarding model.

Missing path knowledge, an unrepresented forwarding discriminator, or unsupported multipath semantics shall produce `Unknown`, not a guessed path.

This requirement applies only to the stronger proven-path capability. It shall not prevent a weaker Network Context source from returning unordered relevant candidates under REQ-NEP-011.

## REQ-NEP-004 — Distinguish no path from no enforcement

When using the stronger path contract, NAPMS shall distinguish:
- `NoForwardingPath`: a source positively establishes that no forwarding path exists for an explicit effective validity interval and attributable provenance;
- `NoEnforcement`: a complete path exists and complete attachment/correspondence knowledge proves no enforcement attachment applies.

Absence of evidence shall not produce either state.

An empty or incomplete Network Context candidate set shall not be promoted to either conclusion.

## REQ-NEP-005 — Validate attachment through correspondence

A path-selected Enforcement Attachment shall be effective at `asOf`, shall reference an effective Logical Firewall, and shall have an effective Logical Firewall Correspondence to the same provider realization traversed at the exact Path Attachment.

A relevant attachment with missing/uncertain correspondence shall fail closed as `Unknown` for claims that require proven placement.

## REQ-NEP-006 — Preserve multiple enforcement points when path is proven

A complete proven path may contain more than one unambiguous enforcement point. NAPMS shall return each placement occurrence in path order with Logical Firewall, attachment, provider/path reference and provenance.

It shall not collapse distinct traversal positions into one firewall name.

This ordering is not inherited by the candidate-set Network Context contract.

## REQ-NEP-007 — Do not choose an ambiguity winner

If one traversed normalized provider/path-attachment point maps to more than one distinct effective Logical Firewall placement, NAPMS shall return `Ambiguous`, preserve all competing placements, and select no winner.

Equivalent duplicate provenance for the same placement shall not create ambiguity.

Candidate-set consumers shall likewise preserve competing candidates rather than selecting an arbitrary winner.

## REQ-NEP-008 — Preserve temporal history and provenance

Forwarding/path facts, Network Context candidate facts, Logical Firewall correspondences and Enforcement Attachments shall preserve attributable source/provenance and explicit effective time where owned by their source contract.

Corrections/supersession shall not erase historical explainability.

## REQ-NEP-009 — Keep placement/context independent from policy state

Network relevance and placement shall be independent from:
- Access Rule authorization/state;
- Technical Access Evidence action/configured content;
- desired-vs-configured reconciliation;
- vendor rendering/execution.

NEP shall not create or mutate Access Rules, Connectivity Decisions, TAE evidence or APR reconciliation state.

## REQ-NEP-010 — Forwarding limitations are fail-closed

The first executable Traffic Relation uses exact source and destination IP addresses.

If a source claims a proven path and the selected environment requires VRF/routing-instance, protocol/port, policy-routing, service-chain, ECMP or another unrepresented dimension to determine that path truthfully, the adapter shall report an explicit knowledge gap and the proven-path selection shall be `Unknown` until the model is extended.

A weaker source may still report unordered relevant candidates if its own source contract supports that claim.

## REQ-NEP-011 — Network Context may expose an unordered candidate set

NAPMS shall support a Network Context read contract that returns zero or more source-supported relevant network/enforcement candidates for an exact source/destination pair and explicit `asOf` without asserting a forwarding path.

Candidate-set semantics:
- candidate membership means only that the source considers the provider realization/enforcement identity relevant to the queried traffic;
- candidates have no semantic sequence;
- a candidate is not proof that traffic traverses that device;
- the set may be incomplete;
- the set may contain false positives;
- source-supported relevance/quality may be exposed as opaque source meaning, but NAPMS shall not manufacture a probability or confidence score;
- candidate provenance and knowledge gaps shall remain attributable.

## REQ-NEP-012 — Candidate completeness is not path completeness

`completeForPair` on a Network Context candidate result, when supplied, means only that the contributing source claims to have enumerated its relevant candidate set for that pair/time.

It shall not mean:
- that the candidates form a route;
- that every candidate is a true positive;
- that traversal order is known;
- that absence of a candidate proves no forwarding or no enforcement.

## REQ-NEP-013 — Proven path remains an optional stronger capability

The I19 `ForwardingPath` / ordered `TraversalPoint` / path-based `EnforcementSelection` model remains valid for sources that can truthfully prove it.

Consumers whose requirement needs only relevant devices, including Checker, shall depend on the weaker unordered Network Context contract and shall not require or expose path ordering merely because a stronger source happens to exist.
