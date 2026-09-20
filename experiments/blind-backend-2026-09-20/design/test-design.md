# Backend executable test design

Status: ACCEPTED candidate after Coding-Agent Challenge 01

Framework/fixture/assertion mechanics remain implementation freedoms. Each contract defines precondition → operation → public/contract oracle.

## Resource/domain contracts

### T-RES-IDENTITY
Precondition: Resource R / Endpoint E has address A1.  
Operation: change E to A2 with current Resource version.  
Oracle: ResourceRef/EndpointRef unchanged; current is normalized A2; history retains A1 with closed interval.

### T-RES-MISSING
Precondition: Resource/Endpoint exists with no current address.  
Operation: read current Resource.  
Oracle: Endpoint exists with `currentAddress:null`; not omitted and not converted to 0.0.0.0/0.

### T-RES-SITE-HISTORY
Precondition: Resource current Site S1.  
Operation: set S2 then clear Site.  
Oracle: Resource current Site becomes S2 then null; history has non-overlapping S1, S2 and explicit current-null assignment periods/effective transitions according to accepted persistence representation.

### T-RES-RESPONSIBILITY-HISTORY
Precondition: active OWNER assignment G1.  
Operation: end assignment.  
Oracle: current assignment disappears; historical fact remains with effectiveTo; group identity never grants permission.

### T-RESOURCE-AGGREGATE-VERSION
Precondition: Resource version V.  
Operation: mutate Endpoint/address/Site/responsibility using V, then another nested mutation using stale V.  
Oracle: first succeeds/new ETag; stale mutation is rejected; no child-specific version is required or accepted.

### T-IMMUTABLE-CATALOGUE-LEAVES
Precondition: Site, ResponsibilityGroup, ComponentDeployment exist.  
Operation: inspect public contract.  
Oracle: no selected-MVP update/move/retire/delete command exists for these immutable facts.

## Application communication

### T-TRAFFIC-REVISION
Precondition: Interaction I has published V1.  
Operation: attempt to change V1; publish changed valid semantics.  
Oracle: V1 unchanged; changed meaning is distinct V2; unsupported protocol-specific semantics are rejected, never widened.

### T-APPLICATION-AGGREGATE-VERSION
Precondition: Application ETag V.  
Operation: add Component/Interaction/revision with V; then use stale V.  
Oracle: child creation uses Application concurrency only; stale request -> STALE_VERSION.

## Business connectivity

### T-NEED-NOT-PERMISSION
Precondition: active Need N.  
Operation: do not submit/record permission decision.  
Oracle: no PolicyRule exists merely because N exists.

### T-NEED-TERMINAL
Precondition: active Need N under BusinessProcess version V.  
Operation: retire with V, then attempt second retirement/reactivation.  
Oracle: first succeeds/new Process version; RETIRED is terminal; historical Need remains.

### T-BUSINESS-PROCESS-VERSION
Precondition: Process version V.  
Operation: create/retire Need or change responsible organization under V, then repeat another child mutation with stale V.  
Oracle: stale mutation rejected; Need has no separate optimistic version.

## Access Policy and cross-owner contracts

### T-REQUEST-DIRECTION
Precondition: revision says C1 -> C2; D1(C1), D2(C2); active Need N.  
Operation: submit D2 -> D1.  
Oracle: INTERACTION_MISMATCH; no AccessRequest/idempotency success committed.

### T-REQUEST-NEED-CURRENT
Precondition: Need retired before submission snapshot.  
Operation: otherwise valid submission.  
Oracle: NEED_NOT_CURRENT; no AccessRequest.

### T-REQUEST-SNAPSHOT-RACE
Precondition: Need active; concurrent retirement and submission coordinated around transaction start.  
Operation: execute both transaction orderings.  
Oracle: validity matches Need state in submission transaction snapshot; no mixed outcome.

### T-DECISION-FINALITY
Precondition: pending AccessRequest A.  
Operations: DENIED then different ALLOWED command; separately ALLOWED then exact idempotent replay.  
Oracle: conflicting later finalization -> DECISION_ALREADY_FINAL; exact replay returns original result; DENIED has no Rule; ALLOWED has one stable Rule.

### T-DECISION-ATOMICITY
Precondition: pending request.  
Operation: inject storage failure between final decision write and Rule insert.  
Oracle: transaction exposes neither partial decision nor Rule; retry through accepted idempotency reaches at most one final result.

### T-RULE-EFFECT-STATE
Precondition: ALLOWED Rule R ACTIVE at version V.  
Operation: set INACTIVE, repeat INACTIVE, then ACTIVE with current versions.  
Oracle: actual transitions preserve RuleRef/request/decision provenance and append history; same-state request is no-op with unchanged ETag/history.

## Policy materialization

### T-MATERIALIZE-COMPLETE
Precondition: one ACTIVE Rule, exact revision, two source endpoints, one destination endpoint, two TrafficClauses.  
Operation: materialize.  
Oracle: HTTP 200 COMPLETE; exact source endpoint × destination endpoint × clause rows; exact ports/address kinds; every row preserves independent provenance; issues empty.

### T-MATERIALIZE-UNRESOLVED
Precondition: active Rule lacks current source realization.  
Operation: materialize.  
Oracle: HTTP 200 UNRESOLVED; issue code SOURCE_REALIZATION_MISSING for that Rule; diagnostic rows are not a complete export.

### T-MATERIALIZE-REFERENCE-UNRESOLVABLE
Precondition: accepted historical reference cannot be resolved due integrity/failure fixture while database request itself is otherwise readable.  
Operation: materialize.  
Oracle: HTTP 200 UNRESOLVED with REFERENCE_UNRESOLVABLE; implementation never silently rebinds a newer ref.

### T-MATERIALIZE-DEPENDENCY-FAILURE
Precondition: database dependency cannot execute materialization.  
Operation: materialize.  
Oracle: HTTP 503 DEPENDENCY_UNAVAILABLE; no UNRESOLVED application result and no COMPLETE event.

### T-MATERIALIZE-INDEPENDENT-PROVENANCE
Precondition: two Rules produce technically equal effects.  
Operation: materialize.  
Oracle: independent Rule/Need/decision provenance remains represented; no provenance-erasing merge.

### T-MATERIALIZE-SNAPSHOT
Precondition: materialization snapshot open; concurrent Resource address change commits later.  
Operation: complete materialization.  
Oracle: one coherent pre-change or post-change snapshot according to ordering, never mixed source/destination facts.

## Persistence/idempotency

### T-IDEMPOTENCY-MATRIX
For every Interface operation marked Idempotent-create:  
Precondition: no record for principal P / operation O / key K.  
Operation: send K + payload A twice, then K + different payload B.  
Oracle: first commits once; second returns original status/body/Location semantic result without re-running mutation; third -> 409 IDEMPOTENCY_CONFLICT.

### T-IDEMPOTENCY-CONCURRENT
Precondition: no record for K.  
Operation: two concurrent identical requests with P/O/K/fingerprint.  
Oracle: at most one authoritative creation; other request replays committed result or receives bounded dependency/timeout failure, never duplicate success state.

### T-IDEMPOTENCY-MISSING
For every marked operation: omit key.  
Oracle: request is rejected before domain mutation according to Interface contract; no state is created.

### T-MIGRATION-FRESH
Precondition: empty PostgreSQL database.  
Operation: apply ordered migrations/start.  
Oracle: structurally ready with no manual data injection; applied migration identity is not re-applied/rewritten.

## HTTP contract

### T-STRICT-JSON
Variants: unknown field, missing required field, forbidden null, caller-supplied server identity/time/version.  
Oracle: exact INVALID_INPUT/validation response; no partial mutation.

### T-CORRELATION
Variants: no correlation header, valid supplied header, invalid supplied header.  
Oracle: generated/echoed valid id; supplied valid id preserved; invalid -> 400; same id appears in required request diagnostic events.

### T-ETAG-MATRIX
For every Interface operation marked If-Match:  
Variants: missing, current, stale.  
Oracle: missing -> 428 PRECONDITION_REQUIRED; current -> normal result + new owner ETag when state changes; stale -> 409 STALE_VERSION; correct owner aggregate is guarded.

### T-HTTP-SUCCESS-SHAPES
For every documented route:  
Oracle: exact status, Location when create, ETag where declared, required body fields/types/nullability; no undocumented semantic fields are required from the client.

### T-PROBLEM-MAPPING
Trigger each stable failure category.  
Oracle: exact HTTP/code mapping, safe detail/correlationId, no stack/schema/secret.

## Authentication/authorization

### T-AUTH-MATRIX
For every Security Architecture row: valid token without required permission then with exactly required permission.  
Oracle: first 403/no mutation; second proceeds; unrelated permission does not imply required one.

### T-AUTH-TOKEN-INVALID
Variants: missing, malformed, expired, wrong issuer, wrong audience, invalid signature with usable key material.  
Oracle: 401 before application-data access.

### T-AUTH-KEY-DEPENDENCY
Variants: cached usable key within max-stale; cache too old; unknown kid with failed bounded refresh.  
Oracle: within-policy cached key may validate; inability to establish validity -> 503 DEPENDENCY_UNAVAILABLE/readiness DOWN, never false 401 or fail-open.

### T-ACTOR-SPOOF
Precondition: authenticated P; request attempts unknown actor/permission field.  
Oracle: strict DTO rejects the field; trusted principal remains P.

### T-PROBLEM-DISCLOSURE
Trigger validation/forbidden/dependency/unexpected failures with secret-like runtime values.  
Oracle: public Problem/log allow-list contains no token, DSN/password or protected secret; stack only protected internal unexpected-failure log.

## Startup/configuration/operability

### T-CONFIG-REQUIRED
For each required `NAPMS_*` key: remove or make invalid.  
Oracle: startup event identifies safe key/category; process exits non-zero before listener.

### T-CONFIG-UNKNOWN
Precondition: otherwise valid config plus unknown `NAPMS_*` key.  
Oracle: startup fails before listen; unknown typo is not ignored.

### T-CONFIG-PRECEDENCE
Attempt config file/CLI/runtime mutation.  
Oracle: no supported application path overrides startup environment; accepted RuntimeConfig is immutable until restart.

### T-CONFIG-NO-HIDDEN-DEFAULT
Omit each required timeout/retry/max-stale/grace value.  
Oracle: startup fails instead of choosing library/framework default.

### T-OIDC-RETRY-BOUND
Precondition: OIDC fetch dependency fails.  
Operation: trigger refresh.  
Oracle: attempts/backoff do not exceed configured values; no unbounded retry/background recovery path is required.

### T-NO-MUTATION-RETRY
Inject transient database error/unknown commit on mutation.  
Oracle: application does not automatically replay the domain mutation; response is failure/unknown and safe client retry uses Idempotency-Key.

### T-HEALTH
Variants: healthy, DB unavailable, usable cached OIDC key, unusable OIDC key.  
Oracle: live reflects process only; ready reflects ability to serve protected traffic; body only UP/DOWN and correct 200/503.

### T-CANCELLATION
Precondition: slow materialization/database query.  
Operation: cancel client/request timeout.  
Oracle: work is cancelled/bounded; no COMPLETE response/event.

### T-SHUTDOWN
Precondition: in-flight request and configured shutdown grace.  
Operation: SIGTERM.  
Oracle: readiness DOWN first, no new application requests accepted, in-flight drains until grace then cancels; committed state is not reported rolled back.

### T-DIAGNOSTIC-EVIDENCE
Trigger successful command, conflict, auth failure, decision, COMPLETE/UNRESOLVED materialization, dependency failure and unexpected failure.  
Oracle: required event class/fields exist and secrets/full request bodies do not.

## Property/state-machine obligations

- arbitrary valid Resource address/Site/responsibility transitions preserve identity and non-overlapping effective history;
- generated port ranges normalize to exactly equivalent semantics or reject invalid bounds; never widen silently;
- AccessRequest permits PENDING -> ALLOWED or PENDING -> DENIED exactly once;
- PolicyRule permits ACTIVE <-> INACTIVE while immutable provenance remains constant and same-state command is no-op;
- arbitrary idempotent/conflicting replay sequences never create duplicate authoritative entities;
- aggregate child command sequences never bypass owner version concurrency.

Test implementation may use example, property, state-machine or fault-injection frameworks; only the observable contracts above are normative.
