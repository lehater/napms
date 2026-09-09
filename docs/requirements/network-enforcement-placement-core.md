# Network Enforcement Placement Core Requirements — I19

Status: `accepted I19 WP-0 requirements baseline`.

Date: 2026-09-09.

## Purpose

Specify observable behavior for the first Network Enforcement Placement slice.

## REQ-NEP-001 — Select placement at explicit logical time

Given one exact source/destination IP pair and an offset-aware `asOf`, NAPMS shall derive an Enforcement Selection from NEP-owned forwarding/path, Logical Firewall correspondence and Enforcement Attachment knowledge.

It shall not infer `asOf` from wall-clock “now” or persistence recording order.

## REQ-NEP-002 — Keep Logical Firewall identity independent

NAPMS shall preserve Logical Firewall identity independently from provider/device realization, Resource identity and Enforcement Attachment identity.

Provider replacement shall not automatically create a different Logical Firewall.

## REQ-NEP-003 — Require complete forwarding knowledge

A successful complete selection shall require source knowledge that is complete for the exact source/destination pair under the first-slice forwarding model.

Missing path knowledge, an unrepresented forwarding discriminator, or unsupported multipath semantics shall produce `Unknown`, not a guessed path.

## REQ-NEP-004 — Distinguish no path from no enforcement

NAPMS shall distinguish:
- `NoForwardingPath`: a source positively establishes that no forwarding path exists for an explicit effective validity interval and attributable provenance;
- `NoEnforcement`: a complete path exists and complete attachment/correspondence knowledge proves no enforcement attachment applies.

Absence of evidence shall not produce either state.

## REQ-NEP-005 — Validate attachment through correspondence

A selected Enforcement Attachment shall be effective at `asOf`, shall reference an effective Logical Firewall, and shall have an effective Logical Firewall Correspondence to the same provider realization traversed at the exact Path Attachment.

A relevant attachment with missing/uncertain correspondence shall fail closed as `Unknown`.

## REQ-NEP-006 — Preserve multiple enforcement points

A complete path may contain more than one unambiguous enforcement point. NAPMS shall return each placement occurrence in path order with Logical Firewall, attachment, provider/path reference and provenance.

It shall not collapse distinct traversal positions into one firewall name.

## REQ-NEP-007 — Do not choose an ambiguity winner

If one traversed normalized provider/path-attachment point maps to more than one distinct effective Logical Firewall placement, NAPMS shall return `Ambiguous`, preserve all competing placements, and select no winner.

Equivalent duplicate provenance for the same placement shall not create ambiguity.

## REQ-NEP-008 — Preserve temporal history and provenance

Forwarding/path facts, Logical Firewall correspondences and Enforcement Attachments shall preserve attributable source/provenance and explicit effective validity.

Corrections/supersession shall not erase historical explainability.

## REQ-NEP-009 — Keep placement independent from policy state

Placement relevance shall be independent from:
- Access Rule authorization/state;
- Technical Access Evidence action/configured content;
- desired-vs-configured reconciliation;
- vendor rendering/execution.

I19 shall not create or mutate Access Rules, Connectivity Decisions, TAE evidence or APR reconciliation state.

## REQ-NEP-010 — First-slice forwarding limitation is fail-closed

The first executable Traffic Relation uses exact source and destination IP addresses.

If the selected environment requires VRF/routing-instance, protocol/port, policy-routing, service-chain, ECMP or another dimension to determine the path truthfully, the adapter shall report an explicit knowledge gap and the selection shall be `Unknown` until the NEP model is extended.
