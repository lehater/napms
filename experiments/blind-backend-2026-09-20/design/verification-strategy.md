# Backend verification strategy

Status: ACCEPTED candidate after Coding-Agent Challenge 01

## Purpose

Prove that implementation realizes accepted product/domain/application/system/interface/data/security/operability knowledge without using implementation structure as semantic truth.

## V1 — Pure domain behavior

Evidence: deterministic unit/property tests against public domain operations/value contracts.

Objectives:
- Resource/Endpoint identity survives address change and missing address remains explicit;
- Site change/clear preserves prior Site facts/effective time;
- responsibility change/end preserves prior assignment facts;
- Site/ResponsibilityGroup and ComponentDeployment are immutable in the selected MVP;
- InteractionRevision is immutable and rejects unsupported/invalid traffic semantics;
- ConnectivityNeed is not permission; retirement is terminal and preserves history;
- AccessRequest subject is immutable; DENIED never yields PolicyRule; ALLOWED yields at most one Rule per request;
- PolicyRule ACTIVE/INACTIVE preserves immutable provenance and same-state mutation is a no-op.

## V2 — Application orchestration

Evidence: application contract tests over public ports with controlled fakes, without inspecting private representation.

Objectives:
- every Interface-marked create uses idempotency semantics;
- nested mutation uses the owner aggregate concurrency version, never a child version;
- SubmitAccessRequest validates current Need, exact InteractionRevision and Deployment direction in one shared validation/write snapshot;
- request admission and permission-decision admission remain independent;
- ALLOWED decision + first Rule has one atomic outcome;
- current materialization emits exact stable issue codes and returns UNRESOLVED as a normal result;
- actual dependency failure is not converted into UNRESOLVED;
- independent Rule provenance is never collapsed.

## V3 — PostgreSQL persistence/transaction integration

Evidence: tests against selected real PostgreSQL from an empty migrated schema.

Objectives:
- owner-local constraints implement accepted invariants without cross-owner FK/write coupling;
- Resource version guards endpoint/address/Site/responsibility mutation;
- Application version guards child/revision creation;
- BusinessProcess version guards organization/Need mutation;
- AccessRequest and PolicyRule versions guard their own mutable lifecycle;
- no duplicate child concurrency version exists;
- Resource address/Site/responsibility intervals remain non-overlapping and history survives change/clear;
- stale owner update is rejected;
- idempotency same-key/same-fingerprint replays committed result; different fingerprint conflicts; state+idempotency commit atomically;
- ALLOWED decision cannot be observed without its PolicyRule;
- submission transaction observes one Need state;
- materialization reads one coherent snapshot during concurrent Resource change;
- migration failure leaves last committed migration and fresh schema requires no manual hidden state.

## V4 — HTTP/API contract

Evidence: black-box HTTP tests against composed backend + real database + controlled identity validation.

Objectives:
- strict JSON rejects unknown fields and invalid null/missing distinctions;
- every documented route accepts/returns exactly the accepted DTO;
- create returns 201/Location; mutation/read return accepted statuses;
- X-Correlation-Id validation/generation/echo works;
- every marked Idempotent-create requires Idempotency-Key and preserves replay status/body/Location;
- every marked mutation requires the correct parent/owner If-Match; missing -> 428, stale -> 409;
- stable Problem status/code mapping is exact;
- Resource history cursor/limit contract is preserved;
- materialization COMPLETE and UNRESOLVED both return HTTP 200 application results;
- materialization dependency failure returns 503;
- unsupported traffic semantics are rejected, never approximated.

## V5 — Security

Evidence: black-box authorization matrix tests plus focused OIDC/dependency tests.

Objectives:
- missing/malformed/expired/wrong-issuer/wrong-audience/invalid-signature token -> 401;
- unavailable/stale-beyond-policy OIDC key material preventing validation -> 503, not false 401;
- cached keys are used only within configured max-stale;
- each operation requires exactly its canonical permission; unrelated permission never implies it;
- request/decide/manage/export remain independent;
- Resource responsibility and Process organization never grant application permission;
- caller cannot override trusted principal;
- tokens/secrets/internal stack/schema absent from public errors and representative logs;
- persistence uses parameter binding for hostile input.

## V6 — Architecture/component structure

Evidence: deterministic import/source dependency checks.

Objectives:
- domain packages do not import HTTP/runtime/PostgreSQL/OIDC/telemetry/config;
- API does not import concrete repositories;
- owner adapters do not mutate peer schemas;
- public peer ports expose owner facts, not persistence rows;
- Policy Materialization has no write repository;
- transaction coordination is isolated at ConsistencyRunner;
- environment reads occur only in startup config/bootstrap;
- optimistic mutation exists only at accepted aggregate owners.

## V7 — Operability/configuration

Evidence: composed-runtime tests with captured evidence, controlled environment and dependency fault injection.

Objectives:
- required startup keys are required/validated and unknown NAPMS_* keys fail startup before listen;
- no config file/CLI/runtime-reload path alters accepted config;
- required numeric timeout/retry keys have no hidden defaults;
- correlationId propagates through required diagnostic evidence;
- required auth/decision/materialization/dependency/startup/shutdown events expose safe fields;
- secrets/tokens are redacted;
- liveness is dependency-independent; readiness reflects database and usable OIDC key material;
- OIDC retry count/backoff/cache policy is bounded by config;
- mutation database operations are not automatically retried;
- request timeout/client cancellation reaches database/materialization work;
- graceful shutdown marks readiness down, drains up to configured grace and never claims rollback of committed state.

## V8 — Fresh-start end-to-end

Evidence: apply all migrations to empty PostgreSQL, start with explicit valid config, execute public HTTP journey.

Journey:
1. register Site/ResponsibilityGroups/Resources/Endpoints and addresses;
2. register Application, Components, Interaction and immutable revision;
3. register source/destination ComponentDeployments;
4. register BusinessProcess + active ConnectivityNeed;
5. submit AccessRequest with request-only principal;
6. record ALLOWED with distinct decide-only principal;
7. materialize with export-only principal;
8. assert HTTP 200 COMPLETE, exact normalized rows and full provenance.

Negative siblings cover DENIED, missing realization -> HTTP 200 UNRESOLVED, wrong-direction deployment, retired Need, stale/missing If-Match, missing/conflicting Idempotency-Key, invalid token, unverifiable token dependency, cancellation and fresh-start config failure.

## Non-gates

No latency/throughput/HA/RPO/RTO threshold is a correctness gate because no accepted numeric target exists. Measurements without accepted thresholds are diagnostic only.
