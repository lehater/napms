# PLAN-I26 — Traffic Analysis Checker

Status: `active / planning baseline`.

Date: 2026-09-10.

## Goal

Deliver the first complete Checker/Traffic Analysis slice for the supported local target, starting with UI information architecture and then adding only the backend composition/domain seams required by accepted behavior.

Canonical requirement owner:
- `docs/requirements/traffic-analysis-checker.md`

Durable ordered roadmap:
- `docs/engineering/traffic-analysis-checker-roadmap.md`

## Current semantic blocker

The current I19 NEP model assumes a proven `ForwardingPath` with ordered traversal positions for successful placement. The accepted Checker requirement states that the available Network Context only provides a set of relevant network/enforcement candidates, may be incomplete, may contain false positives and does not establish a trustworthy sequence.

Per `docs/process/domain-change-protocol.md`, this conflict must be resolved at the highest affected canonical layer before Checker backend code depends on the old ordered-path guarantee.

## Execution stages

### WP0 — Network Context semantic re-entry

- Re-read current NEP requirements/domain/application contracts only as needed.
- Decide which proven-path semantics remain valid as an optional stronger capability and which baseline selection semantics must be generalized to candidate-set knowledge.
- Update requirements/domain/architecture truth before implementation.
- Define candidate relevance/quality, provenance, completeness/knowledge-gap and ambiguity contracts without inventing unsupported probability.
- Add/adjust knowledge tests for the corrected semantics.

Exit: Checker can consume Network Context terminology without claiming a route/path that the source cannot prove.

### WP1 — Checker Web fixture slice

- Apply `web/AGENTS.md` and nearest Web skill.
- Add dedicated Checker/Traffic Analysis route/workspace.
- Implement query controls: source, destination, protocol, port/range, as-of.
- Implement tabs: Overview, Network Context, Policy, Ownership, Evidence.
- Use typed deterministic fixtures.
- Cover accepted uncertainty and negative states from REQ-CHK-012.
- Run `make web-check` plus applicable harness/knowledge checks for touched docs/contracts.

Exit: the complete information architecture is inspectable locally without waiting for backend integration.

### WP2 — Traffic Analysis application contract

- Define consuming-module ports and owner-preserving `TrafficAnalysisQuery`/`TrafficAnalysisResult`.
- Define authenticated HTTP transport DTO.
- No independent Checker persistence.
- Core/architecture tests first.

Exit: stable composition seam exists for incremental owner integrations.

### WP3 — Domain resolution and policy composition

- Integrate Resource Catalogue endpoint/address history.
- Integrate ACC semantic connectivity context where resolvable.
- Integrate Requirement, Decision, Access Rule and Effective Policy reads.
- Preserve unknown/ambiguous/historical states and owner references.

Exit: Checker can explain what the queried traffic means administratively/policy-wise when domain resolution is available.

### WP4 — Network candidate integration

- Consume corrected Network Context candidate-set contract.
- Return relevant candidates without fabricated ordering.
- Expose source-supported relevance/quality, provenance, ambiguity and knowledge gaps.

Exit: Network Context tab is backed by owner data rather than fixtures.

### WP5 — Evidence-backed technical rules

- Query stored Technical Access Evidence by candidate and requested `asOf`.
- Select the latest applicable snapshot; never perform synchronous live firewall/device reads.
- Expose captured-at/source/provenance/completeness.
- Return matching/overlapping technical entries per candidate.
- Preserve original vendor representation only when already stored by evidence.

Exit: network engineers can see last-known imported device rules and exactly when that evidence was captured.

### WP6 — Traffic predicate matching

- Implement backend-owned source/destination/protocol/port set matching.
- Cover exact, containment, overlap, no-match and unknown/ambiguous states as supported by accepted contracts.
- Add focused unit/property-style boundary tests for CIDR/host and port/range cases.

Exit: UI does not perform independent technical rule matching.

### WP7 — Resource responsibility/contact seam

- Re-enter Resource Catalogue tactical/requirements ownership as needed.
- Add minimum Resource Responsibility / Contact Assignment capability with local deterministic stub/persistence appropriate to the current plan.
- Allow person or team reference.
- Support service owner, technical owner and operations/support contact at minimum.
- Keep responsibility/contact separate from Authority Management action authority.

Exit: Ownership tab can answer who owns/supports both resolved sides when data exists.

### WP8 — Integration and acceptance

Prove at least:
- fully resolved/in-sync traffic;
- ambiguous/unknown IP mapping;
- several relevant network candidates including weak/possible relevance;
- evidence snapshot timestamps and missing evidence;
- broader/overlapping technical rule match;
- configured evidence without matching authorization;
- missing ownership data;
- maintenance/contact-discovery journey from traffic tuple to affected service owners/support contacts.

Run the final relevant local gates. Keep PR draft while stages accumulate; mark ready only for the final gate.

### WP9 — Optional presentation refinement

After the full slice works, adjust default expansion/visibility for network, security/governance, application-owner and assurance perspectives without creating separate truth models or incompatible APIs.

## Non-goals

- Live firewall queries from Checker.
- Real Cisco/provider transport or lab validation.
- Automatic device remediation.
- A guaranteed network path/order from current Network Context.
- Enterprise identity/CMDB integration.
- Hard-coded role/job-title domain semantics.
- Automatic snapshot freshness trust decisions without a separate accepted policy.

## Validation policy

Use the smallest matching checks during each WP and final repository gates appropriate to all touched areas. Expected checks include:
- `make test`;
- `make harness-check`;
- `make knowledge-check`;
- `make web-check`;
- `make check` for the final integrated candidate.

Hosted Actions remain the final PR gate only.

## Current next action

Execute WP0: reconcile the I19 proven-path model with the accepted candidate-set Network Context behavior, then begin the UI fixture slice.
