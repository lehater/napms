# PLAN-014 — I14 Requirement-to-Policy Alignment

Status: `active`

## Goal

Implement the first explainable, authority-safe composition that compares authoritative Connectivity Requirements with authoritative effective Access Policy without making either bounded context own the other.

Primary product question:

```text
for one connectivity need at an explicit asOf:
    is equivalent semantic connectivity currently covered by authorized/effective policy?
```

Guardrails:

```text
Required != Authorized
Requirement-to-Policy Alignment != Access Policy
Requirement-to-Policy Alignment != Connectivity Decision
Requirement-to-Policy Alignment != configured/observed access
```

I14 must not invent approval workflow, persist a peer Alignment aggregate, or turn absence/hidden policy into a false `Uncovered` conclusion.

## Current stage

**WP1 — Semantic/authority closure.**

I13 is complete and absorbed. I14 starts from accepted Connectivity Requirement and Access Policy semantics. Working packet: `docs/plans/active/I14-WP1-alignment-decision-packet.md`.

## Inputs

Canonical:
- `docs/domain/connectivity-requirements/tactical-model.md`;
- `docs/domain/access-policy/tactical-model.md`;
- `docs/domain/capabilities.md`;
- `docs/domain/semantic-ownership.md`;
- `docs/requirements/connectivity-requirements-core.md`;
- `docs/requirements/wave1-semantic-contracts.md`;
- `docs/architecture/connectivity-requirements-boundary.md`;
- `docs/architecture/wave1-domain-message-flows.md`;
- `docs/engineering/post-wave1-product-completion-roadmap.md`;
- `docs/process/decision-protocol.md`;
- `docs/process/domain-change-protocol.md`.

Accepted facts:
- Alignment is a non-peer composition over Connectivity Requirements + Access Policy;
- Connectivity Requirement exact interaction is Source Deployment + Destination Deployment + immutable DCS revision;
- Access Rule semantic identity is the same exact triple;
- Requirement applicability is `Ongoing | AbsoluteWindow`;
- Access Rule contributes effective desired policy only when Active and inside its EffectiveWindow;
- Requirement and Rule governance scopes are stable, non-identity values and are not accepted as necessarily equal;
- `Required != Authorized`;
- I14 does not own Connectivity Decision internals;
- configured/observed satisfaction belongs to later Technical Access Evidence / Access Policy Realization work.

## WP1 decision questions

Resolve before executable alignment code:

1. **Alignment subject and time**
   - Is matching exact equality of RequiredSemanticInteraction to RuleSemanticIdentity?
   - Does one comparison use one explicit offset-aware `asOf` for both Requirement applicability and Rule effective-state evaluation?
   - How should Retired or not-currently-applicable Requirements appear: excluded from the current view, or explicit `NotApplicable`?

2. **Authority boundary**
   - What authority must be present before Alignment may expose `Covered`, `Uncovered`, or Rule provenance?
   - Requirement read authority and policy read authority are independent.
   - RequirementGovernanceScope and RuleGovernanceScope may differ.
   - No result may classify hidden/ambiguous policy as `Uncovered`.

3. **Outcome vocabulary**
   - Minimum evidence-supported candidates are `Covered`, `Uncovered`, and an explicit fail-closed/unknown result.
   - Strategic capability language also mentions `Denied`, but current Access Policy stores only authorized Rules; a durable NotAllowed decision is not current policy truth.
   - Decide whether `Denied` remains deferred to I15/I16.

4. **Orphan policy**
   - Roadmap expects policy-without-current-requirement visibility where useful.
   - Decide whether I14 first slice includes a policy-centric orphan view or closes only the Requirement-centric owner journey first.

5. **Persistence**
   - Default hypothesis: Alignment is a pure read composition and has no authoritative persistence.
   - Introduce persisted Alignment state only if accepted domain evidence requires independent identity/lifecycle/audit.

## Work packages

### WP1 — Semantic/authority closure

Status: `active`.

Method:
- synthesize canonical CR/AP semantics;
- classify known vs unknown;
- resolve the minimum owner choices above;
- update capabilities/requirements/architecture before code where needed.

Exit:
an explicit, testable alignment truth table exists, including authority and failure semantics.

### WP2 — Requirements and acceptance examples

Status: `planned`.

Add executable examples for:
- current applicable Requirement + effective matching Rule;
- current applicable Requirement + no effective matching Rule;
- inactive Rule;
- Rule outside EffectiveWindow;
- Requirement outside applicability;
- differing governance scopes;
- denied/unknown Requirement read;
- denied/unknown policy read;
- exact semantic mismatch;
- no false `Uncovered` on hidden/ambiguous policy;
- no configured/observed conclusion.

### WP3 — Architecture and application ports

Status: `planned`.

Define a non-peer alignment application composition:
- CR read input remains CR-owned;
- AP effective-policy/matching input remains AP-owned;
- consumer-owned translation DTO/value types at the composition boundary;
- no CR -> AP or AP -> CR domain dependency;
- no peer Alignment aggregate unless WP1 changes accepted disposition.

### WP4 — Executable core

Status: `planned`.

Implement the smallest framework-free alignment use case/read model and exhaustive authority/temporal tests.

Core/architecture gate must pass before HTTP/Web changes.

### WP5 — HTTP + Web owner view

Status: `planned`.

Extend `My Connectivity Needs` with current policy-coverage presentation using backend-derived alignment only.

UI must:
- distinguish `Covered`, `Uncovered`, and fail-closed/unknown;
- never display hidden Rule data;
- keep `Allowed/Denied` decision semantics separate unless WP1 explicitly admits evidence.

### WP6 — PostgreSQL/Docker E2E

Status: `planned`.

Prove through real composition/public runtime:
- declared need + effective matching Rule -> Covered;
- need without effective visible Rule -> accepted uncovered/unknown result;
- mutation of Rule state/window changes Alignment without mutating Requirement;
- Requirement mutation/retirement changes current-view participation;
- no new persisted Alignment truth.

### WP7 — Final review/gates/canonical absorption

Status: `planned`.

Run:
- core;
- PostgreSQL;
- Web;
- Docker;
- harness;
- knowledge;
- architecture/security review.

Close all P0/P1, absorb I14 truth, mark roadmap I14 done, promote I15, remove active plan, squash merge.

## Exit criteria

I14 is complete only when:
- exact Requirement↔Policy matching semantics are accepted;
- temporal semantics are explicit and use no hidden wall-clock;
- authority cannot leak Rule/policy existence or turn hidden policy into false absence;
- no Connectivity Decision workflow/reason is invented;
- no configured/observed conclusion is manufactured;
- owner-facing Alignment is explainable with exact evidence/provenance allowed by authority;
- no peer Alignment persistence is added without accepted identity/lifecycle need;
- final gates pass with no open P0/P1.

## Blockers

Current semantic blocker:
- authority semantics for policy coverage when RequirementGovernanceScope and matching RuleGovernanceScope differ are not yet accepted.

Secondary decision:
- whether non-current Requirements are omitted or shown as explicit `NotApplicable`.

## Next

Resolve WP1 authority/outcome/time semantics, record them canonically, then write the acceptance truth table before implementation.
