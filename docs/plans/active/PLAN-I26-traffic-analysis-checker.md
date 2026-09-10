# PLAN-I26 — Traffic Analysis Checker

Status: `active / final gate`.

Date: 2026-09-10.

## Goal

Deliver the first complete Checker/Traffic Analysis slice for the supported local target, starting from a technical traffic tuple and composing owner-preserving domain, policy, Network Context, evidence and resource-responsibility information without introducing a new source of business truth.

## Inputs

Canonical requirement owner:
- `docs/requirements/traffic-analysis-checker.md`

Durable ordered roadmap:
- `docs/engineering/traffic-analysis-checker-roadmap.md`

Related semantic owners:
- `docs/requirements/network-enforcement-placement-core.md`
- `docs/domain/network-enforcement-placement/network-context.md`
- `docs/domain/resource-role-model.md`
- `docs/architecture/network-context-candidate-boundary.md`

## Exit criteria

I26 is complete when:
- Checker accepts source/destination/protocol/port/as-of and renders the complete information architecture;
- reverse technical-to-domain resolution preserves resolved, ambiguous, historical and unknown states;
- policy composition reuses existing domain/read owners rather than creating Checker-owned truth;
- Network Context returns unordered relevant enforcement/device candidates and never fabricates path/order;
- configured rules come only from stored Technical Access Evidence snapshots with capture/record/provenance information;
- technical predicate matching supports exact, containment and overlap semantics in backend code;
- Resource Responsibility/contact information remains separate from Authority Management;
- the supported local demo exercises multiple candidates, missing evidence and deterministic responsibility data;
- core, harness, knowledge, web, PostgreSQL persistence and Docker local runtime gates are green;
- canonical current-state/roadmap documentation is updated and the active plan is removed before merge.

## Blockers

No product/domain blocker is currently known. Remaining blockers are only failures discovered by repository gates.

## WP0 — Network Context semantic re-entry

- Reconcile the stronger proven `ForwardingPath` capability with the baseline unordered candidate-set Network Context contract.
- Preserve proven-path semantics only where a source can actually prove traversal/order.
- Define candidate provenance, source relevance, completeness and knowledge-gap semantics without fabricated probability.

Exit: complete. Checker can consume Network Context without claiming a route/path that the source cannot prove.

## WP1 — Checker Web fixture slice

- Add dedicated Checker route/workspace.
- Implement source, destination, protocol, port/range and as-of controls.
- Implement Overview, Network Context, Policy, Ownership and Evidence tabs.
- Use typed deterministic fixtures only during UI-first construction.

Exit: complete; the product read path has since been switched from fixtures to the real API.

## WP2 — Traffic Analysis application contract

- Define consuming-module ports and owner-preserving `TrafficAnalysisQuery` / `TrafficAnalysisResult`.
- Define authenticated HTTP transport DTO.
- Keep Checker persistence-free.

Exit: complete.

## WP3 — Domain resolution and policy composition

- Integrate Resource Catalogue endpoint/address history.
- Integrate ACC semantic connectivity context where resolvable.
- Reuse scoped connectivity composition for Requirement, Decision, Access Rule and Effective Policy summaries.
- Preserve unknown/ambiguous/historical states and multiple matches.

Exit: complete for the supported local target.

## WP4 — Network candidate integration

- Consume the corrected Network Context candidate-set contract.
- Return candidates without fabricated ordering.
- Expose source relevance, provenance and knowledge gaps.

Exit: complete with deterministic local Network Context adapter.

## WP5 — Evidence-backed technical rules

- Query stored Technical Access Evidence by candidate and requested `asOf`.
- Select the latest applicable snapshot; never perform synchronous live firewall/device reads.
- Expose capture/record/source/provenance information.
- Return matching/overlapping technical entries per candidate.

Exit: complete for stored Configured evidence snapshots.

## WP6 — Traffic predicate matching

- Implement backend source/destination/protocol/port set matching.
- Cover exact, containment, overlap and no-match semantics.
- Add focused boundary tests.

Exit: complete.

## WP7 — Resource responsibility/contact seam

- Add minimum Resource Responsibility capability owned by Resource Catalogue.
- Allow person/team references and service owner, technical owner, operations/support and business owner roles.
- Keep responsibility/contact separate from Authority Management action authority.

Exit: complete with temporal domain model/read contract and deterministic local adapter.

## WP8 — Integration and acceptance

Prove:
- fully resolved local traffic;
- ambiguous/unknown resolution behavior;
- several relevant Network Context candidates;
- evidence timestamps and missing evidence;
- broader/overlapping technical rule matching;
- ownership/contact discovery;
- no live device query path.

Current state: implementation and focused tests are present. Hosted repository gates are running; any remaining failures must be fixed before absorption.

## WP9 — Optional presentation refinement

Presentation refinement is deferred unless a gate or acceptance review exposes a concrete usability defect. No separate role-specific truth/API is introduced.

## Next

Complete all hosted repository gates. Then absorb I26 into canonical `current-state` / architecture / roadmap truth, remove this completed plan from `docs/plans/active`, set the active capsule to `Current: none`, refresh PR metadata, and squash-merge into `main`.
