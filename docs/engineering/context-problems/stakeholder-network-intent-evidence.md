# Stakeholder Network Intent — Evidence Register

Status: `non-authoritative stakeholder evidence`.

Date: 2026-09-13.

## Purpose

Preserve consequential stakeholder observations and candidate discovery entities that cut across the current network-policy problem space without prematurely assigning them to a Bounded Context, requirement set, aggregate, persistence model, or Context Map.

This file is source/discovery evidence, not canonical product or domain truth. Acceptance belongs to the owning S0/S1/S2 stage.

## Observed / normalized evidence

The following observations were harvested from project stakeholder discussions available on 2026-09-13.

- Working directly with raw firewall access lists is a forced low-level task rather than the desired primary user abstraction.
- A more useful user abstraction is the network interaction required between described resources and application components deployed on them.
- Application/component interaction may itself be below a future higher abstraction. Organizational processes are a plausible higher-level source of need: a process may require software, software may require component interactions, and those interactions may require network access.
- The value sought is causal/business traceability in both directions, not merely a syntactic mapping:
  - from an organizational need/process toward software, component interaction, required network access, traffic and enforcement;
  - from observed traffic or enforcement back toward the interaction/application/process that justifies it.
- Business/process attributes such as criticality, importance, periodicity and lifecycle are examples of information that may eventually help explain the importance of dependent network access. The exact attributes and propagation rules are not yet accepted.
- A useful reverse-analysis outcome is to inspect traffic and understand approximately what organizational purpose/process it serves, who needs it, how important it is, and what impact blocking it may have.
- Access-list/rule cleanup based only on configuration syntax or structural redundancy cannot answer whether semantically valid access is still needed by the organization.
- If the business/process need disappears, associated software/interactions/access may cease to be justified even when the existing firewall configuration remains technically valid.
- Business-driven access rationalization is therefore materially different from technical policy optimization that preserves effective access while improving its representation.
- Business relevance may be useful for prioritizing cleanup when access-list volume must be reduced, including identifying access associated with retired or low-value needs. Exact deletion/prioritization policy remains unresolved.
- A desired end-to-end capability is to explain why network access exists and connect technical enforcement back to the need that caused it.

## Related previously observed realization evidence

The following cross-cutting observations are preserved here only as references for synthesis; APR-specific detail remains owned by `access-policy-realization.md`.

- Users may seek an access-list audit, a source-destination/service accessibility check, a semantic required-versus-realized difference, or a proposed correction.
- Semantic difference can be independently useful without remediation, including reporting or handing recommendations to another person.
- Semantic correctness of effective access is distinct from structural/configuration optimality.
- Raw rule comparison is insufficient where ordering, deny behavior, groups/objects, defaults or similar constructs affect effective behavior.
- For source-destination analysis the real network path is not assumed known; candidate relevant enforcement devices/policies are inferred from available evidence.
- Device evidence acquisition has operational characteristics that may vary per device, including polling frequency and timeout; device active/inactive state is administratively controlled.

## Candidate journeys

These are discovery candidates only. They are not accepted journeys or lifecycle stages.

- Describe an application, its resources/components and the network interactions those components require.
- Start from a required source-destination/service interaction, identify candidate enforcement locations, and inspect its realization.
- Audit a firewall/access-list realization and obtain missing/excess effective access.
- Obtain a semantic difference and stop there for analysis/reporting.
- Obtain a semantic difference, prepare a recommended correction, and hand it to another participant.
- Design, verify, render and operationally apply a correction after a realization discrepancy is found.
- Start from observed traffic/access and trace it upward to application/component interaction and organizational purpose to assess importance and blocking impact.
- Start from a retired or changed organizational need and trace downward to network access/enforcement that may no longer be justified.

## Candidate use cases

These are candidate discovery entities, not accepted requirements.

- Describe application communication.
- Describe component-to-component network interaction.
- Associate organizational need/process with supporting software/application.
- Trace organizational need to required network access.
- Trace observed traffic/access to application and organizational purpose.
- Assess business impact/importance of network access.
- Identify access with no current business justification.
- Prioritize access cleanup using business relevance.
- Determine candidate enforcement devices/locations for a required interaction.
- Determine relevant policy attachments/locators on a candidate device.
- Acquire current device configuration evidence.
- Assess policy realization.
- Obtain semantic missing/excess delta.
- Check source-destination/service accessibility.
- Audit access-list realization.
- Prepare a remediation recommendation/change design.
- Verify a proposed correction semantically before execution.
- Render a verified change for a provider/device.
- Apply a configuration change operationally.
- Prepare a realization/audit report.

## Candidate capability clues

These clues may support later synthesis and Strategic DDD analysis. A capability is not automatically a Bounded Context.

- Organizational Need / Process Description.
- Application and Component Modelling.
- Application Interaction Modelling.
- Required Network Access Definition.
- Business-to-Network Traceability / Attribution.
- Business Impact Analysis for Network Access.
- Enforcement Candidate Determination.
- Policy Scope / Attachment Determination.
- Technical Configuration Evidence Acquisition.
- Effective Policy Interpretation / Normalization.
- Semantic Policy Comparison.
- Policy Change Design.
- Semantic Change Verification.
- Provider Configuration Rendering.
- Network Configuration Execution.
- Realization / Attribution Reporting.

## Candidate semantic results / seams

These are useful concepts for later analysis, not accepted contracts or Context Map edges.

- organizational need/process description;
- application/component description;
- component network interaction;
- required technical access;
- candidate enforcement relevance;
- enforcement/policy locator;
- observed/configured device evidence;
- configured effective policy;
- required effective policy;
- realization assessment;
- semantic missing/excess delta;
- candidate policy change design;
- semantically verified proposed change;
- provider-specific rendered change;
- operational execution result;
- business attribution / impact explanation for observed traffic or access.

A recurring discovery clue is that independently useful semantic results may be consumed by several journeys. This is boundary evidence only; it must not be converted directly into Bounded Contexts.

## Requirement candidates

The following are S1 candidates requiring explicit Requirements-stage acceptance before becoming canonical requirements.

- Users should be able to work with network interactions at a higher abstraction than raw ACL/rule structures where the product has enough semantic information to do so.
- The system should be able to preserve/expose the justification chain between organizational/application need and required network access where such source information exists.
- The system should support reverse explanation from observed traffic/access toward the application/organizational need that justifies it, with uncertainty represented rather than invented attribution.
- Business relevance/criticality should be usable in impact and cleanup decisions where authoritative business context exists; exact scoring/propagation behavior is unresolved.
- Technical policy optimization that preserves required/effective semantics must remain distinguishable from business-driven rationalization that intentionally changes required access because the underlying need changed.
- Realization/audit results should be usable independently of remediation when the user's goal is analysis, accessibility checking or reporting.

## Important non-inferences

Do not infer from this evidence that:

- `Organizational Process`, `Application`, `Component`, `Interaction`, `Access List` or any other term is already an accepted entity/aggregate;
- process → software → interaction → access is the final mandatory hierarchy;
- any candidate capability is a Bounded Context;
- any Bounded Context or Context Map edge has been accepted by this harvest;
- access-list scope is an internal persistence/computation boundary merely because it is a natural current user-facing scope;
- process criticality automatically propagates to traffic, rules or ACLs by `max`, inheritance or another algorithm;
- traffic attribution can always be exact;
- a recommendation handoff implies a formal approval workflow;
- technical cleanup and business-driven removal share one optimization objective.

## Unknowns / evidence gaps

Later conversations or domain analysis should clarify, when relevant:

- who is authoritative for organizational process/need descriptions and their lifecycle;
- whether process/application/component relationships are entered explicitly, imported from authoritative organizational systems, inferred from observations, or combined;
- how application intent is translated into technical required access and who owns/approves that translation;
- whether component/application interaction is the desired stable user abstraction or only an intermediate abstraction;
- how ambiguity is represented when observed traffic can map to several applications/processes;
- which business attributes materially affect access impact/cleanup decisions;
- whether a remediation/change plan has an independent durable/editable/approvable lifecycle;
- exact ownership of provider-specific policy interpretation versus raw device acquisition;
- authoritative freshness/completeness semantics for observed device state.

## Routing for future work

- Problem/goal evidence belongs to S0 when a concrete product problem is selected.
- Observable behavior candidates belong to S1 only after explicit acceptance.
- Entity/language/authority/invariant/lifecycle/boundary interpretations belong to S2.
- APR-specific realization evidence remains in `docs/engineering/context-problems/access-policy-realization.md`.
- Strategic DDD synthesis may consume this file later, but this harvest intentionally does not build or change the Context Map.
