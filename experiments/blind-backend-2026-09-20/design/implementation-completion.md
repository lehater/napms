# Backend implementation completion criteria

Status: ACCEPTED after Coding-Agent Challenge 07 repair

Depends on: Implementation Design, Verification Strategy and Test Design.

IMPLEMENTATION may claim realization complete only when every item below has executable evidence.

1. **External contract** — every accepted HTTP route, DTO, status, Problem code, Location, ETag, correlation, Idempotency-Key and configured request-body-size rule exists exactly as Interface Design states; every ordinary growing collection is cursor-paged and parent views contain counts rather than unbounded children.

2. **Source/domain validity** — cross-Application Interaction is accepted when Component/traffic semantics are valid; no blanket same-Application invariant exists in domain/API/schema.

3. **Aggregate concurrency** — Resource, Application, Interaction, BusinessProcess, AccessRequest and PolicyRule own exactly their declared versions; child entities cannot invent competing optimistic-concurrency semantics.

4. **Transaction consistency** — ordinary owner writes are PostgreSQL READ COMMITTED; request/justification current-Need validation uses owner-side FOR SHARE-equivalent lock held through Access Policy commit without peer writes; composed multi-owner reads/materialization use read-only REPEATABLE READ.

5. **Resource truth/history** — immutable AuthorityScopeRef, explicit same-logical-unit Endpoint membership with no automatic grouping, current address/Site/singular OWNER/singular ADMINISTRATOR and required history are preserved, including explicit actor/time provenance and replacement/no-op behavior.

6. **Current-access identity** — exactly one PolicyRule exists per AccessSubject(source Deployment, destination Deployment, exact InteractionRevision); NeedRef and technical realization are not Rule identity.

7. **Permission evidence/version** — ALLOWED finalization is atomic with Rule resolve/create, AuthorizationEvidence and initial Need justification; DENIED creates no Rule/evidence; equal concurrent subjects converge on one Rule; each new AuthorizationEvidence on an existing Rule advances whole-Rule version exactly once without operational-history entry or state/window reset.

8. **Business justification** — BusinessProcess preserves optional opaque criticalityLabel without score/order/propagation; ConnectivityNeed preserves participantComponentRef; source/destination Needs remain independently attributable; additional current matching Need can attach without new permission evidence/duplicate Rule; currentness remains Business Connectivity truth; later retirement changes derived status only.

9. **Reconciliation** — zero current Need yields NO_CURRENT_BUSINESS_JUSTIFICATION and does not automatically revoke/deactivate Rule or make materialization incomplete.

10. **Operational effectiveness/audit** — first Rule is ACTIVE/unbounded; ACTIVE/INACTIVE and absolute [effectiveFrom,effectiveUntil) preserve Rule/permission identity; same operational values are no-op; policy.read history exposes CREATED/OPERATIONAL_CHANGED actor/time/state/window and excludes no-op/evidence-only/justification-only entries.

11. **Selection/materialization** — ALL or explicit unique non-empty PolicyRule subset is supported with no semantic Rule-count cap; explicit selection is bounded only by configured HTTP request-body bytes. Every selected Rule must have complete permission/business provenance; only selected effective Rules additionally impose technical-realization completeness.

12. **Materialization reliability** — the first statement of one read-only REPEATABLE READ transaction establishes the snapshot and returns PostgreSQL transaction_timestamp() as exact evaluationAt; bounded preflight determines COMPLETE/UNRESOLVED and dependency success before HTTP 200 commitment; emit repeats bounded traversal in that same snapshot; post-commit stream failure cannot become a valid successful export.

13. **Self-contained explainability** — AccessRequest/AuthorizationEvidence preserve request authority scope/time; export contains ExportAuthorityEvidence for every selected Resource scope plus one complete MaterializedRuleProvenance per selected Rule with all authorization evidence, participant-attributed Need justifications/currentness and reconciliation; normalized rows correlate by PolicyRuleRef and preserve exact traffic + explicit technical actor/time facts. A policy.export-only caller can explain the export without requiring policy.read.

14. **Idempotency/concurrency recovery** — concrete target is part of idempotency scope; exact persisted original response JSON/status/Location/ETag replay precedes NEW-command If-Match and is never reconstructed from current state; committed replay records have no selected-MVP TTL; different fingerprint conflicts; different targets do not collide; concurrent identical command resolves commit->replay, rollback->NEW, unresolved bounded wait/DB failure->503; no automatic DB mutation retry.

15. **Persistence ownership** — schema/migrations match Data Design: no cross-owner write coupling/FKs, no false interaction.application_ref, unique AccessSubject Rule, evidence/justification uniqueness, explicit histories and owner-local constraints.

16. **Security** — OIDC HTTPS-only configured issuer/discovery/jwks_uri with downgrade rejection, configured asymmetric algorithm allow-list/key compatibility, required kid, exact issuer/audience/exp/nbf/skew/sub/permission-claim/authority-claim semantics; request/export require effective grants for every relevant AuthorityScopeRef at server-owned time and preserve evidence; deterministic full-refresh attempt semantics and >0 max-stale age measured from last successful full refresh are proven; provider cache headers cannot extend that window; 401-vs-503 distinction is proven; request/decide/manage/read/export remain separate and forwarded identity/permission headers cannot establish authority; secret/log/error rules hold.

17. **Operability** — startup-only configuration including body-size bound, unknown-key failure, no hidden required defaults, OIDC retry/cache policy, DB/lock waits, diagnostic evidence, health/readiness, cancellation, materialization commit boundary, graceful shutdown and redaction are proven.

18. **Architecture/components** — dependency checks prove domain independence from adapters, API independence from concrete repositories, Interaction independence from Application write ownership, Access Policy non-ownership of Need currentness and read-only Policy Materialization.

19. **Executable verification** — every accepted Test Design contract has evidence at its required domain/application/PostgreSQL/API/security/operability level.

20. **Fresh start/no redesign** — empty PostgreSQL -> `napms migrate` -> `napms serve` -> complete public-HTTP journey succeeds without manual state fabrication, and code/tests introduce no new product/domain/architecture/interface/data/security/operability/verification semantic convention absent from accepted closure.

Any failure remains implementation/evidence work unless it exposes a genuine upstream semantic gap; such a gap reopens its owning Authority and invalidates IMPLEMENTATION COMPLETE.
