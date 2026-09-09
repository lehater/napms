# Current implementation state

Status: `I14 PASS — Requirement-to-Policy Alignment implemented`.

Date: 2026-09-09.

Current execution is owned by `docs/plans/active/README.md`.

## Completed through I7

- I1 authoritative Access Rule materialization core;
- I2 PostgreSQL uniqueness/concurrency/rollback proof;
- I3 authorized Active/Inactive mutation with durable business audit;
- I4 EffectiveWindow mutation/evaluation and authorized effective desired-policy selection;
- I5 coherent immutable Export Snapshot;
- I6 vendor-neutral normalized policy transformation;
- first-class greenfield Authority Management, Application Communication Catalogue and Resource Catalogue bounded contexts;
- PostgreSQL-only persistence with module-owned schemas/repositories and cross-module persistence guards;
- fail-closed temporal Authority/catalogue semantics;
- typed local-dev PostgreSQL configuration/composition;
- direct end-to-end proposal -> Authority -> ACC -> Connectivity Decision -> Access Policy -> effective selection -> snapshot -> normalized export proof.

## I8 result

`PASS` for the explicitly bounded `local-dev` Web UI + HTTP JSON runtime.

Implemented:
- accepted Web UI product/UX baseline and implementation handoff under `docs/ui/`;
- first Web UI vertical slice: Login -> Compose Connectivity -> Access Rule Proposal -> Materialized/Resolved/NotAllowed result;
- React + TypeScript + Tailwind + shadcn-oriented frontend foundation with dark-navy enterprise shell;
- FastAPI HTTP JSON outer adapter derived from application use cases rather than database CRUD;
- local login/password authentication with scrypt-hashed configured credentials and opaque server-side sessions;
- trusted authenticated backend actor identity feeding Authority Management; request-payload `actorId` spoofing is rejected;
- authority-aware proposal-scope discovery and paginated ACC directed-interaction discovery;
- explicit `local-dev` Connectivity Decision adapter returning `Allowed` only after existing Authority and structural-validity checks, with `local-dev:allowed` provenance;
- normalized-policy JSON handoff preserving Rule/decision/Authority/ACC/RC semantics and provenance;
- no partial normalized rows when snapshot facts are stale, missing, ambiguous or correlation-invalid;
- structured JSON completion events, bounded correlation IDs, safe dependency/outcome context and generic public unexpected-error responses;
- explicit liveness/readiness and startup/configuration failure behavior;
- safe mappings for authentication, authority denied/unknown, invalid/unknown interaction, decision unknown/mismatch, persistence uncertainty, not-found, stale/correlation and normalization failures;
- final I8 architecture/security review has no open P0/P1 findings;
- final core, PostgreSQL, Web, harness and knowledge gates passed.

## I9 result

`PASS` for the first operational Access Rule Web workspace.

Implemented:
- explicit Authority action `ReadAccessRule`;
- authorized paginated Access Rule list across unambiguously permitted RuleGovernanceScopes;
- authorized Rule Details using the Rule's stored governance scope;
- independent backend admission of `SetRuleOperationalState`; read permission does not imply mutation permission;
- HTTP routes for Access Rule list, details and Active/Inactive mutation;
- mutation trust boundary: actor comes from session, effective time from runtime, governance scope from authoritative Rule; client-supplied actor/scope/time is rejected;
- Rule Details expose semantic identity, state/effective window, decision correlation, proposal provenance and business state history;
- React workspace navigation for Compose Connectivity and Access Rules, with bookmarkable list/details and server-side pagination;
- Active/Inactive UI action only when backend reports mutation capability `Permitted`;
- PostgreSQL paging and full workspace read -> mutate -> persisted audit proof;
- fail-closed denied/unknown read and mutation authority;
- explicit not-found, same-state and persistence-failure mappings;
- final architecture/security review has no open P0/P1 findings;
- core, PostgreSQL, Web, harness and knowledge gates passed.

## I10 result

`PASS` for the Policy Operations Web workspace.

Implemented:
- independent backend admission of `SetRuleEffectiveWindow` on Rule Details;
- HTTP EffectiveWindow set/change/clear using authenticated actor, runtime mutation time and authoritative Rule governance scope;
- explicit offset-aware `start < end` validation and half-open `[start, end)` semantics;
- EffectiveWindow business-history presentation in the Web UI;
- application-level `ReadEffectiveDesiredPolicy` scope discovery evaluated at the same explicit `asOf` as policy views;
- Effective Desired Policy HTTP/Web view with authorized-empty result distinct from denied/unknown authority;
- Normalized Policy Web view over the existing coherent snapshot/normalization chain;
- normalized presentation preserves `Any`, `NotApplicable`, inclusive ranges, Rule/decision context and Authority/ACC/RC provenance;
- PostgreSQL end-to-end proof from EffectiveWindow mutation through effective selection and normalized export;
- request payload cannot establish actor, mutation time or Rule governance scope;
- final architecture/security review has no open P0/P1 finding;
- core, PostgreSQL, Web, harness and knowledge gates passed.

## I11 result

`PASS` for the Dockerized Local Runtime.

Implemented:
- one-command local startup through `make dev-up`;
- non-root Python backend image;
- multi-stage React build + nginx runtime image;
- Docker Compose topology `postgres -> migrate -> seed -> api -> web`;
- one public local endpoint on `127.0.0.1:8080`; PostgreSQL and FastAPI remain unexposed to the host;
- named persistent PostgreSQL volume with explicit `dev-reset`;
- tracked global migration registry over module-owned SQL files;
- migration journal with SHA-256 checksum protection and PostgreSQL advisory locking;
- repeatable migration execution and fail-fast checksum drift behavior;
- idempotent local-demo seed for one usable connectivity flow and current Authority actions;
- typed seed/runtime configuration;
- secret-safe local login bootstrap: random plaintext password exists only in startup-helper process memory; only its scrypt hash is passed to Compose;
- public-endpoint smoke proof through nginx: readiness -> login -> session -> seeded proposal scope;
- Docker CI gate proving fresh full-stack startup plus repeated migration and seed execution;
- explicit local-only PostgreSQL trust boundary with no host DB port and no production claim;
- final architecture/security review has no open P0/P1 finding;
- core, PostgreSQL, Web, Docker, harness and knowledge gates passed.

## I12 result

`PASS` for Human-readable Catalogue UX.

Implemented:
- optional ACC-owned display names for Component Deployments and immutable DCS revisions without changing UUID-based identity;
- checksum-tracked PostgreSQL migration `application-catalogue/0002`;
- exact-identity batch catalogue presentation reads with DCS subject correlation;
- bounded server-side interaction search executed only after existing `ProposeConnectivity` authority admission;
- DCS traffic summaries decoded from the existing immutable projection payload;
- optional presentation enrichment on already-authorized proposal, Rule, Effective Desired Policy and normalized-policy responses;
- presentation enrichment is fail-soft: missing labels or presentation lookup/decode failure falls back to stable IDs without changing an authorized business result;
- Compose Connectivity is searchable and label-first while submitting the same stable semantic IDs;
- Access Rules, Rule Details, Effective Policy and Normalized Policy show display names first and technical IDs/provenance second;
- local Docker demo seeds `Demo Web Frontend -> Demo Orders API / HTTPS Orders API` and the public smoke test verifies the labels and traffic summary;
- no generic catalogue browse/read endpoint, catalogue CRUD/admin workflow or new read authority was introduced;
- final architecture/security review has no open P0/P1 finding;
- core, PostgreSQL, Web, Docker, harness and knowledge gates passed.

## I13 result

`PASS` for the first executable Connectivity Requirements bounded-context slice.

Implemented:
- accepted Tactical DDD for Connectivity Requirement identity, active semantic uniqueness, Dependent Component Deployment, exact Required Semantic Interaction, Applicability, Justification and terminal `Active -> Retired` lifecycle;
- invariant `Required != Authorized` and zero implicit Connectivity Decision / Access Policy side effect;
- distinct Authority Management actions for declare/read/applicability/justification/retire;
- consumer-owned Authority/ACC ports with fail-closed denied/unknown semantics;
- framework-free Domain/Application core with idempotent declaration, explicit no-op semantics and version-aware mutation;
- module-owned PostgreSQL schema/repository with partial active semantic uniqueness, optimistic concurrency and atomic business audit;
- tracked migration `connectivity-requirements/0001` included in packaged runtime images;
- HTTP API for scope/interaction discovery, declaration, authorized list/detail, applicability, justification and retirement;
- server trust boundary: authenticated actor and runtime business action time are not client-supplied; later actions use stored Requirement Governance Scope;
- Web workspace `My Connectivity Needs` with label-first ACC interaction discovery, declaration, details, applicability/justification mutation and retirement;
- no `Pending/Approved/Rejected`, approval queue or Allowed/Denied status introduced;
- PostgreSQL greenfield E2E proving declaration/read/mutation/retirement, restart persistence, re-declaration after retirement and zero Access Rule creation;
- Docker public-nginx smoke proving login -> Requirement declaration -> read/mutate/retire while Access Rules remain empty;
- final architecture/security review has no open P0/P1 finding;
- core, PostgreSQL, Web, Docker, harness and knowledge gates passed.

Deferred to later increments:
- Connectivity Decision internals/workflow;
- configured/observed technical satisfaction and reconciliation.

## I14 result

`PASS` for the first Requirement-to-Policy Alignment composition.

Implemented:
- non-peer, framework-free application composition over authoritative Connectivity Requirements + Access Policy; no Alignment aggregate, lifecycle, table or migration;
- exact matching by Source Component Deployment + Destination Component Deployment + immutable DCS revision;
- one explicit offset-aware `asOf` for Requirement applicability and Access Rule effective contribution;
- Requirement-centric outcomes `Covered | Uncovered | NotCurrent | Unknown`;
- `Denied` remains deferred because current Access Policy does not persist durable NotAllowed decision truth;
- policy-centric orphan detection remains deferred until a selected operator view has accepted cross-scope authority semantics;
- accepted Option A visibility: `ReadConnectivityRequirement` admits derived coverage status even when Requirement and Rule governance scopes differ;
- derived coverage exposes no Rule ID, Rule governance scope, Decision/proposal provenance, Rule properties or Rule audit;
- Access Policy persistence/contract uncertainty produces `Unknown`, never false `Uncovered`;
- Retired or currently non-applicable Requirements produce `NotCurrent`; I14 does not invent historical lifecycle reconstruction;
- authorized Requirement detail read was factored from mutation-capability checks so Alignment does not invoke unrelated mutation authority;
- HTTP page/detail Alignment reads with mandatory explicit `asOf`;
- My Connectivity Needs list/details show policy coverage without implying approval/denial or configured/observed access;
- PostgreSQL greenfield E2E proves `Uncovered -> Covered -> Uncovered -> NotCurrent` while the owner has no Access Rule read authority and while Requirement/Rule governance scopes differ;
- Docker public-nginx smoke proves the same semantic transition and separately proves Requirement declaration itself does not create an Access Rule;
- final architecture/security review has no open P0/P1 finding;
- core, PostgreSQL, Web, Docker, harness and knowledge gates passed.

Deferred to later increments:
- durable Connectivity Decision / NotAllowed truth and workflow;
- policy-centric orphan-policy operator view;
- configured/observed technical satisfaction and reconciliation.

## I8 scope boundary

I8 intentionally does **not** define Connectivity Decision Domain internals.

The following remain deferred:
- approval/review workflow, approver roles and `Pending/Approved/Rejected` lifecycle;
- persistent generic `Access Request` business identity;
- external OIDC/OAuth2/corporate IdP;
- production authentication/session topology;
- dashboard and secondary aggregate UI;
- broader Access Rule workspace filtering/search;
- generic IAM/CMDB administration;
- CSV/XLSX serializers;
- vendor rendering, configured-state reconciliation and device execution.

## Post-Wave-1 execution

The ordered path toward the current strategic-model notion of product completion is tracked in:

`docs/engineering/post-wave1-product-completion-roadmap.md`.

Next roadmap increment:

`I15 — Connectivity Decision Domain Closure`.

I14 is complete and its active plan is removed during canonical absorption. No new active plan is created in the I14 semantic stage.

Future roadmap increments are not pre-expanded into active plans; each is promoted into an active plan only when execution starts, so deferred domain unknowns are not accidentally represented as accepted implementation detail.

## Current infrastructure boundary

Implemented:
- Access Policy PostgreSQL;
- Authority Management PostgreSQL;
- Application Communication Catalogue PostgreSQL;
- Resource Catalogue PostgreSQL;
- Connectivity Requirements PostgreSQL;
- strict internal DCS projection codec;
- typed local-dev configuration/composition;
- FastAPI HTTP runtime;
- local-dev authentication/session boundary;
- explicit local-dev Connectivity Decision adapter;
- public normalized-policy JSON serializer;
- Requirement-to-Policy Alignment application composition with no dedicated persistence;
- React Web UI through Connectivity Requirements, Requirement-to-Policy Alignment, Operational Workspace, Policy Operations and Human-readable Catalogue UX;
- structured runtime observability/correlation and health/readiness;
- Dockerized local runtime with tracked migrations, demo seed, Connectivity Requirements + Alignment public smoke and nginx same-origin entrypoint.

The implementation remains greenfield: Legacy, MSSQL and vendor/device execution are not dependencies.
