# PLAN-013 — I13 Connectivity Requirements Core

Status: `active`

## Goal

Promote the already-accepted **Connectivity Requirements** strategic context into a minimal Tactical DDD + executable core without conflating need with permission.

Target first vertical slice:

```text
authorized responsible actor
    -> declare a semantic connectivity need
    -> persist authoritative Connectivity Requirement
    -> list/read that requirement
    -> change/retire it only under accepted lifecycle rules

AND

Connectivity Requirement existence
    != ConnectivityDecision(Allowed)
    != Access Rule existence
    != configured access
```

I13 deliberately stops before Requirement-to-Policy Alignment and before Connectivity Decision internals.

## Current stage

**WP7 — Web UI: My Connectivity Needs.**

Evidence synthesis is complete. Working packet:
`docs/plans/active/I13-WP1-connectivity-requirements-decision-packet.md`.

WP1 owner choices are accepted and canonicalized. Infrastructure remains deferred until WP2/WP3 behavior and ports are explicit.

## Inputs

Canonical:
- `docs/domain/strategic-model.md`;
- `docs/domain/capabilities.md`;
- `docs/domain/resource-role-model.md`;
- `docs/domain/semantic-ownership.md`;
- `docs/domain/ubiquitous-language.md`;
- `docs/requirements/wave1-product-requirements.md`;
- `docs/requirements/wave1-deferrals.md`;
- `docs/engineering/current-state.md`;
- `docs/engineering/post-wave1-product-completion-roadmap.md`;
- `docs/process/domain-change-protocol.md`;
- `docs/process/decision-protocol.md`.

Accepted strategic facts:
- Connectivity Requirements owns the question “what semantic connectivity is needed?”;
- system/resource owners may declare need for their owned/responsible scope;
- declaring need does not authorize access;
- another user/decision mechanism with corresponding policy/security authority determines permission;
- `Required != Authorized`;
- `Required != Configured/Observed`;
- `ConnectivityRequirement != AccessRequest/ticket`;
- current identity shape `Dependent × RequiredSemanticInteraction × Applicability` is only a strategic hypothesis, not an accepted Tactical natural key.

## Decision questions for WP1

Resolve before coding the aggregate:

1. What is the exact authoritative identity of one Connectivity Requirement?
2. What is `Dependent` in the first executable slice: Resource, Component Deployment, another stable subject, or an explicit supported union/reference?
3. Is `RequiredSemanticInteraction` the same exact Deployment + Deployment + immutable DCS subject used by an Access Rule Proposal, or can a requirement be intentionally more abstract?
4. What is the minimum `Applicability` model:
   - always/current;
   - absolute time window;
   - other condition?
5. What lifecycle is real domain meaning:
   - declare;
   - amend;
   - retire/withdraw;
   - supersede;
   - any other state only if evidence requires it?
6. Which changes preserve requirement identity and which create a new requirement?
7. What justification/provenance is mandatory?
8. Which Authority Management actions are required for:
   - declare;
   - read;
   - amend;
   - retire?
9. How is responsibility/ownership used only as input to Authority Management rather than as hidden authorization?
10. What concurrency/idempotency behavior is required for repeated declaration/amendment?

Unknown answers stay explicitly unknown; do not choose a database key/API shape to answer them implicitly.

## Work packages

### WP1 — Tactical DDD closure

Status: `done`.

Method:
- synthesize accepted strategic evidence;
- create focused decision packets for the questions above;
- obtain owner decisions only where canonical evidence is insufficient;
- update Ubiquitous Language / Connectivity Requirements Tactical model;
- update semantic ownership/context relationship only if evidence actually changes Strategic DDD.

Exit:
accepted aggregate/lifecycle/value-object/command/query/invariant semantics sufficient to write executable examples.

### WP2 — Requirements and acceptance examples

Status: `done`.

Add post-Wave-1 requirements/examples for:
- authorized declaration;
- unauthorized declaration;
- valid/invalid semantic interaction;
- idempotent/repeated operation;
- amend vs new identity;
- retirement;
- audit/provenance;
- explicit proof that Requirement creation does not materialize/authorize Access Rule.

Exit:
behavior matrix is testable without persistence/HTTP choices.

### WP3 — Architecture and ports

Status: `done`.

Define:
- Connectivity Requirements module boundary;
- consumer-owned Authority/ACC/RC ports as required by accepted semantics;
- persistence port;
- no direct database/framework dependencies in Domain/Application;
- cross-context relationship to ACC/RC/AM;
- no Decision-domain dependency unless the accepted requirement model genuinely needs one.

Exit:
dependency direction and semantic ownership are explicit.

### WP4 — Domain + Application executable core

Status: `done`.

Implement inside-out:
- aggregate/value objects;
- commands/queries;
- authority-first application use cases;
- exhaustive relevant core tests;
- architecture/import guards.

Core gate must pass before infrastructure.

### WP5 — PostgreSQL persistence

Status: `done`.

Implement module-owned schema/migration/repository:
- authoritative uniqueness/idempotency from accepted identity;
- lifecycle/property audit atomically with mutation;
- concurrency/rollback proof;
- tracked migration integration.

### WP6 — HTTP contract/runtime

Status: `done`.

Add only use-case-oriented endpoints required by the first owner/responsible-user journey.

Trust boundary:
- actor from authenticated session;
- effective command time from runtime;
- authoritative subject/scope facts from domain/catalogue, not caller spoofing;
- safe denied/unknown/not-found/conflict/persistence mappings.

### WP7 — Web UI: My Connectivity Needs

Status: `active`.

First UI:
- navigation entry for Connectivity Requirements;
- list visible requirements;
- declare a requirement using I12 label-first ACC search;
- requirement details;
- admitted amend/retire actions only if WP1 accepts them;
- stable IDs/provenance secondary to readable catalogue labels.

No approval queue is introduced in I13.

### WP8 — PostgreSQL/Docker end-to-end evidence

Status: `planned`.

Extend local demo with one actor/responsibility/requirement scenario.

Prove through public nginx endpoint:

```text
login
 -> declare valid Connectivity Requirement
 -> read it back
 -> no Access Rule created merely because the requirement exists
```

Include denied/unknown authority and persistence failure evidence.

### WP9 — Final review/gates/canonical absorption

Status: `planned`.

Run:
- core;
- PostgreSQL;
- Web;
- Docker;
- harness;
- knowledge;
- architecture/security review.

Close all P0/P1.

Then:
- absorb I13 outcomes into canonical domain/requirements/architecture/engineering truth;
- mark I13 `done` in the product-completion roadmap;
- promote I14 Requirement-to-Policy Alignment;
- remove this active plan;
- squash merge one coherent I13 semantic stage.

## Exit criteria

I13 is complete only when:

- Connectivity Requirement Tactical identity/lifecycle is accepted rather than inferred from persistence;
- one authoritative requirement can be declared/read and, if accepted by WP1, amended/retired;
- every accepted mutation is authorized and business-audited;
- the requirement references only accepted semantic subjects;
- retries/concurrency cannot create contradictory authoritative requirement truth;
- Requirement existence has zero implicit Access Policy effect;
- no `Allowed`, Access Rule or configured-access conclusion is manufactured by I13;
- PostgreSQL/runtime/Web/Docker evidence proves the first journey;
- all final repository gates pass;
- no open P0/P1 finding remains.

## Blockers

No current owner/product blocker.

No current semantic blocker. WP6 core/PostgreSQL/Docker/harness/knowledge gates are green, including the fresh-stack migration packaging fix.

## Next

Implement WP7 My Connectivity Needs Web workspace over the accepted I13 HTTP contract; no approval/decision UI.
