# Backend executable test design

Status: ACCEPTED candidate

Framework and fixture mechanics are intentionally unspecified. Each contract defines precondition → operation → observable oracle.

## Domain contracts

### T-RES-IDENTITY
Precondition: Resource R/Endpoint E has address A1.  
Operation: change E to valid address A2.  
Oracle: ResourceRef and EndpointRef unchanged; current is A2; history still exposes A1 with a closed validity interval.  
Forbidden oracle: table primary-key layout.

### T-RES-MISSING
Precondition: Resource/Endpoint exists without address.  
Operation: read current Resource.  
Oracle: endpoint exists with explicit no-current-address state; it is not omitted and not represented as 0.0.0.0/0.

### T-TRAFFIC-REVISION
Precondition: Interaction I has published revision V1.  
Operation: attempt to change V1 traffic meaning, then publish changed meaning.  
Oracle: V1 remains unchanged; changed meaning receives distinct V2; unsupported protocol-specific semantics are rejected rather than widened.

### T-NEED-NOT-PERMISSION
Precondition: active Need N exists.  
Operation: read/submit no permission decision.  
Oracle: no PolicyRule exists merely because N exists.

### T-DECISION-FINALITY
Precondition: pending AccessRequest A.  
Operations: record DENIED then attempt ALLOWED; separately record ALLOWED then repeat same ALLOWED.  
Oracle: conflicting second final decision is rejected; same accepted decision replay is idempotent; DENIED has no Rule; ALLOWED has one stable RuleRef.

### T-RULE-EFFECT-STATE
Precondition: ALLOWED rule R is ACTIVE.  
Operation: set INACTIVE then ACTIVE.  
Oracle: RuleRef/request/decision provenance unchanged; materialization includes R only while ACTIVE.

## Cross-owner application contracts

### T-REQUEST-DIRECTION
Precondition: revision V says Component C1 -> C2; deployments D1(C1), D2(C2); active Need N(I).  
Operation: submit D2 -> D1 with V/N.  
Oracle: INTERACTION_MISMATCH; no AccessRequest committed.

### T-REQUEST-NEED-CURRENT
Precondition: Need N retired before submission transaction snapshot.  
Operation: submit otherwise valid request.  
Oracle: NEED_NOT_CURRENT; no AccessRequest.

### T-REQUEST-SNAPSHOT-RACE
Precondition: N active; concurrent retirement and request submission are coordinated around transaction start.  
Operation: execute both orders.  
Oracle: request validity corresponds to N state in the submission transaction snapshot; no mixed/undefined outcome.

### T-MATERIALIZE-COMPLETE
Precondition: one ACTIVE Rule, exact revision, two source endpoints, one destination endpoint, two TrafficClauses.  
Operation: materialize current policy.  
Oracle: COMPLETE with exact Cartesian expansion required by endpoint × clause semantics, no broadened ports, each row carries the same Rule/Need/decision/revision provenance.

### T-MATERIALIZE-UNRESOLVED
Precondition: two ACTIVE Rules; one lacks any current source address.  
Operation: materialize.  
Oracle: overall UNRESOLVED; issue identifies affected Rule; any diagnostic rows are explicitly non-complete.

### T-MATERIALIZE-INDEPENDENT-PROVENANCE
Precondition: two different Rules produce technically equal address/protocol/port effects.  
Operation: materialize.  
Oracle: results retain two independent provenance chains; implementation cannot merge them into one provenance-less effect.

### T-MATERIALIZE-SNAPSHOT
Precondition: materialization transaction open; concurrent address change commits after its snapshot.  
Operation: finish materialization.  
Oracle: output reflects one coherent pre-change or post-change snapshot according to transaction ordering, never source from one snapshot and destination from another.

## Persistence/atomicity contracts

### T-STALE-WRITE
Precondition: two readers hold aggregate version V.  
Operation: first commits V+1; second writes with V.  
Oracle: second gets STALE_VERSION and overwrites nothing.

### T-IDEMPOTENCY
Precondition: no prior key K.  
Operation: send duplicate-sensitive create with K/payload P twice, then K/payload Q.  
Oracle: first/second return same committed semantic result; third is IDEMPOTENCY_CONFLICT; only one authoritative creation exists.

### T-DECISION-ATOMICITY
Precondition: pending request.  
Operation: inject storage failure between decision persistence and Rule insert.  
Oracle: transaction rolls back both; retry can reach one valid final outcome. No decided-without-rule ALLOWED state is observable.

### T-MIGRATION-FRESH
Precondition: empty supported PostgreSQL database.  
Operation: apply ordered migrations once, then normal startup.  
Oracle: schema ready with no manual seed required for structural correctness; second migration check does not reapply applied versions.

## API/security contracts

### T-AUTH-MATRIX
For every row of the Security Architecture operation matrix:  
Precondition: valid token without required permission, then with exactly required permission.  
Operation: call operation with otherwise valid request.  
Oracle: first FORBIDDEN/no mutation; second proceeds to normal domain outcome. Extra unrelated permission does not satisfy requirement.

### T-AUTH-TOKEN-VALIDATION
Precondition variants: missing, malformed, expired, wrong issuer, wrong audience, invalid signature.  
Operation: call protected read.  
Oracle: authentication failure before application data access.

### T-ACTOR-SPOOF
Precondition: valid principal P; body/header includes another actor identity.  
Operation: protected mutation.  
Oracle: provenance uses P; spoof field rejected/ignored according to DTO contract and never becomes trusted actor.

### T-PROBLEM-DISCLOSURE
Precondition: trigger validation, forbidden, dependency and unexpected failures with secret-like config/token values present in runtime.  
Operation: inspect HTTP problem + captured structured logs.  
Oracle: stable public code/correlationId; no token/password/connection secret; stack only protected internal log for unexpected failure.

### T-ETAG
Precondition: mutable aggregate current ETag V.  
Operation: update with V then repeat with stale V.  
Oracle: first succeeds/returns new ETag; second 409 STALE_VERSION.

## Operability contracts

### T-HEALTH
Precondition variants: healthy; DB unavailable; OIDC key material unavailable.  
Operation: live + ready probes.  
Oracle: live remains healthy while process can execute; ready fails when required dependency/config cannot support traffic; neither response exposes secret/detail.

### T-CANCELLATION
Precondition: intentionally slow materialization read.  
Operation: cancel request.  
Oracle: database/read work is cancelled/bounded; no COMPLETE response/event is emitted.

## Property/state-machine obligations

- generated valid address changes preserve Resource/Endpoint identity and non-overlapping history;
- generated port ranges either normalize to exactly equivalent semantics or reject invalid overlap/range bounds—never widen silently;
- AccessRequest state machine permits PENDING -> ALLOWED or PENDING -> DENIED exactly once;
- PolicyRule state machine permits ACTIVE <-> INACTIVE while all immutable provenance fields remain constant;
- arbitrary sequences of idempotent replay/conflicting replay never create duplicate authoritative entities.

Test implementation may use examples, property generators or state-machine frameworks; the observable contracts above are normative, not a specific framework.
