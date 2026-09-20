# Backend executable test design

Status: ACCEPTED after Source Corpus amendments 01–02

Test framework/fixture mechanics are implementation freedoms. Each contract defines precondition -> operation -> observable oracle.

## Resource Description

### T-RES-IDENTITY
Precondition: Resource R / Endpoint E has address A1.  
Operation: set A2.  
Oracle: ResourceRef/EndpointRef unchanged; current A2 normalized; A1 remains historical with closed interval.

### T-RES-MISSING
Precondition: Endpoint exists with no current address.  
Operation: GET Resource.  
Oracle: endpoint remains visible with currentAddress:null; never omitted or widened to 0.0.0.0/0.

### T-ADDRESS-CANONICAL
Variants:
- IPv4 HOST;
- IPv6 HOST;
- IPv4 PREFIX with zero host bits;
- IPv6 PREFIX with zero host bits;
- IPv4-mapped IPv6 HOST.

Oracle: accepted values return canonical text; HOST/PREFIX kinds and IP family are preserved; mapped IPv6 is not silently converted to IPv4.

### T-PREFIX-HOST-BITS
Variants: `192.0.2.7/24`, IPv6 prefix with non-zero host bits.  
Oracle: request is rejected as INVALID_INPUT; backend never silently masks to a broader network.

### T-RES-SITE-HISTORY
Precondition: Resource current Site S1.  
Operation: set S2, then clear.  
Oracle: current S2 then null; history preserves S1/S2 transitions without overlap.

### T-RES-RESPONSIBILITY-SINGULAR
Precondition: OWNER=G1, ADMINISTRATOR=G2.  
Operation: set OWNER=G3.  
Oracle: OWNER becomes only G3; G1 closes in history; ADMINISTRATOR remains G2.

### T-RES-RESPONSIBILITY-NOOP
Precondition: OWNER=G1 at Resource version V.  
Operation: set OWNER=G1 with current ETag.  
Oracle: 200, unchanged ETag/version, no extra history row.

### T-RESOURCE-AGGREGATE-VERSION
Precondition: two clients hold Resource ETag V.  
Operation: one changes address; second changes Site using stale V.  
Oracle: first succeeds; second 409 STALE_VERSION; no child-specific version bypass.

## Application Communication

### T-INTERACTION-CROSS-APPLICATION
Precondition: Component C1 belongs to Application A; C2 belongs to Application B; A != B.  
Operation: POST /v1/interactions with C1 -> C2.  
Oracle: 201; Interaction subject is C1 -> C2; no Application row/version is mutated solely by Interaction creation.

### T-INTERACTION-NO-SAME-APP-GUARD
Precondition: valid C1/C2 in different Applications.  
Operation: execute domain/application Interaction creation path.  
Oracle: no validation result may reject solely because ApplicationRefs differ.

### T-APPLICATION-COMPONENT-CONCURRENCY
Precondition: Application ETag V.  
Operation: create Component with V, then another Component with stale V.  
Oracle: first succeeds/new Application ETag; second 409 STALE_VERSION.

### T-INTERACTION-REVISION-CONCURRENCY
Precondition: Interaction ETag V.  
Operation: publish revision R1 with V, then R2 with stale V.  
Oracle: first succeeds/new Interaction ETag; second 409; no Application ETag is required.

### T-TRAFFIC-REVISION
Precondition: Interaction has revision V1.  
Operation: attempt to mutate V1; separately publish changed supported traffic as V2.  
Oracle: V1 immutable; V2 distinct; unsupported protocol-specific semantics reject rather than widen.

### T-TRAFFIC-IP-PROTOCOL
Variants:
- TCP ipProtocol=6 with ports;
- UDP=17 with ports;
- ICMP=1 with empty ports;
- arbitrary 0..255 protocol with empty ports;
- non-TCP/UDP with any port range;
- ipProtocol outside 0..255;
- protocol name field such as `"TCP"` instead of ipProtocol.

Oracle: first four are representable according to exact rules; non-TCP/UDP ports -> UNSUPPORTED_TRAFFIC_SEMANTICS; out-of-range/name-alias input -> validation failure; no approximation.

### T-PORT-RANGE-NORMALIZATION
Input source/destination range lists contain unsorted duplicates, overlaps and directly adjacent ranges.  
Oracle: accepted revision exposes sorted merged canonical ranges representing exactly the same port set; ranges separated by a gap are never merged.

## Application Deployment / Business Connectivity

### T-DEPLOYMENT-IMMUTABLE
Precondition: Deployment D(C,R) exists.  
Operation: inspect API/application command surface.  
Oracle: no update/move/retire/delete command exists in MVP.

### T-NEED-PARTICIPANT-ATTRIBUTION
Precondition: Interaction I = C1 -> C2.  
Operation: create Need N1(Process P1,I,C1) and N2(Process P2,I,C2).  
Oracle: both succeed independently; reads preserve participantComponentRef C1 vs C2; neither depends on a Deployment/IP.

### T-NEED-PARTICIPANT-INVALID
Precondition: Interaction I = C1 -> C2; C3 exists but is not an I participant.  
Operation: declare Need(I,C3).  
Oracle: validation rejects; no Need state committed.

### T-NEED-NOT-PERMISSION
Precondition: active Need N exists.  
Operation: no permission decision.  
Oracle: no PolicyRule/current access exists solely because N exists.

### T-NEED-TERMINAL
Precondition: Need ACTIVE.  
Operation: retire; attempt reactivation/second retirement.  
Oracle: RETIRED final; history preserved; invalid later mutation rejected/no-op only if explicitly allowed (reactivation is not allowed).

### T-BUSINESS-PROCESS-VERSION
Precondition: Process ETag V.  
Operation: mutate organization/Need with V, then stale V.  
Oracle: owner version guards child mutation; no Need-specific optimistic version.

## Access Request / permission

### T-REQUEST-DIRECTION
Precondition: revision describes C1 -> C2; deployments D1(C1), D2(C2); current Need N for Interaction.  
Operation: submit D2 -> D1.  
Oracle: INTERACTION_MISMATCH; no AccessRequest/idempotency success.

### T-REQUEST-NEED-CURRENT
Precondition: Need retired before submission snapshot.  
Operation: otherwise valid request.  
Oracle: NEED_NOT_CURRENT; no AccessRequest.

### T-REQUEST-NEED-LOCK-RACE
Precondition: Need ACTIVE; retirement races AccessRequest submission.  
Operation: exercise both lock orderings.  
Oracle:
- if retirement update/commit wins first, request observes RETIRED -> NEED_NOT_CURRENT;
- if Access Policy current-Need FOR SHARE validation lock wins first, retirement blocks until request commits and request succeeds;
- Access Policy never writes Business Connectivity tables;
- lock wait obeys request/DB timeout.

### T-DECISION-FINALITY
Precondition: pending request A.  
Operation: finalize DENIED then attempt ALLOWED via another command.  
Oracle: second -> DECISION_ALREADY_FINAL; DENIED produced no Rule.

### T-DECISION-ATOMICITY
Precondition: pending request.  
Operation: fail storage between ALLOWED request finalization and Rule/evidence/initial-justification creation.  
Oracle: no partial ALLOWED-without-corresponding Rule state observable; transaction rolls back or commits whole outcome.

## PolicyRule identity/evidence/justification

### T-RULE-UNIQUE-SUBJECT
Precondition: two distinct pending AccessRequests have identical AccessSubject but different current Needs.  
Operation: finalize both ALLOWED, including concurrent variant.  
Oracle: both responses reference the same PolicyRuleRef; exactly one Rule exists; two AuthorizationEvidence entries exist; both Need justifications are associated.

### T-RULE-DIFFERENT-SUBJECT
Precondition: requests differ in source Deployment, destination Deployment or InteractionRevision.  
Operation: finalize ALLOWED.  
Oracle: different AccessSubject yields different PolicyRuleRef.

### T-RULE-NO-NEED-IN-IDENTITY
Precondition: existing Rule subject S justified by N1.  
Operation: ALLOWED request with same S but N2.  
Oracle: same RuleRef; N2 association added; no duplicate Rule.

### T-RULE-ALLOWED-DOES-NOT-RESET-STATE
Precondition: existing Rule S is INACTIVE or has bounded effectiveWindow; new request for S becomes ALLOWED.  
Operation: finalize.  
Oracle: evidence/Need association append, but preexisting state/window remain unchanged.

### T-RULE-EVIDENCE-VERSION
Precondition: existing Rule S at version V; a distinct pending AccessRequest with the same AccessSubject becomes ALLOWED.  
Operation: finalize ALLOWED.  
Oracle: same RuleRef; new AuthorizationEvidence exists; Rule version becomes V+1 exactly once; operational state/window unchanged; no OPERATIONAL_CHANGED history row is added.

### T-RULE-EVIDENCE-RACE-MANAGE
Precondition: existing Rule at version V; one transaction finalizes another ALLOWED request for the same AccessSubject while another manager submits operational mutation with If-Match V.  
Operation: exercise both commit orderings.  
Oracle: Rule aggregate serialization prevents lost update. If evidence append wins first, manager gets STALE_VERSION; if manager wins first, ALLOWED append uses resulting state/window and advances the latest Rule version without resetting them.

### T-JUSTIFICATION-ATTACH
Precondition: Rule S exists; current Need N2 matches Rule Interaction.  
Operation: attach N2 with manage permission.  
Oracle: same Rule; N2 added exactly once with its participantComponentRef preserved; no AuthorizationEvidence added; effectState/window unchanged; Rule version increments for first association.

### T-JUSTIFICATION-MISMATCH
Precondition: current Need points to different Interaction.  
Operation: attach.  
Oracle: INTERACTION_MISMATCH/VALIDATION_REJECTED as canonical mapping; no association/version change.

### T-JUSTIFICATION-RETIRED
Precondition: Need retired before attachment snapshot.  
Operation: attach.  
Oracle: NEED_NOT_CURRENT; no association.

### T-NEED-RETIREMENT-RECONCILIATION
Precondition: Rule ACTIVE/unbounded, only justification N is current.  
Operation: retire N in Business Connectivity; read Rule/materialize later.  
Oracle: Access Policy rows untouched; Rule remains ACTIVE; Need reported RETIRED; reconciliationFlags contains NO_CURRENT_BUSINESS_JUSTIFICATION.

### T-MULTIPLE-JUSTIFICATIONS
Precondition: Rule with N1 and N2.  
Operation: retire N1 only.  
Oracle: one current Need remains; no NO_CURRENT_BUSINESS_JUSTIFICATION flag.

## Operational state/effective window

### T-RULE-EFFECT-STATE
Precondition: Rule ACTIVE/unbounded.  
Operation: INACTIVE then ACTIVE.  
Oracle: RuleRef/evidence/justifications unchanged; operational history records actual transitions; no new decision.

### T-RULE-OPERATIONAL-NOOP
Precondition: Rule has state/window X at version V.  
Operation: set X again.  
Oracle: 200; ETag/version/history unchanged.

### T-RULE-OPERATIONAL-HISTORY
Precondition: Rule is created ACTIVE/unbounded by decider D, then manager M sets INACTIVE/window W and later ACTIVE/window W2.  
Operation: GET /v1/policy-rules/{ruleRef}/history.  
Oracle: cursor-bounded ordered events include CREATED(D,time,ACTIVE/unbounded) then exact OPERATIONAL_CHANGED(M,...) events; no authorization token/request body is exposed; semantic no-op operations add no event.

### T-EFFECTIVE-WINDOW-BOUNDARIES
Precondition: ACTIVE Rule with [from, until).  
Operation: materialize at evaluation times before from, exactly from, immediately before until, exactly until.  
Oracle: non-effective before/from rules according to inclusive-lower/exclusive-upper semantics: effective at from, non-effective at until.

### T-EFFECTIVE-WINDOW-VALIDATION
Variants: from >= until, empty non-null window object.  
Oracle: INVALID_INPUT/VALIDATION_REJECTED; no mutation.

## Policy selection/materialization

### T-MATERIALIZE-ALL
Precondition: several current Rules.  
Operation: POST materialization with {}.  
Oracle: response selection is `{mode:"ALL",selectedRuleCount:<all current Rules>}`; one ruleProvenance record exists per selected Rule; effectiveness then applies.

### T-MATERIALIZE-SUBSET
Precondition: Rules R1/R2/R3.  
Operation: body {policyRuleRefs:[R1,R3]}.  
Oracle: selection is EXPLICIT with count 2; exactly R1/R3 have ruleProvenance and are evaluated; R2 is absent from ruleProvenance/nonEffective/rows/issues. No semantic selected-Rule count limit is asserted beyond configured request-body bytes.

### T-MATERIALIZE-SELECTION-INVALID
Variants: duplicate selected ref, unknown ref, explicit empty array.  
Oracle: duplicate/empty -> INVALID_INPUT; unknown -> REFERENCE_INVALID; no partial materialization result.

### T-MATERIALIZE-SUBSET-NO-DOMAIN-CAP
Precondition: configured request-body limit can hold an explicit selection larger than 200 unique RuleRefs.  
Operation: materialize that explicit subset.  
Oracle: request is not rejected because selected count exceeds 200; exact supplied Rules are selected. Only transport byte limit may reject the request.

### T-HTTP-BODY-LIMIT
Precondition: NAPMS_HTTP_MAX_REQUEST_BODY_BYTES = B.  
Operation: send a JSON body larger than B to a body-bearing route; separately send a valid body <= B.  
Oracle: oversized -> 413 PAYLOAD_TOO_LARGE before semantic mutation; within bound follows normal route semantics; no hidden body-size default.

### T-MATERIALIZE-COMPLETE
Precondition: one selected effective Rule; two source addresses, one destination, two traffic clauses.  
Operation: materialize.  
Oracle: HTTP 200 COMPLETE; exact Cartesian expansion and ports/address kinds; response contains one complete ruleProvenance entry with all AuthorizationEvidence and participant-attributed Need justifications/currentness/reconciliation; each technical row references PolicyRuleRef and carries addressEffectiveFrom/addressChangedBySubject; the response is explainable by a policy.export-only caller without policy.read; issues empty.

### T-MATERIALIZE-NON-EFFECTIVE
Precondition: selected Rule INACTIVE or ACTIVE outside window; technical address missing.  
Operation: materialize.  
Oracle: HTTP 200 COMPLETE if all other effective Rules resolve; Rule appears in nonEffective with correct reason; no realization issue/row for it.

### T-MATERIALIZE-NON-EFFECTIVE-PROVENANCE-MISSING
Precondition: selected Rule is INACTIVE or outside effectiveWindow, but one accepted AuthorizationEvidence/Need provenance reference required for its ruleProvenance cannot be resolved.  
Operation: materialize.  
Oracle: HTTP 200 UNRESOLVED + REFERENCE_UNRESOLVABLE for that Rule; non-effectiveness waives only technical realization, not provenance completeness.

### T-MATERIALIZE-NON-EFFECTIVE-TECHNICAL-MISSING
Precondition: selected Rule is INACTIVE or outside effectiveWindow; complete permission/business provenance resolves; Deployment/Resource/address technical realization is missing.  
Operation: materialize.  
Oracle: Rule remains nonEffective, no technical MaterializationIssue is produced for it, and this missing technical realization alone does not prevent COMPLETE.

### T-MATERIALIZE-UNRESOLVED
Precondition: selected effective Rule lacks source realization.  
Operation: materialize.  
Oracle: HTTP 200 UNRESOLVED; SOURCE_REALIZATION_MISSING for Rule; diagnostic rows not complete export.

### T-MATERIALIZE-NO-CURRENT-JUSTIFICATION
Precondition: effective Rule has only retired Needs and valid technical realization.  
Operation: materialize.  
Oracle: COMPLETE possible; rows carry NO_CURRENT_BUSINESS_JUSTIFICATION; absence of current Need is not MaterializationIssue.

### T-MATERIALIZE-REFERENCE-UNRESOLVABLE
Precondition: accepted referenced semantic fact cannot be resolved.  
Operation: materialize.  
Oracle: UNRESOLVED + REFERENCE_UNRESOLVABLE; no silent substitution.

### T-MATERIALIZE-DEPENDENCY-FAILURE
Precondition: DB/dependency prevents evaluation.  
Operation: materialize.  
Oracle: HTTP 503 DEPENDENCY_UNAVAILABLE; no COMPLETE/UNRESOLVED result.

### T-MATERIALIZE-PROVENANCE
Precondition: two independent Rules project technically equal effects.  
Operation: materialize.  
Oracle: independent Rule/evidence/justification provenance retained; no provenance-erasing merge.

### T-MATERIALIZE-SNAPSHOT
Precondition: read snapshot open; concurrent Resource address and Need retirement commit later.  
Operation: finish materialization.  
Oracle: Resource realization and Need currentness are from one coherent pre/post snapshot, never mixed.

## Idempotency / ETag

### T-IDEMPOTENCY-SAME-TARGET
For every Idempotent-create operation.  
Operation: same principal/method/route/target/key/body twice.  
Oracle: one mutation; second returns original semantic status/body/Location/ETag.

### T-IDEMPOTENCY-EXACT-REPLAY-BYTES
Precondition: idempotent command commits response R; later independent commands change the affected aggregate/current view.  
Operation: replay the original scoped key/fingerprint.  
Oracle: replay returns the originally persisted status/body/Location/ETag, not a reconstruction from current state; only X-Correlation-Id belongs to the retry request.

### T-IDEMPOTENCY-NO-TTL
Precondition: a committed idempotency record exists.  
Operation: advance test/application time far beyond ordinary retry horizons and replay.  
Oracle: selected MVP has no expiry/purge semantics; record remains replayable. A TTL implementation violates the accepted Data contract.

### T-IDEMPOTENCY-TARGET-SCOPE
Precondition: same principal/key/body shape against two different target Resources/Processes/Rules.  
Operation: execute both.  
Oracle: scopes are independent; no false conflict/replay across target ids.

### T-IDEMPOTENCY-CONFLICT
Operation: same scoped key with different accepted body.  
Oracle: 409 IDEMPOTENCY_CONFLICT; second mutation does not execute.

### T-IDEMPOTENCY-REPLAY-BEFORE-ETAG
Precondition: Idempotent-create + If-Match command commits using parent ETag V and returns new ETag V2, but client loses response.  
Operation: retry exact request with original If-Match V.  
Oracle: replay original committed result/ETag V2; no STALE_VERSION.

### T-IDEMPOTENCY-NEW-STALE
Precondition: no idempotency record for key K; supplied If-Match stale.  
Operation: NEW command.  
Oracle: 409 STALE_VERSION; no mutation/committed idempotency success.

### T-IDEMPOTENCY-CONCURRENT
Operation: two concurrent identical scoped requests.  
Oracle:
- at most one authoritative mutation;
- if first commits, waiter replays;
- if first rolls back, waiter becomes NEW and then applies normal If-Match;
- if resolution exceeds request/DB timeout, waiter gets 503 DEPENDENCY_UNAVAILABLE;
- never duplicate state and never IDEMPOTENCY_CONFLICT solely because identical command is in progress.

### T-JUSTIFICATION-NEED-LOCK-RACE
Precondition: current Need N; Rule R; Need retirement races justification attachment.  
Operation: exercise both lock orderings.  
Oracle follows the same winner semantics as request validation: retirement-first rejects, validation-lock-first lets attachment commit before retirement; no peer write by Access Policy.

## HTTP contract

### T-PROVENANCE-CONTRACT
Precondition: authenticated actors create/change Resource address, publish InteractionRevision, declare participant-attributed Needs and create multiple ALLOWED requests for one AccessSubject.  
Operation: read source facts and materialize using a principal with policy.export but without policy.read.  
Oracle:
- address fact exposes effectiveFrom/effectiveTo + changedBySubject;
- revision exposes createdAt + createdBySubject;
- Need exposes createdAt + createdBySubject + participantComponentRef;
- export ruleProvenance contains every AuthorizationEvidence including submittedBySubject/submittedAt/initialNeedRef + decision actor/time, and every associated Need with current/retired status/participant attribution/reconciliation;
- materialized row exposes addressEffectiveFrom + addressChangedBySubject and correlates through PolicyRuleRef;
- export remains explainable without separate policy.read calls;
- no untyped public `provenance` object/string is required or emitted.

### T-STRICT-JSON
Variants: unknown field, forbidden null, missing required field, server-owned actor/id/version/time.  
Oracle: exact validation failure before mutation.

### T-CORRELATION
Variants: absent/valid/invalid X-Correlation-Id.  
Oracle: generated/echoed/400 behavior; required events use effective id.

### T-ETAG-MATRIX
For every If-Match operation: missing/current/stale.  
Oracle: 428 / success / 409 using correct aggregate owner (Resource, Application, Interaction, BusinessProcess, AccessRequest, PolicyRule).

### T-PAGINATION-CONTRACT
For Resource endpoints/history, Application Components, Interaction revisions, Process Needs, Rule evidence/justifications/history:  
Precondition: more than one page of items.  
Operation: read with omitted limit, explicit valid limits, malformed cursor and cursor from another parent/query.  
Oracle:
- default page is at most 50, explicit 1–200 honored;
- nextCursor is opaque and forward traversal yields items without silent truncation for the tested stable dataset;
- malformed/cross-query cursor -> 400 INVALID_INPUT;
- parent current views expose counts rather than embedding the full growing collection;
- no cross-request snapshot guarantee is asserted.

### T-MATERIALIZE-BOUNDED-STREAM
Precondition: export large enough to require multiple internal chunks.  
Operation: materialize under instrumentation/fault-capable test adapter.  
Oracle: one logical snapshot/evaluationAt; output semantics equal small in-memory reference result; implementation does not require materializing all Rule/fact/row data at once; output row order is not used as an oracle.

### T-MATERIALIZE-EVALUATION-AT
Precondition: instrument the first statement of the materialization read-only REPEATABLE READ transaction and capture PostgreSQL transaction_timestamp().  
Operation: materialize Rules whose effective windows bracket that instant.  
Oracle: response evaluationAt equals that exact DB timestamp and effectiveness decisions use it; independently sampled application wall-clock time cannot change the outcome.

### T-MATERIALIZE-PREFLIGHT-DEPENDENCY-FAILURE
Precondition: a required DB/owner read fails during preflight after some earlier Rules were successfully inspected.  
Operation: materialize.  
Oracle: no HTTP 200 materialization body was committed; response is 503 DEPENDENCY_UNAVAILABLE (or 500 for accepted unexpected failure); no COMPLETE event.

### T-MATERIALIZE-POST-COMMIT-STREAM-FAILURE
Precondition: preflight succeeds and HTTP 200 streaming begins; inject client cancellation/transport failure during emit.  
Operation: continue materialization.  
Oracle: response body is incomplete/truncated and cannot parse as a valid complete export; no fabricated closing COMPLETE result and no policy.materialization.completed success event.

### T-PROBLEM-MAPPING
Trigger each stable failure.  
Oracle: exact status/code/correlationId; no secret/stack/schema.

## Security

### T-AUTH-MATRIX
For every operation matrix row: token without required permission, then exactly required permission.  
Oracle: first 403/no mutation; second normal semantic outcome; unrelated permission never implies it.

### T-AUTH-REPLAY
Precondition: original idempotent command was committed by principal P with permission; P's current token lacks required permission.  
Operation: retry same key/fingerprint.  
Oracle: current authorization fails 403 before replay result is disclosed.

### T-AUTH-TOKEN-INVALID
Missing/malformed/expired/wrong issuer/audience/invalid signature with usable key material.  
Oracle: 401 before application data access.

### T-AUTH-PERMISSION-CLAIM
Variants:
- permission claim absent;
- [] empty array;
- array containing required permission;
- duplicate permissions;
- unknown permission strings;
- scalar/string/object claim;
- array containing non-string element.

Oracle:
- absent/[] authenticate with empty set and protected operation returns 403;
- required exact string authorizes only its matrix operation;
- duplicates collapse;
- unknown values grant no known permission;
- wrong type/non-string element -> 401 invalid credential/token format.

### T-AUTH-ALGORITHM-AUDIENCE-TIME
Variants:
- configured allowed asymmetric algorithm with compatible JWKS key;
- token alg not in allow-list;
- alg=none;
- HS256;
- allowed alg with incompatible key type;
- aud exact string;
- aud array containing configured audience;
- missing/wrong-type/nonmatching aud;
- missing exp;
- exp just inside/outside configured skew;
- nbf just inside/outside configured skew;
- empty/missing sub;
- missing/wrong-type kid;
- unknown kid with successful refresh but key still absent;
- unknown kid with refresh dependency failure.

Oracle:
- only exact Security Architecture semantics validate;
- missing/wrong-type kid and successfully-refreshed-but-still-unknown kid -> 401;
- unknown kid whose validity cannot be established because refresh cannot complete -> 503;
- no JWT library default expands algorithm or time tolerance.

### T-OIDC-INITIAL-ACQUISITION
Precondition: valid startup config.  
Variants: metadata/JWKS available with usable allowed key; dependency unavailable/invalid through all configured attempts.  
Oracle: usable keys -> listener may start; failure -> runtime.startup.failed safe dependency category + non-zero exit before listener.

### T-OIDC-DISCOVERY-HTTPS-BOUNDARY
Variants:
- configured HTTPS issuer, discovery issuer exact match, HTTPS jwks_uri;
- configured HTTP issuer;
- discovery issuer mismatch;
- HTTP jwks_uri;
- HTTPS discovery/JWKS endpoint redirecting to HTTP.
Oracle: only the first satisfies production serve contract; every mismatch/downgrade fails safely. Test identity infrastructure uses HTTPS or a controlled adapter below the production HTTP transport boundary; production config is never relaxed.

### T-OIDC-SINGLE-FLIGHT-RECOVERY
Precondition: running process; cached key states varied.  
Variants:
- unknown kid causes concurrent protected requests;
- readiness and protected request trigger refresh concurrently;
- refresh fails while cached key is within max-stale;
- refresh fails after max-stale.
Oracle:
- one bounded in-flight refresh sequence is shared;
- usable cache permits validation/readiness when appropriate;
- beyond max-stale with failed refresh -> readiness DOWN and unverifiable protected token -> 503;
- no fetch storm/fail-open/false 401.

### T-AUTH-KEY-DEPENDENCY
Variants: valid cached key within max-stale; cache too old; unknown kid + failed bounded refresh.  
Oracle: usable cache may validate; inability to establish validity -> 503/readiness DOWN, never fail-open/false 401.

### T-ACTOR-SPOOF
Request contains actor/permission/server-owned provenance fields.  
Oracle: strict DTO rejects; trusted principal unchanged.

### T-FORWARDED-IDENTITY-IGNORED
Precondition: attacker supplies X-Forwarded-User, X-Remote-User and permission-like proxy headers with a missing or different bearer identity.  
Operation: protected request.  
Oracle: those headers never establish/override Principal or permissions; only validated bearer-token identity controls admission.

### T-PROBLEM-DISCLOSURE
Trigger validation/auth/dependency/unexpected failures with secret-like config.  
Oracle: no token/DSN/password/private stack in public result/allow-listed logs.

## Startup/operability

### T-CONFIG-REQUIRED
Remove/invalid each required NAPMS_* key.  
Oracle: startup fails before listener; safe startup event.

### T-CONFIG-UNKNOWN
Add unknown NAPMS_* key.  
Oracle: startup fails rather than ignore typo.

### T-CONFIG-PRECEDENCE
Attempt config file/CLI/runtime mutation.  
Oracle: no supported override/reload; RuntimeConfig immutable until restart.

### T-CONFIG-MODE-PROFILES
Variants:
- migrate mode with DB DSN + DB statement timeout only;
- serve mode missing a serve-required OIDC/listen/body-size key;
- either mode with unknown NAPMS_* key;
- mode argument plus attempted CLI configuration override.
Oracle: migrate accepts its minimal profile; serve rejects missing full config; unknown key fails both; mode selects process action only and no CLI argument overrides configuration values.

### T-MIGRATION-FRESH
Precondition: empty PostgreSQL database.  
Operation: run `napms migrate`, then `napms serve`.  
Oracle: migrate applies ordered ids/checksums and exits without listener; serve performs no DDL, verifies exact schema, initializes runtime and may open listener.

### T-MIGRATION-CONCURRENT
Precondition: empty or partially migrated database.  
Operation: run two migrate processes concurrently.  
Oracle: exclusive PostgreSQL advisory migration lock serializes them; each migration is applied at most once and both observe one valid final set.

### T-MIGRATION-CHECKSUM-STATE
Variants: changed checksum, unknown applied id, missing earlier expected id, pending expected migration on serve.  
Oracle: invalid historical state fails; serve refuses listener and never auto-repairs/applies pending DDL.

### T-MIGRATION-ROLLBACK
Precondition: inject failure inside one current migration transaction.  
Operation: run migrate.  
Oracle: that migration and its applied-id/checksum record roll back; prior fully committed migration set remains intact; process exits non-zero.

### T-OIDC-RETRY-BOUND
OIDC dependency fails.  
Oracle: attempts/backoff bounded by config.

### T-NO-MUTATION-RETRY
Inject transient DB/unknown commit.  
Oracle: application does not automatically replay mutation; client recovery is via idempotency.

### T-HEALTH
Healthy/DB down/usable cached key/unusable key.  
Oracle: live process-only; ready traffic capability; body UP/DOWN only.

### T-CANCELLATION
Slow DB/materialization.  
Operation: cancel/timeout.  
Oracle: work cancelled/bounded; no COMPLETE result/event.

### T-SHUTDOWN
In-flight request + SIGTERM.  
Oracle: ready DOWN first; stop new work; drain to grace then cancel; never claim rollback of committed state.

### T-DIAGNOSTIC-EVIDENCE
Trigger success/conflict/auth failure/decision/materialization/dependency/unexpected/shutdown.  
Oracle: required event fields exist, secrets/full request bodies absent.

## Property/state-machine obligations

- Resource address/Site/responsibility transitions preserve identity and valid non-overlapping history.
- Cross-Application Component pairs are treated identically to same-Application pairs except for their actual refs.
- Interaction revisions form immutable append-only semantics under Interaction version.
- AccessRequest permits PENDING -> ALLOWED or DENIED exactly once.
- Equal AccessSubject ALLOWED request sequences converge on one Rule and every newly appended AuthorizationEvidence advances whole-Rule version exactly once.
- AuthorizationEvidence and Need associations are append-only sets keyed by request/Need.
- PolicyRule ACTIVE <-> INACTIVE + effective-window changes preserve subject/evidence/justifications.
- Source/destination participant Needs remain independently attributed through request/Rule/materialization provenance.
- Arbitrary Need retirement sequences change only derived reconciliation status, not Rule permission/operational state.
- Arbitrary idempotency replay/conflict/concurrency sequences never create duplicate authoritative entities.
- Growing collection cardinality does not change parent DTO shape or bypass pagination contracts.
