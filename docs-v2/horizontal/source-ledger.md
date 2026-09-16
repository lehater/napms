# Full-width source disposition ledger

Status: IN PROGRESS / non-canonical.

This ledger prevents legacy file placement or vocabulary from silently becoming v2 ownership. `docs/**` is read as accepted design evidence; each source is routed to the earliest semantic stage it actually supports.

## Root documentation contract

| Source | Horizontal disposition |
|---|---|
| `docs/README.md` | reconstruction/source-authority policy; informs horizontal guardrails, not product requirements by itself |
| `docs/AGENTS.md` | repository/agent process guidance; PROCESS-OUT-OF-SCOPE for product S0-S2 reconstruction |

## Requirements sources

| Source | S0/S1/S2 routing |
|---|---|
| `docs/requirements/README.md` | inventory/status evidence; individual referenced contracts are authoritative content |
| `business-connectivity-g1.md` | S0 problem evidence + S1 Business Intent requirements; strategic ownership -> Business Connectivity |
| `application-catalogue-domain-target.md` | S1 ACC/AD/RC target behavior; S2 boundary evidence split across ACC, AD, RC |
| `application-catalogue-target.md` | retained as-built behavior; compatibility facts do not override newer target ownership |
| `catalogue-curation.md` + acceptance/security | S1 catalogue curation behavior; split among ACC/AD/RC/AM boundaries; RC MVP cardinality follows current revalidated S2 |
| `access-governance-g1.md` | S1 proposal/formal-decision behavior retained; legacy Access Governance ownership is superseded by current Access Policy ownership |
| `access-policy-core.md` | S1 concrete PolicyRule behavior; S2 owner Access Policy |
| `network-enforcement-placement-core.md` | S1 placement/relevance behavior; S2 owner NEP |
| `technical-access-evidence-core.md` + acceptance | S1 evidence behavior; S2 owner TAE; acquisition separated as integration capability |
| `policy-realization-reconciliation-g1.md` + `access-policy-realization-mvp.md` | S1 comparison/delta/change/verification behavior; S2 owner APR |
| `provider-policy-renderer-mvp.md` | S1 semantic-preserving rendering behavior; S2 disposition integration capability |
| `network-environment-operations.md` | S1 controlled mutation behavior; S2 owner NEO |
| `policy-export-core.md` + `first-mvp-vendor-neutral-policy-export.md` | S1 export/materialization behavior; strategic disposition RPM composition over authoritative contexts |
| `scoped-connectivity-inventory.md` + acceptance | S1 owner-preserving read behavior; S2 non-peer read composition |
| `traffic-analysis-checker.md` | S1 technical-entry/read-analysis behavior; strategic routing to owner-preserving composition over existing contexts, not a new peer BC |
| `web-ui-requirements.md` | S1 product-facing interaction/quality requirements; UI remains outer adapter and does not create semantic ownership |
| `enterprise-identity-authoritative-sources.md` | current local-first behavior + optional extension seams; authentication/source integration remains outside peer domain ownership, AM remains authority owner |

## Domain sources

| Source family | Horizontal disposition |
|---|---|
| `strategic-model.md`, `context-map.md`, `semantic-ownership.md`, `capabilities.md`, `bounded-contexts.puml` | primary current strategic S2 baseline; normalized into `s2/strategic-model.md` |
| `strategic-model.json` | machine-readable strategic baseline; consistency evidence for the same S2 ownership model, not a second semantic owner |
| `ubiquitous-language.md` | S1/S2 terminology source; candidate glossary reconstruction input |
| `mvp-ddd-convergence-checkpoint.md` | accepted convergence/evidence record; not a separate semantic owner |
| per-context `docs/domain/<context>/**` | tactical/domain-detail evidence used only to verify strategic boundaries/terms in this pass; tactical reconstruction is downstream |
| `resource-role-model.md` | RC/authority/responsibility boundary evidence; responsibility does not imply authority |
| legacy/as-built domain compatibility material | retained only where current docs explicitly require reconstruction; does not override revalidated target strategic ownership |

## Architecture sources

Architecture is downstream of S0-S2. It may corroborate an already accepted boundary or expose a migration gap, but implementation topology/transport does not become upstream truth.

| Source | Horizontal disposition |
|---|---|
| `README.md` | architecture inventory/routing; DOWNSTREAM-S3+ |
| `current-architecture.md`, `code-structure.md` | as-built technical realization; DOWNSTREAM-S3+, not product/domain authority |
| `application-catalogue-target-boundary.md`, `catalogue-curation-boundary.md` | boundary corroboration for accepted ACC/AD/RC/AM semantics; S3 realization details remain downstream |
| `enterprise-identity-authoritative-sources-boundary.md` | corroborates source-integration seam and authentication-vs-authorization boundary; concrete adapter/runtime design downstream |
| `network-context-candidate-boundary.md`, `network-enforcement-placement-boundary.md` | corroborate NEP candidate-relevance semantics; transport/runtime realization downstream |
| `network-environment-operations-boundary.md` | corroborates NEO controlled-mutation boundary; execution architecture downstream |
| `technical-access-evidence-boundary.md` | corroborates TAE-vs-acquisition ownership; collector/runtime details downstream |
| `target-policy-authoring-boundary.md` | corroborates current AP/ACC/AD authoring ownership only where aligned with revalidated requirements/domain; older ownership language cannot override current S2 |
| `first-mvp-policy-lifecycle-export.md` | downstream lifecycle architecture that corroborates exact ACC revision + concrete AD deployment pair + AP lifecycle + complete vendor-neutral export; technical orchestration remains S3 |
| `scoped-connectivity-inventory.md` | downstream realization of owner-preserving read composition; no peer BC promotion |

## Engineering sources

The engineering tree is fully enumerated. It contains 15 files. Product-quality semantics already recovered from error/observability/recovery contracts live in `s1/quality-requirements.md`; concrete HTTP, persistence, DI, configuration, Docker and runbook choices remain downstream.

| Source | Horizontal disposition |
|---|---|
| `README.md` | engineering inventory/authority routing; DOWNSTREAM-S3+ |
| `application-catalogue-target-http-contract.md` | HTTP realization; REFERENCE/S3. Legacy plural-address or deployment-in-ACC transport shapes are not migrated against current S2 |
| `catalogue-curation-command-contract.md` | command/application contract; REFERENCE/S3. Retry/authority/provenance qualities may corroborate S1 but transport shape does not define ownership |
| `catalogue-curation-http-api-contract.md` | HTTP realization; REFERENCE/S3. Current upstream semantics come from requirements/domain |
| `configuration.md` | runtime configuration; DOWNSTREAM-S3+/S4 |
| `current-state.md` | as-built implementation inventory; DOWNSTREAM-S3+ and explicitly not consulted as product design authority |
| `dependency-injection.md` | implementation composition mechanism; DOWNSTREAM-S3+/S4 |
| `error-model.md` | SPLIT: user/system-visible fail-closed/error-disclosure qualities -> S1 quality; exception/HTTP mapping -> S3 |
| `http-api-contract.md` | broad HTTP realization; REFERENCE/S3; does not override current target domain/reference semantics |
| `i2-persistence-engine-decision.md` | persistence technology decision; DOWNSTREAM-S3+ |
| `local-backup-recovery.md` | SPLIT: durable-state recoverability -> S1 quality; pg_dump/container procedure -> S3/S4/operations |
| `local-docker-runtime.md` | local deployment/runtime realization; DOWNSTREAM-S3+/operations |
| `local-product-operator-runbook.md` | operational procedure; DOWNSTREAM-S4/operations; may evidence operability problem but does not define domain semantics |
| `local-upgrade-procedure.md` | operational/upgrade procedure; DOWNSTREAM-S4/operations |
| `observability.md` | SPLIT: correlation/safe diagnostic/explainability qualities -> S1 quality; concrete telemetry/logging implementation -> S3/S4 |

## UI sources

UI is an outer adapter. Observable user jobs/interactions may support S0 journeys or S1 behavior; screen layout, component composition and visual tokens remain downstream presentation design.

| Source | Horizontal disposition |
|---|---|
| `README.md`, `screens.md` | UI inventory/navigation; SPLIT only where they express accepted observable journeys |
| `interaction-rules.md` | S0/S1 interaction evidence: deliberate scope switching, owner-preserving views, contextual access initiation, explicit unresolved states, accessibility/scale qualities |
| `checker.md` | S0 Checker journey + S1 technical tuple/asOf/multiple-match/uncertainty behavior; presentation structure downstream |
| `application-catalogue-target.md`, `application-catalogue-wireframes.md` | SPLIT: search/scale/lifecycle user behavior retained; older deployment-interaction/resource-binding ownership is superseded by current ACC/AD/AP revalidation |
| `resource-catalogue-wireframes.md` | SPLIT: Resource find/manage/history journey retained; plural-address presentation superseded by one effective AddressSpace current decision |
| `component-composition.md`, `components.md`, `layout.md`, `design-system.md`, `design-tokens.md` | presentation-system realization; DOWNSTREAM-S3+/UI design, except accepted accessibility/scale qualities already represented in S1 |
| `references/**` | generated/explanatory visual references; noncanonical presentation evidence; no independent S0-S2 truth |

## Decisions sources

ADRs are decision evidence, not automatically earlier-stage truth. Current/revalidated requirements and domain ownership control target reconstruction; ADRs clarify rationale/supersession and identify downstream constraints.

| Source family | Horizontal disposition |
|---|---|
| `ADR-001*`, `ADR-002*`, `ADR-004*` | architecture/product-history decisions; retain rationale where still current, but realization choices remain downstream |
| `ADR-006*` through `ADR-011*` | catalogue identity/lifecycle/authority/concurrency/reference decisions; corroborate S1/S2 only where aligned with current accepted target docs |
| `ADR-009-i27-dcs-authoring.md` | PARTIALLY SUPERSEDED for target endpoint semantics: deployment IDs inside ACC-authored DCS revision are not migrated; immutable revision/traffic-authoring facts survive only where corroborated by current ACC target |
| `ADR-012-application-definition-deployment-model.md` | later accepted definition/deployment separation; primary decision evidence for ACC vs AD boundary where consistent with current revalidated domain |
| `ADR-013-i31-application-catalogue-compatibility-and-reference-semantics.md` | later compatibility/reference-semantics decision; used to interpret retained as-built compatibility without overriding current target ownership |

## Plans and process sources

| Source family | Horizontal disposition |
|---|---|
| `docs/plans/README.md`, `docs/plans/active/README.md` | plan lifecycle/inventory; PROCESS-OUT-OF-SCOPE for product S0-S2 |
| `docs/plans/active/PLAN-130-revalidate-policy-lifecycle.md` | revalidation work evidence; useful for supersession chronology, not an independent product semantic owner |
| `docs/process/**` | predecessor documentation/change/DDD process; PROCESS-OUT-OF-SCOPE for product reconstruction because docs-v2 process/spec owns the candidate lifecycle |

## Deferred/future material

Deferred material is retained as `EXTENSION` where it describes a real accepted future problem/capability. It is not promoted to current MVP behavior and does not create a new Bounded Context without an independent authoritative lifecycle/model.

## Coverage state

Directory-family accounting is now complete for root, requirements, domain, architecture, engineering, UI, decisions, plans and process. Requirements and engineering are enumerated to file-level/family-level disposition; architecture/UI/decisions have explicit source-family dispositions and known supersession rules.

Remaining semantic work is not tree discovery. It is to finish candidate S0/S1/S2 artifacts from the accounted sources: glossary, acceptance/observable outcomes, strategic context-map artifact and requirement-to-context traceability validation. Any newly discovered material contradiction during that work must be escalated rather than resolved from implementation.
