# PLAN-029 — I16A Scoped Connectivity Workspace Foundation

Status: `ready / selected current execution`

Date: 2026-09-09.

## Goal

Prepare and implement the first resource-centric owner workspace so an authenticated actor can select a responsibility scope, see the Resources in that scope, see bound application Component Deployments, understand their local/remote connectivity and independent Need/Decision/Policy state, and start connectivity work from that context.

This plan deliberately precedes the real Connectivity Decision runtime replacement. Its purpose is to make the product understandable and operational from the user's mental model before adding more workflow complexity.

## Current stage

WP-07 — Contextual Add Connectivity / Request access.

WP-01 through WP-05 are implemented on the current branch. WP-06 resource-centric Web workspace is implemented and awaits the repository Web/final gates. WP-07 now uses the first executable exact-interaction cut; full zero-interaction authoring remains gated by ACC semantics rather than a UI placeholder.

## Inputs

Canonical product inputs:
- docs/requirements/scoped-connectivity-inventory.md
- docs/requirements/web-ui-requirements.md
- docs/domain/strategic-model.md
- docs/domain/semantic-ownership.md
- docs/domain/resource-role-model.md
- docs/domain/capabilities.md
- docs/domain/ubiquitous-language.md
- docs/domain/connectivity-requirements/tactical-model.md
- docs/domain/connectivity-decision-model.md
- docs/domain/access-policy/tactical-model.md
- docs/architecture/scoped-connectivity-inventory.md
- docs/engineering/post-wave1-product-completion-roadmap.md

Existing implementation evidence:
- Authority Management scope discovery/action checks;
- Resource Catalogue Resource/Endpoint realization;
- ACC Component Deployment / DCS / DeploymentResourceBinding;
- Connectivity Requirements workspace;
- Requirement-to-Policy Alignment;
- Access Rule workspace/effective policy;
- existing local-dev Decision seam.

Product-owner decisions accepted for this plan:
- Connectivity is the primary post-login workspace;
- selected scope defines the local/responsibility side;
- foreign Resource/Component/Deployment catalogue data is globally readable in the current increment;
- foreign catalogue objects are read-only unless a separately admitted action exists;
- fine-grained catalogue visibility is deferred;
- Resources/Components with zero connectivity must be visible;
- Add Connectivity is contextual from the inventory;
- Need / Decision / Policy / Realization remain independent dimensions;
- Connectivity Decision remains final Allowed | NotAllowed.

## Blockers

### P0 — waiting/process semantics, conditional

Only blocks WP-07 if Add Connectivity requires durable cross-request Waiting/Under review state before I16B.

Do not add Pending to Connectivity Decision.

### P1 — fine-grained catalogue visibility

Deferred by accepted product decision. Current I16A baseline keeps foreign Resource/Component/Deployment catalogue data globally readable.

## Work packages

## WP-01 — Domain re-entry: responsibility scope and local Resources

Decision questions:
- What domain relation makes a Resource part of one selected responsibility scope?
- Which bounded context owns the relation?
- Is the relation a Responsibility Assignment subject, Resource affiliation relation, or another accepted concept?
- How does it vary over time?
- Can one Resource participate in multiple responsibility scopes?
- Which user actions follow from the relation, and which remain independently admitted by Authority Management?

Primary method:
1. inspect existing domain evidence and accepted owner language;
2. produce examples/counterexamples for resource owner, technical custodian, policy authority and read-only foreign resource;
3. use docs/process/domain-change-protocol.md;
4. update highest affected canonical DDD artifacts first.

Working artifacts:
- update docs/domain/resource-role-model.md;
- update docs/domain/semantic-ownership.md;
- update docs/domain/capabilities.md;
- update ubiquitous language only if a new accepted term is required;
- update strategic-model only if context ownership/relationship actually changes.

Result: CLOSED.

Accepted:
- Resource Catalogue owns time-qualified Resource Scope Affiliation;
- Authority Management owns actor/action authority for the same Responsibility Scope reference;
- ReadScopedConnectivity independently admits the owner workspace scope;
- Resource may belong to multiple responsibility scopes;
- affiliation changes do not change Resource identity or stored Requirement/Decision/Rule governance scopes;
- authority and catalogue visibility remain separate.

## WP-02 — Scoped Connectivity Inventory semantic contract closure

Goal:
turn the accepted product requirement into an implementation-ready application composition.

Must define:
- exact local-resource query input/output;
- asOf semantics;
- local/remote direction;
- Resource -> Component -> interaction correlation;
- one-to-many DeploymentResourceBinding handling;
- zero-connectivity rows;
- unresolved remote realization;
- Need/Decision/Policy summary semantics;
- safe coarse status exposure;
- partial/unknown/error behavior.

Update:
- docs/requirements/scoped-connectivity-inventory.md;
- docs/architecture/scoped-connectivity-inventory.md;
- acceptance examples if useful.

Result: CLOSED.

Accepted:
- one explicit asOf across authority, affiliations, bindings, requirements, decisions and policy;
- top-level paging over local Resources;
- local-relative incoming/outgoing projection;
- one-to-many Resource/Component bindings;
- zero-connectivity and unresolved-realization semantics;
- safe coarse Requirement/Decision/Policy summaries under ReadScopedConnectivity;
- dimension-specific Unknown/partial-enrichment behavior;
- specification-by-example in scoped-connectivity-inventory-acceptance-examples.md.

## WP-03 — Application/ports core

Goal:
implement the framework-free Scoped Connectivity Inventory composition.

Constraints:
- consumer-owned ports;
- no cross-module repository joins;
- authenticated actor supplied outside the core boundary;
- explicit asOf;
- bounded paging/search;
- no persistence for composite business truth.

Tests first:
- local Resource with zero connectivity;
- outgoing and incoming relationships;
- remote foreign Resource visible;
- multiple Resource bindings;
- unresolved remote realization;
- Requirement/Rule combinations;
- protected-detail/coarse-status behavior;
- ambiguity/failure -> Unknown/explicit partial behavior.

Local exit:
core tests prove product semantics without HTTP/PostgreSQL-specific shortcuts.

## WP-04 — Infrastructure/read adapters

Goal:
provide efficient bounded adapters through existing module-owned persistence and application ports.

Requirements:
- no N+1 behavior where bounded batch reads can preserve semantics;
- module ownership remains intact;
- existing data schemas are reused where semantically valid;
- new persistence only for newly accepted domain truth, never for the inventory projection merely for convenience.

Local exit:
PostgreSQL integration tests prove the read composition over realistic resource/component/requirement/rule data.

## WP-05 — HTTP contract

Goal:
expose the inventory and required scope/options through authenticated HTTP JSON endpoints.

Requirements:
- actor from session;
- selected scope is validated against accepted scope semantics;
- explicit asOf;
- bounded search/filter/paging;
- safe DTOs for coarse vs protected details;
- stable error model.

Update docs/engineering/http-api-contract.md in the same stage.

Local exit:
HTTP tests cover normal, empty, partial, unauthorized and failure paths.

## WP-06 — Connectivity read-only Web workspace

Goal:
make Connectivity the primary post-login route.

Deliverables:
- Sidebar IA v2;
- ScopeSwitcher;
- resource-centric ConnectivityTreeGrid;
- Resource -> Component -> relationship hierarchy;
- zero-connectivity rows;
- remote side;
- DCS/access summary;
- independent Need/Decision/Policy cells;
- relationship details;
- optional technical columns;
- full-width operational layout.

Guardrails:
- no graph yet;
- no fake Planned screen data;
- no unified connectivity Status;
- no UUID-first primary UX.

Local exit:
the usability acceptance criteria in web-ui-requirements.md pass without reading project documentation.

## WP-07 — Contextual Add Connectivity

Goal:
start new connectivity work from a local Component in the inventory.

Deliverables:
- contextual Request access action from an existing exact ACC interaction;
- prefilled selected scope/local Component/exact source-destination-DCS;
- applicability/justification input only when a new current Requirement is needed;
- reuse of an existing current Requirement without rewriting it;
- integration with existing accepted Requirement/proposal/Decision/Rule flow;
- explicit partial outcome when Requirement declaration succeeds but a later proposal step fails.

Deferred from the first executable cut:
- starting from a Component with zero ACC-known interactions;
- arbitrary remote/DCS authoring or selection.

Those require an accepted ACC capability and must not be simulated in the Web client.

Guardrail:
the user-level action may be Request access, but no persistent Access Request entity is invented.

Local exit:
one E2E flow starts from the inventory and reaches the existing valid final outcome without navigating through Compose Connectivity.

## WP-08 — I16A acceptance and handoff to I16B

Acceptance:
- knowledge-check passes;
- make check passes;
- no open P0/P1 architecture/security/domain findings;
- Docker/public demo proves the primary resource-centric journey;
- durable outcomes absorbed into canonical docs;
- completed PLAN-029 removed when I16A closes;
- roadmap promotes I16B.

## Exit criteria

I16A is complete when:

1. responsibility scope -> local Resource semantics are accepted and implemented;
2. the Scoped Connectivity Inventory has no independent business truth/persistence;
3. authenticated users can select a scope and see all local Resources, including zero-connectivity Resources/Components;
4. bound Components and local-relative interactions are visible;
5. remote catalogue side is readable under the current global baseline;
6. Need/Decision/Policy remain independent;
7. protected details respect their own read semantics;
8. Add Connectivity starts from local context and reuses known data;
9. no waiting lifecycle is invented;
10. tests, Docker proof and repository knowledge gates pass.

## Next

After I16A PASS:
- absorb durable semantics into canonical docs;
- remove PLAN-029 from active;
- promote I16B Connectivity Decision Runtime and Workflow;
- create a new active plan for I16B only when execution begins.
