# I28 — User Journey Validation Pilot

Status: `active`.

## Goal

Prove a repository-local workflow for validating one complete user journey from accepted user goal through the Web UI to a durable result, use it to close the first Application Catalogue authoring journey, and keep only the smallest reusable Harness support demonstrated by the pilot.

The pilot journey is J01: an authorized catalogue curator creates a new Application, describes its Components and Component Deployments, defines directed communication semantics, corrects ordinary authoring mistakes using accepted lifecycle/edit semantics, and can reopen the resulting model through the UI.

## Inputs

- accepted Catalogue Curation behavior and acceptance examples;
- accepted Web UI product requirements and `docs/ui/` guidance;
- current Applications catalogue Web implementation and its backend boundary;
- repository Harness rules and the admitted `user-journey-validation` Skill;
- pilot fixture kept intentionally small: one application with a few components/deployments and two directed communications.

## Non-goals

- no generic QA platform or multi-agent orchestration;
- no catalogue-wide exhaustive screen matrix before J01 proves value;
- no permanent duplicate journey documentation when accepted requirements or executable tests can own the result;
- no automated E2E suite before the pilot path is semantically and interactively stable.

## WP-1 — Harness admission and routing

Purpose: make end-to-end journey validation a first-class reusable agent workflow without changing the Harness architecture.

Deliverables:
- `.agents/skills/user-journey-validation/SKILL.md`;
- positive/confusable-negative routing coverage in `tests/evals/skill-routing-cases.json`;
- no new dispatcher, role state machine, runtime coordinator or validator unless demonstrated evidence requires one.

Local exit:
- the Skill boundary is distinct from `implement-slice`, `domain-model-change`, `resolve-decision` and `agent-harness-design`;
- `make harness-check` passes.

## WP-2 — J01 baseline and gap classification

Purpose: establish whether the current product lets the actor complete J01 through supported UI concepts rather than implementation knowledge.

Pilot fixture:

```text
Application: Order Management
  Component: Web UI
    Deployment: production
  Component: Orders API
    Deployment: production
  Component: Database
    Deployment: production

Communications:
  Web UI / production -> Orders API / production : tcp/443
  Orders API / production -> Database / production : tcp/5432
```

Validation boundary:
- discover and create the Application from the catalogue UI;
- add the structural children required by the fixture;
- define the two directed communication specifications;
- exercise accepted correction/lifecycle behavior needed for ordinary authoring mistakes;
- navigate away, reload/reopen and verify the durable model remains understandable;
- exercise material validation/retry/cancel or destructive-confirmation paths exposed by this journey;
- do not use direct API/database mutations as journey evidence.

For each failed step classify:
- accepted behavior missing/incorrect in Web implementation;
- Web UI requirement/guidance incomplete relative to accepted feature semantics;
- product/domain truth genuinely missing or conflicting;
- usability/presentation defect with semantics unchanged.

Local exit:
- J01 has an explicit PASS/FAIL verdict and reproducible P0-P3 findings;
- every P0/P1 finding has an owning next workflow and concrete expected accepted result.

## WP-3 — Close J01 P0/P1 gaps

Purpose: resolve only the blocking/important findings demonstrated by WP-2.

Rules:
- update highest affected canonical truth before implementation when requirements conflict;
- route semantic/lifecycle/authority changes through the existing domain/decision workflows;
- implement already accepted behavior through the scoped Web/backend workflow without broad refactors;
- rerun J01 after each coherent semantic increment.

Local exit:
- no P0/P1 J01 finding remains;
- J01 can be completed and corrected through the supported UI and its durable result can be reopened.

## WP-4 — Deterministic regression

Purpose: protect the stable high-value path after usability and semantics are confirmed.

Deliverables:
- add the minimum browser/E2E tooling justified by J01;
- automate the deterministic J01 happy path and high-value regression checks that do not pretend to measure subjective usability;
- keep test fixtures isolated and reproducible.

Local exit:
- the automated journey regression passes locally;
- manual/judgement evidence and automated evidence make distinct claims.

## WP-5 — Pilot review and absorption

Purpose: decide what should become the repeatable pattern for later journeys.

Review:
- whether `user-journey-validation` remained useful and distinct in real execution;
- whether any shared process belongs in `docs/process/` after demonstrated reuse;
- whether routing/eval coverage needs refinement;
- which J01 truths belong in accepted requirements and which evidence belongs only in executable tests/Git history.

Local exit:
- reusable Harness support contains no J01-specific product truth;
- accepted product/UI truth is synchronized;
- active execution state can be removed after integration.

## Exit criteria

- `make harness-check` passes with the journey-validation routing boundary;
- J01 passes end-to-end through the supported UI with no P0/P1 findings;
- accepted requirements and UI guidance do not conflict on behavior required by J01;
- deterministic high-value J01 behavior has executable regression evidence where justified;
- no generic orchestration or permanent audit-document layer was introduced without demonstrated need.

## Blockers

None known at plan creation. Runtime/browser execution constraints discovered during WP-2 must be recorded as evidence rather than silently replaced with code inspection.

## Next

Finish WP-1 validation, then execute WP-2 using `user-journey-validation`. Do not begin implementation fixes until the baseline findings identify their owning semantic/UI layer.
