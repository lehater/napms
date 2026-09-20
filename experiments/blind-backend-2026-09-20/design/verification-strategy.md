# Backend verification strategy

Status: ACCEPTED after Coding-Agent Challenge 07 repair

## Purpose

Prove that the blind backend closure is realizable without a coding agent inventing material product/domain/architecture/interface/data/security/operability semantics.

Accepted design artifacts are the oracle. Existing NAPMS implementation/design is not evidence.

## V1 — Domain behavior

### Resource Description
- Resource/Endpoint identity survives address set/change/clear.
- Missing current address remains explicit.
- Site assignment and singular OWNER/ADMINISTRATOR replacement/clear preserve non-overlapping history.
- setting an already-current responsibility is a no-op.
- address history preserves effectiveFrom/effectiveTo/changedBySubject.
- HOST accepts canonical IPv4/IPv6 literal only; PREFIX requires CIDR with host bits already zero; host-bit prefixes reject rather than mask; mapped IPv6 is not silently converted to IPv4.
- Site and ResponsibilityGroup remain immutable in selected MVP.

### Application Communication
- Component belongs to exactly one Application.
- Interaction may reference Components from different Applications; no same-Application invariant is permitted.
- Interaction subject is immutable.
- published InteractionRevision is immutable; changed traffic meaning creates a new revision.
- revision preserves createdAt/createdBySubject.
- ipProtocol is integer 0..255 with no canonical name aliases.
- only TCP(6)/UDP(17) permit port ranges; other protocols require empty port sets.
- port lists canonicalize by sort + merge overlap/adjacency without crossing gaps.
- unsupported traffic semantics reject rather than widen/approximate.

### Business Connectivity
- Need is business justification, not permission.
- participantComponentRef is required and equals either Interaction source or destination Component.
- source-side and destination-side Needs for one Interaction remain independently representable.
- Need is independent from Deployment/IP.
- retirement is terminal, preserves historical createdAt/createdBySubject and never rewrites permission/current-access state.

### Access Policy
- AccessSubject is exactly sourceDeploymentRef + destinationDeploymentRef + interactionRevisionRef.
- NeedRef and current technical realization are not Rule identity.
- AccessRequest subject/initial Need/provenance are immutable and finalizes once.
- one PolicyRule exists per AccessSubject.
- first Rule is ACTIVE with unbounded window.
- AuthorizationEvidence is append-only/unique by AccessRequestRef and exports immutable request submitter/time/initialNeedRef plus decision actor/time.
- JustificationAssociation is append-only/unique by NeedRef.
- PolicyRule version covers evidence set, justification set and operational state/window.
- state/window no-op changes version/history neither.
- evidence/justification-only changes do not create operational-history events.
- zero current Need does not mutate permission/effect state.

## V2 — Application orchestration

Evidence: contract tests against public application services/ports.

- idempotency lookup/replay occurs before NEW-command If-Match validation.
- Application version guards Component creation; Interaction is an independent aggregate; Interaction version guards revision publication.
- SubmitAccessRequest:
  - opens one Access Policy READ COMMITTED write transaction;
  - Business Connectivity lockAndResolveCurrentNeed acquires FOR SHARE-equivalent validation lock held through commit;
  - exact revision, deployment direction and participant semantics are validated;
  - Access Policy never writes Business Connectivity.
- AttachPolicyRuleJustification uses the same current-Need locking semantics.
- Need retirement race has deterministic lock-order outcomes.
- ALLOWED finalization atomically finalizes request, resolve/creates one Rule, appends evidence, attaches initial Need and idempotency result.
- later ALLOWED for same AccessSubject:
  - reuses Rule;
  - appends new evidence;
  - advances whole-Rule version exactly once;
  - does not reset state/window;
  - creates no operational-history event.
- evidence append racing access.manage cannot lose either update.
- additional Need attachment adds no permission evidence.
- Need retirement is reflected by subsequent composed reads without Access Policy mutation.
- zero current Need derives NO_CURRENT_BUSINESS_JUSTIFICATION only.
- ordinary growing reads are cursor-bounded; no parent view embeds unbounded child collections.

## V3 — PostgreSQL persistence/transaction integration

Evidence: tests against a fresh real supported PostgreSQL instance.

### Ownership/schema
- no cross-owner database FK/write coupling.
- no interaction.application_ref or same-Application constraint.
- owner-local Application->Component and Interaction->Revision relationships only.
- Access Policy stores NeedRef association but not authoritative Need currentness.
- unique PolicyRule AccessSubject constraint.
- unique AuthorizationEvidence AccessRequestRef.
- unique PolicyRule+Need association.
- required temporal/current-role constraints are enforced.

### Aggregate versions
- Resource -> Endpoint/address/Site/responsibility mutation.
- Application -> Component creation.
- Interaction -> revision publication.
- BusinessProcess -> organization/Need mutation.
- AccessRequest -> final decision.
- PolicyRule -> evidence/justification/operational mutation.
- no child version bypass.

### Current-Need locking
- if retirement update/commit wins before validation lock, submission/attachment observes RETIRED and rejects.
- if validation FOR SHARE-equivalent lock wins, retirement waits until Access Policy commit.
- waits are bounded by request/DB statement timeout.
- Access Policy issues no Business Connectivity UPDATE.

### Idempotency
- scope = principal + method + route + normalized target + key.
- same committed fingerprint replays exact persisted original JSON body bytes/status/Location/ETag before stale If-Match check, even after the aggregate has changed later.
- same scope/different fingerprint -> IDEMPOTENCY_CONFLICT.
- same key/different target is independent.
- concurrent identical: first commit -> replay; first rollback -> waiter proceeds NEW; unresolved timeout/DB failure -> DEPENDENCY_UNAVAILABLE.
- state + idempotency result commit atomically.
- committed idempotency records have no selected-MVP TTL/expiry; no automatic application mutation retry.

### Read snapshots
- composed PolicyRule reads resolving Need status use read-only REPEATABLE READ.
- materialization preflight and emit use the same read-only REPEATABLE READ snapshot; the first DB statement both establishes that snapshot and returns transaction_timestamp(), which is the exact evaluationAt.

## V4 — HTTP/API contract

Evidence: black-box API tests against composed backend.

### Boundary/error rules
- strict JSON missing/null/unknown/server-owned-field behavior is exact.
- request body over NAPMS_HTTP_MAX_REQUEST_BODY_BYTES -> 413 PAYLOAD_TOO_LARGE before semantic command execution.
- correlation validation/generation/echo exact.
- If-Match missing/current/stale -> 428/success/409 for correct aggregate owner.
- stable Problem code/status mapping exact.
- committed idempotent replay can succeed with original now-stale If-Match.
- unresolved concurrent idempotency wait -> 503, not 409.

### Growing collections
For Resource endpoints/history, Application Components, Interaction revisions, Process Needs, Rule evidence/justifications/history:
- default limit 50, valid 1–200;
- opaque forward cursor;
- malformed/cross-query cursor -> 400;
- no silent truncation;
- parent/current views expose counts;
- no cross-request snapshot guarantee is asserted.

### Current access/audit
- Rule view exposes current state/window/counts/reconciliation.
- authorization evidence and participant-attributed justification pages are complete.
- operational history exposes CREATED/OPERATIONAL_CHANGED actor/time/state/window and excludes no-op/evidence-only/justification-only events.

### Materialization
- body {} selects ALL.
- explicit non-empty unique PolicyRuleRef set selects exactly that subset.
- no semantic selected-Rule count cap exists; transport input is bounded only by configured request-body bytes.
- unknown selected ref -> REFERENCE_INVALID; duplicate/empty explicit set -> INVALID_INPUT.
- preflight completes before HTTP 200 commitment.
- preflight dependency failure -> 503/500 Problem before materialization body.
- COMPLETE and UNRESOLVED -> HTTP 200.
- selected INACTIVE/out-of-window Rule is nonEffective and does not require technical realization, but its complete authorization/business provenance must still resolve.
- unresolved permission/business provenance for any selected Rule -> UNRESOLVED; unresolved technical realization -> UNRESOLVED only for selected effective Rule.
- post-commit client/transport failure yields incomplete body, not a valid export.

### Self-contained explainability
Every successful materialization response contains:
- one MaterializedRuleProvenance per selected Rule;
- exact AccessSubject/state/window/effective-at-evaluation;
- all AuthorizationEvidence including submittedBySubject/submittedAt/initialNeedRef and decision provenance;
- all participant-attributed Need justification/currentness;
- reconciliation flags;
- normalized technical rows referencing PolicyRuleRef;
- explicit address actor/time realization facts.

A caller possessing policy.export but not policy.read can explain every exported/non-effective selected Rule from the export response itself.

## V5 — Security

- valid identity requires non-empty sub.
- token alg must be in configured asymmetric allow-list and key type-compatible; none/HS*/unknown reject; kid is required non-empty string.
- issuer exact-match; aud required string-or-array containing configured audience.
- exp required and nbf optional use configured clock skew exactly.
- missing permission claim -> authenticated empty permission set.
- permission claim present -> array<string>; wrong type/non-string -> 401.
- duplicate strings collapse; unknown permission strings grant no known permission.
- invalid token against established usable key -> 401.
- inability to establish validity because key material is unavailable/stale -> 503 rather than false 401/fail-open.
- missing/wrong-type kid -> 401 without refresh; unknown kid -> bounded refresh, successful refresh still missing kid -> 401, refresh dependency failure preventing validity -> 503.
- configured issuer is HTTPS-only; discovery issuer exact-match and jwks_uri HTTPS-only are enforced with downgrade redirects rejected.
- initial metadata/JWKS acquisition succeeds before listener start; initial failure exits non-zero.
- runtime unknown-kid/readiness refresh is bounded and single-flight; one attempt is a full discovery+JWKS validation cycle and one sequence performs at most configured attempts with backoff between failures.
- successful refresh atomically replaces validation material and resets lastSuccessfulValidationMaterialRefreshAt; failed refresh preserves prior material/timestamp.
- cache age is now-lastSuccessfulValidationMaterialRefreshAt; max-stale must be >0 and provider cache headers cannot extend it.
- refresh failure with still-usable cache preserves readiness; beyond max-stale without successful refresh -> readiness DOWN.
- exact operation permission matrix; no permission implication.
- request/decide/manage/read/export independent.
- Resource responsibility, Process organization and Need existence never grant authorization.
- current caller is authenticated/authorized again before idempotent replay.
- actor/permission/server provenance cannot be mass-assigned.
- tokens/DSN/secrets/stacks/schema absent from public errors and allow-listed diagnostics.
- hostile inputs reach SQL only as bound parameters.

## V6 — Architecture/component structure

Mechanical checks prove:
- domain packages import no HTTP/PostgreSQL/OIDC/telemetry/config.
- API handlers import no concrete repositories.
- owner adapters mutate only owner tables.
- ApplicationRepository does not own Interaction.
- Interaction creation does not mutate Application rows.
- Access Policy does not store authoritative Need currentness.
- CurrentPolicyMaterializer has no write port.
- transaction isolation/current-Need lock is isolated in persistence/ConsistencyRunner/owner adapter contracts.
- environment is read only by startup config/bootstrap.
- public HTTP DTOs do not leak into domain.
- no generic cross-owner repository/service locator.

## V7 — Operability/configuration

- mode-specific configuration is enforced: migrate requires DB DSN/statement timeout only; serve requires full serve set. Unknown NAPMS_* fails both modes.
- unknown NAPMS_* key fails startup.
- no config-file/CLI/runtime-reload override path exists.
- required numeric timeout/retry/body-size values have no hidden defaults.
- OIDC initial pre-listen acquisition + runtime single-flight fetch retry/backoff/max-stale exact.
- DB statements, Need locks and idempotency-key waits obey request/statement deadlines.
- no automatic DB mutation retry.
- correlation propagates through required events.
- liveness is process-only; readiness requires DB + usable OIDC validation material.
- cancellation propagates to DB/materialization.
- materialization success event is emitted only after a syntactically complete result; truncated/aborted stream never emits successful completion.
- `migrate` acquires exclusive advisory migration lock, verifies immutable ids/checksums, applies pending migrations transactionally and starts no listener.
- concurrent migrators serialize; failure leaves last fully committed migration.
- `serve` never applies DDL and refuses pending/missing/unknown/checksum-mismatched schema before listener.
- external TLS is deployment-owned; application has no TLS-cert config and ignores forwarded identity/permission headers.
- graceful shutdown: ready DOWN, stop new requests, drain to grace, then cancel.
- diagnostics contain no secret/full body.

## V8 — Fresh-start end-to-end

From empty PostgreSQL: run binary `migrate`, then `serve`, then use public HTTP only:

1. create Site/groups/Resources/Endpoints/current addresses;
2. create Application A/C1 and Application B/C2;
3. create cross-Application Interaction C1 -> C2 and publish revision;
4. create source/destination Deployments;
5. create BusinessProcess P1 + source-participant Need;
6. create BusinessProcess P2 + destination-participant Need;
7. submit AccessRequest with request-only principal using one current Need;
8. record ALLOWED with decide-only principal;
9. attach second participant-side Need with manage-only principal;
10. verify same one PolicyRule, complete evidence/justification audit and ACTIVE/unbounded state;
11. materialize with export-only principal lacking policy.read;
12. assert COMPLETE response is self-contained: ruleProvenance explains permission/business basis and rows carry exact normalized technical effects linked by PolicyRuleRef.

Negative/edge siblings include:
- cross-Application Interaction must succeed;
- reversed deployment direction;
- RETIRED Need request/attachment;
- Need retirement lock races;
- DENIED;
- duplicate ALLOWED subject convergence + Rule-version race with manage;
- stale/missing ETag;
- idempotency replay/conflict/different target/concurrent timeout;
- missing realization effective vs non-effective distinction;
- zero current Need reconciliation without revocation;
- effective-window boundaries;
- subset ALL/explicit and oversized body 413;
- invalid permission claim variants;
- OIDC dependency unavailable;
- materialization preflight failure before 200;
- post-commit stream cancellation/truncation;
- startup/config/shutdown failure paths.

## Non-gates

Numeric latency, throughput, HA, RPO and RTO targets are not correctness gates because source input provides none. Structural boundedness, transaction semantics and correctness evidence above are gates.
