# Backend implementation design

Status: ACCEPTED candidate after Source Corpus amendment 02

## Implementation target

Greenfield realization of the blind backend design only. Existing NAPMS production code is not an input and must not be copied or used to settle semantics.

## Selected realization stack

- Language: Go, current supported stable toolchain at implementation start.
- Runtime: one Go binary with explicit `migrate` and `serve` modes. `serve` is one stateless HTTP process using Go standard HTTP/context facilities; no application framework is required.
- Database: PostgreSQL.
- Database access: explicit bound SQL through a PostgreSQL driver/pool; no ORM.
- JSON: strict decoder that can reject unknown fields as required by Interface Design.
- Authentication: maintained OIDC/JWT validation library or small adapter capable of the accepted issuer/audience/signature/time and bounded JWKS cache/fetch semantics.
- IDs: server-generated opaque UUID values; UUID structure is not semantic.
- Timestamps: PostgreSQL/Go UTC instants with RFC 3339 at HTTP boundary.

Rationale: this stack directly satisfies modular-monolith, explicit dependency, cancellation/context and snapshot-transaction contracts with minimal framework semantics. PostgreSQL provides the required transactional snapshot and constraint model.

A library may be substituted only when all accepted external/transaction/security/operability behavior remains unchanged.

## Repository/module layout contract

Suggested top-level realization:

- `cmd/napms/` — process bootstrap/composition only.
- `internal/resource/` — Resource Description domain/application ports/services.
- `internal/applicationcommunication/`
- `internal/applicationdeployment/`
- `internal/businessconnectivity/`
- `internal/accesspolicy/`
- `internal/policymaterialization/`
- `internal/platform/httpapi/` — strict DTO/router/ETag/idempotency/problem mapping.
- `internal/platform/security/` — OIDC authentication + permission authorizer.
- `internal/platform/postgres/` — pool, transaction runner, migrations and owner adapters.
- `internal/platform/observability/` — structured evidence/metrics/correlation.
- `internal/platform/config/` — startup-only `NAPMS_*` environment parsing/validation.
- `migrations/` — ordered SQL grouped/named by owning module.

Equivalent names are allowed if dependency/ownership boundaries remain mechanically recognizable.

## Process modes

- `napms migrate`: requires DB DSN + DB statement timeout; acquires exclusive PostgreSQL advisory migration lock, validates ordered migration checksums, applies pending migrations transactionally and exits. It creates no HTTP/OIDC/application services.
- `napms serve`: validates full serve configuration, verifies schema ids/checksums are exactly current, initializes OIDC validation material, then opens the HTTP listener. It never applies migrations.
- mode selection is not configuration precedence and accepts no configuration values via CLI flags.

External TLS is deployment-owned: ingress/reverse proxy/load balancer terminates HTTPS; the internal serve listener is plaintext only inside the trusted deployment boundary and must not be publicly exposed. No TLS certificate/key configuration is implemented by the application.

## Runtime configuration realization

Implement the Operability Design keys exactly:

- `NAPMS_LISTEN_ADDR`
- `NAPMS_DATABASE_DSN`
- `NAPMS_OIDC_ISSUER`
- `NAPMS_OIDC_AUDIENCE`
- `NAPMS_OIDC_PERMISSION_CLAIM`
- `NAPMS_OIDC_ALLOWED_ALGS`
- `NAPMS_OIDC_CLOCK_SKEW`
- `NAPMS_DB_STATEMENT_TIMEOUT`
- `NAPMS_HTTP_REQUEST_TIMEOUT`
- `NAPMS_HTTP_MAX_REQUEST_BODY_BYTES`
- `NAPMS_OIDC_HTTP_TIMEOUT`
- `NAPMS_OIDC_FETCH_MAX_ATTEMPTS`
- `NAPMS_OIDC_FETCH_BACKOFF`
- `NAPMS_JWKS_MAX_STALE`
- `NAPMS_SHUTDOWN_GRACE`
- optional `NAPMS_LOG_LEVEL`.

Requirements:
- migrate profile requires only DATABASE_DSN + DB_STATEMENT_TIMEOUT; any supplied other known NAPMS_* keys are validated, unknown keys fail;
- serve profile requires the full serve set;
- parse/validate once before mode work/listener;
- reject unknown `NAPMS_*` names;
- no config files/flags/runtime reload/feature flags;
- no hidden numeric defaults for required timeout/retry/body-size keys;
- DSN value is secret/redacted;
- OIDC adapter must enforce HTTPS-only configured issuer/discovery/jwks_uri with downgrade rejection plus Security Architecture's exact alg/kid/aud/exp/nbf/sub/permission-claim contract and surface “invalid token” separately from “cannot establish validity because key dependency is unavailable”;
- after parsing config, initialize OIDC metadata/JWKS with the accepted bounded retries before opening listener; failure aborts startup;
- runtime refresh is one single-flight path shared by readiness/protected validation; no independent fetch storms.

## Slice order

### I1 — Runtime skeleton and owner boundaries

Create module/package skeleton, composition root, strict mode-specific startup configuration, dedicated MigrationRunner/SchemaVerifier, PostgreSQL pool, OIDC initial validation-material acquisition for serve, correlation context, health probes, shutdown handling and architecture dependency checks. No product behavior beyond startup/health.

Completion:
- `migrate` initializes a fresh DB; concurrent migrate processes serialize; `serve` accepts only exact current migration ids/checksums and never applies DDL;
- valid config + usable initial OIDC validation material starts; invalid/missing/unknown config or failed initial OIDC acquisition fails before listen;
- live/ready and graceful shutdown contracts executable;
- forbidden dependency checks executable.

### I2 — Resource Description

Implement immutable Site and ResponsibilityGroup registration/read; Resource/Endpoint, Site assignment, address history and responsibility history; Resource-version optimistic concurrency; accepted HTTP representations.

Completion:
- T-RES-*;
- Site-history preservation;
- Resource stale-concurrency/ETag;
- idempotent creates;
- resource permission matrix;
- persistence integration.

### I3 — Application Communication

Implement two aggregates inside the module:
- Application + Component, where Application version guards Component creation;
- independent Interaction + immutable InteractionRevision, where Interaction creation may reference Components from different Applications and Interaction version guards revision publication.

Completion:
- cross-Application Interaction acceptance and no false same-Application validation;
- T-TRAFFIC-REVISION/property tests;
- Application ETag only for Component creation;
- Interaction ETag only for revision publication;
- idempotent Interaction/revision creates;
- HTTP/persistence contracts.

### I4 — Application Deployment and Business Connectivity

Implement immutable ComponentDeployment registration/read; Process/ResponsibleOrganization; Need creation with required participantComponentRef constrained to Interaction source/destination Component; terminal Need retirement with BusinessProcess-version concurrency.

Completion:
- deployment reference validation;
- no deployment label/move/retire API;
- Need lifecycle/history/currentness + participant-side attribution;
- process-child ETag/idempotency;
- relevant authorization/API tests.

### I5 — Access Policy

Implement:
- immutable AccessRequest with AccessSubject + initial Need justification;
- final ALLOWED/DENIED request decision;
- one PolicyRule per unique AccessSubject;
- atomic ALLOWED resolve/create Rule + AuthorizationEvidence + initial Need association;
- multiple authorization-evidence entries and participant-attributed Need justifications without duplicating Rule; whole-Rule aggregate version advances on every newly appended evidence/justification set mutation;
- ACTIVE/INACTIVE + absolute EffectiveWindow;
- additional current-Need attachment with participantComponent validation;
- derived NO_CURRENT_BUSINESS_JUSTIFICATION without copied Need currentness;
- Rule operational/evidence/justification ETag concurrency and cursor-bounded operational audit history; evidence/justification-only mutation never creates operational-history row;
- replay-before-If-Match idempotency semantics.

Completion:
- T-REQUEST-* and T-DECISION-*;
- T-RULE-UNIQUE-SUBJECT / DIFFERENT-SUBJECT / NO-NEED-IN-IDENTITY;
- T-JUSTIFICATION-* and T-NEED-RETIREMENT-RECONCILIATION;
- T-RULE-EFFECT-* / T-EFFECTIVE-WINDOW-*;
- idempotency target-scope/replay-before-ETag/concurrency contracts, including commit->replay, rollback->NEW and unresolved wait->503;
- request/decide/manage/read permission separation.

### I6 — Current Policy Materialization

Implement read-only shared-snapshot CurrentPolicyMaterializer with:
- all-Rules or explicit PolicyRule subset selection;
- operational/effective-window evaluation before technical realization;
- current/retired Need resolution from Business Connectivity;
- NO_CURRENT_BUSINESS_JUSTIFICATION reconciliation flag;
- no automatic deactivation when current Need count is zero;
- exact canonical ipProtocol/port-range and IPv4/IPv6 HOST/PREFIX expansion for selected effective Rules only;
- self-contained streamed `ruleProvenance` for every selected Rule containing AuthorizationEvidence with request submitter/time/initialNeed + decision actor/time and participant-attributed Need justification/currentness/reconciliation; unresolved accepted provenance for any selected Rule makes the result UNRESOLVED even when that Rule is INACTIVE/out-of-window; normalized technical rows correlate by PolicyRuleRef and carry explicit Resource-address actor-time facts; paginated Rule endpoints remain an additional audit surface; no generic provenance blob;
- stable nonEffective and MaterializationIssue representations.

Completion:
- COMPLETE and UNRESOLVED are HTTP 200 application results;
- inactive/out-of-window selected Rules create nonEffective entries and waive only technical-realization requirements; provenance completeness remains mandatory;
- zero-current-Need Rule can still COMPLETE with reconciliation flag;
- effective missing realization -> UNRESOLVED;
- dependency failure -> HTTP 503;
- all/subset selection with no semantic subset-count cap, configured request-body safety limit, two-phase preflight-before-HTTP-commit, bounded/chunked same-snapshot processing, self-contained provenance, preflight-503 and post-commit truncated-stream tests green.

### I7 — Security and operability closure

Implement the already-accepted API error/header semantics, all authorization mappings, OIDC cache/fetch rules, diagnostic evidence, metrics, timeouts/cancellation, config non-reload and secret redaction.

This slice contains no new external/domain semantics.

Completion: V4/V5/V7 and configuration/security test contracts green.

### I8 — End-to-end/fresh-start closure

Run all migrations on empty PostgreSQL and execute complete + negative sibling journeys using only public HTTP and configured OIDC test infrastructure.

Completion: V8 and all Test Design obligations green; no manual DB state fabrication.

## PostgreSQL realization constraints

- separate logical schemas or unambiguous table ownership prefixes per semantic owner; exact names are local;
- owner-local FK/check/unique/exclusion constraints implement Persistence Design;
- no FK across independently owned module schemas;
- effective temporal rows use `timestamptz`;
- address storage may use validated canonical text or PostgreSQL network types only if HOST/PREFIX distinction, IPv4/IPv6 family, mapped-IPv6 identity and strict no-host-bits Prefix semantics are preserved; never let a database cast silently mask a Prefix;
- traffic storage follows Persistence Design exactly: ipProtocol integer 0..255; separate normalized source/destination range rows; ports only for TCP(6)/UDP(17); no protocol-name alias parsing at HTTP/domain boundary;
- Resource/Application/Interaction/BusinessProcess/AccessRequest/PolicyRule optimistic versions follow Persistence Design exactly; no duplicate child version semantics;
- transaction runner sets isolation explicitly; current materialization uses read-only REPEATABLE READ and obtains evaluationAt from the first statement's PostgreSQL transaction_timestamp();
- prepared/bound parameters only;
- migration identity/checksum is immutable and mandatory; changed/unknown/missing migration state is rejected. `migrate` uses an exclusive PostgreSQL advisory lock; `serve` only verifies.

## Completion criteria

IMPLEMENTATION is complete only when:

1. every HTTP operation, request/response shape, status/header rule, growing-collection pagination rule and authorization mapping in Interface/Security Design exists;
2. required Idempotency-Key and If-Match semantics are applied exactly; idempotency stores exact response JSON bytes/status/Location/ETag for replay, never reconstructs from current state, and committed records have no MVP TTL;
3. every domain invariant and application consistency rule is enforced at its owner;
4. PostgreSQL schema/migrations realize Persistence Design including Resource Site/address/responsibility history, independent Application/Interaction aggregate ownership, one Rule per AccessSubject, evidence/justification uniqueness and idempotency replay data;
5. CurrentPolicyMaterializer obtains evaluationAt from the same DB snapshot transaction_timestamp(), evaluates selection + ACTIVE/window semantics, performs complete bounded preflight before HTTP 200 commitment, derives Need reconciliation without revocation, cannot return COMPLETE with unresolved selected-effective Rule input, returns preflight dependency failure as 503/500, and treats post-commit stream failure as incomplete/non-artifact rather than a successful export;
6. materialization response is self-contained for explainability: one complete provenance record per selected Rule preserves all permission/business evidence/currentness/reconciliation, while normalized rows preserve exact traffic semantics and correlate by PolicyRuleRef; paginated Rule endpoints are supplemental, not required to explain export;
7. OIDC authentication/cache/fail-closed dependency distinctions hold;
8. startup configuration, no-reload, retry/timeout, logging/metrics/health/cancellation/shutdown/redaction semantics are observable;
9. architecture/component dependency checks pass;
10. every Test Design contract has executable evidence at the proper level;
11. full fresh-database end-to-end acceptance journey and negative siblings pass;
12. no implementation convention introduces a new product/domain/API/data/security/operability semantic decision, generic provenance schema or alternative Rule-version scope.

## Explicit coding-agent freedoms

Private function/type names, helper decomposition, exact Go filenames, SQL/index/query optimization preserving accepted contracts, choice among maintained libraries that satisfy those contracts, internal migration-runner code/library preserving the fixed migrate/serve/advisory-lock/checksum contract, logger/metrics library, test framework/helpers, UUID library, composition wiring syntax and local refactorings.

Collection pagination/default/max/no-truncation, configured request-body byte enforcement, absence of a semantic subset-count cap, self-contained export provenance, materialization two-phase response-commit boundary and bounded-memory semantics are also not coding freedoms. Exact cursor encoding/chunk size/stream-buffer implementation remain free.

PostgreSQL owner-write/read-snapshot isolation and current-Need FOR SHARE validation-lock semantics are not coding freedoms.

OIDC HTTPS issuer/discovery/JWKS transport, algorithm allow-list source, required kid semantics, clock-skew semantics and initial/single-flight key acquisition lifecycle are not coding freedoms.

Migrate-vs-serve ownership, advisory migration serialization, exact schema verification, DB-snapshot evaluationAt and exact persisted idempotency replay/retention are not coding freedoms.

The following are **not** coding freedoms: same-vs-cross Application validity, ConnectivityNeed participantComponent semantics, AccessSubject fields, Rule uniqueness, Need exclusion from Rule identity, evidence/justification ownership, operational audit-history exposure, automatic-vs-nonautomatic Need revocation, ACTIVE/window semantics, policy subset behavior, endpoint DTO/status/header semantics, permission mapping/claim representation, aggregate concurrency owner, idempotency scope/order, transaction boundaries, OIDC failure classification, configuration precedence/reload/retry semantics, logging safety or materialization COMPLETE/UNRESOLVED meaning.

If implementation discovers an expected behavior not decidable from the closure, it must stop that slice and report the missing upstream decision rather than select a convention.
