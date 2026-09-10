# Traffic Analysis Checker Roadmap

Status: `selected next product increment after I25`.

Date: 2026-09-10.

## Purpose

Provide the ordered implementation path for the technical-entry-point analysis currently code-named **Checker**.

The accepted observable behavior is owned by `docs/requirements/traffic-analysis-checker.md`.

Checker is intentionally UI-first, with backend seams introduced only where current owner APIs/read models are insufficient.

## Ordered roadmap

### C0 — Semantic re-entry and contract correction

Resolve the discovered mismatch between the existing I19 ordered `ForwardingPath`/traversal-position contract and the newly accepted Checker requirement that the available Network Context is only a possibly incomplete candidate set with potential false positives.

Deliverables:
- classify what remains valid in NEP and what must be generalized/superseded;
- update the highest owning requirements/domain/architecture artifacts before code;
- preserve a stronger proven-path capability only if a source can actually prove it;
- define the candidate-set semantics needed by Checker: relevance/quality, provenance, ambiguity, completeness/knowledge gaps.

### C1 — Checker Web skeleton on deterministic fixtures

Create a dedicated Checker/Traffic Analysis workspace with:
- source/destination/protocol/port/as-of inputs;
- Overview;
- Network Context;
- Policy;
- Ownership;
- Evidence.

Use deterministic fixtures/stubs and cover realistic uncertainty/failure states before depending on a complete backend composition.

### C2 — Checker application/read contract

Define one owner-preserving application composition:
- `TrafficAnalysisQuery`;
- `TrafficAnalysisResult`;
- authenticated transport DTO/API.

Do not add a new bounded context or independent persistence for composed truth.

### C3 — Technical address to domain resolution

Compose Resource Catalogue and Application Communication Catalogue capabilities to resolve:

`IP -> Endpoint -> Resource -> Component/Application context`

Preserve ambiguity, unknown and historical states.

### C4 — Policy/governance composition

Compose available:
- Connectivity Requirement;
- Connectivity Decision;
- authoritative Access Rule;
- Effective Policy;
- provenance/explainability references.

Keep `Required`, `Allowed`, Rule state and technical evidence distinct.

### C5 — Network Context candidate integration

For the query tuple, return relevant network/enforcement candidates without inventing a path or order.

Expose source-supported relevance/quality, provenance, ambiguity and knowledge gaps.

### C6 — Per-candidate Technical Access Evidence correlation

For every relevant network candidate:
- select the latest applicable stored Technical Access Evidence snapshot for `asOf`;
- never perform a synchronous live device/firewall read;
- expose snapshot/capture time and provenance;
- find matching/overlapping normalized technical entries;
- expose original vendor representation when already retained by evidence;
- preserve completeness/unknown state rather than claiming live currentness.

### C7 — Shared traffic-predicate matching semantics

Implement backend-owned matching/coverage semantics for supported source/destination address sets, protocol and port predicates.

The result must distinguish enough of:
- exact;
- candidate covers query;
- query covers candidate;
- partial overlap;
- no match;
- unknown/ambiguous.

Web must render the backend result, not duplicate the algebra.

### C8 — Resource ownership/contact capability

Add the minimum owner-preserving seam required for operational contact discovery.

Expected model direction:
- Resource Responsibility / Contact Assignment;
- person or team party reference;
- service owner;
- technical owner;
- operations/support contact;
- temporal validity and provenance where applicable.

Keep resource responsibility separate from Authority Management action authority.

A deterministic local/in-memory stub is sufficient until a real authoritative catalogue/source is selected.

### C9 — Full Checker integration and acceptance

Integrate the tabs against the real composition API and prove at least the accepted first-slice scenarios from the requirements baseline.

Acceptance must include the operational maintenance use case:
- technical traffic tuple is entered;
- related service/resource context is resolved;
- relevant network candidates and their evidence-backed technical rules are shown;
- source/destination ownership/support contacts are available when known.

### C10 — Role-oriented presentation refinement

Only after the full projection exists, refine default presentation/visibility for common perspectives such as:
- network operations;
- security/governance;
- application/resource owner;
- assurance/audit.

Use one Checker composition and capability/visibility rules rather than hard-coded job-title domain models.

## Dependency sequence

```text
C0 semantic correction
  -> C1 UI fixtures
  -> C2 read contract
  -> C3 domain resolution
  -> C4 policy composition
  -> C5 network candidates
  -> C6 evidence-backed rules
  -> C7 predicate matching
  -> C8 ownership/contacts
  -> C9 integration/acceptance
  -> C10 presentation refinement
```

C1 may proceed in parallel with later backend research after C0 establishes safe terminology and fixture semantics.

## Priority summary

- P0/P1: correct Network Context versus proven-path semantics before Checker backend depends on NEP.
- P1: Checker application composition API/read model.
- P1: evidence snapshot lookup and per-candidate rule correlation.
- P1: shared traffic predicate matching.
- P1: operational resource ownership/contact capability.
- P2: role-oriented presentation refinements after full projection works.

## Explicit implementation constraints

- Local-first remains the selected target.
- Deterministic stubs are preferred over speculative provider/enterprise integrations.
- No real lab or live device transport is required.
- Checker is evidence-driven, not device-driven.
- Technical Access Evidence does not become authorization truth.
- Network Context uncertainty remains visible to the user.
