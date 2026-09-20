# Backend cross-cutting applicability coverage

Status: ACCEPTED after Source Corpus amendments 01–02

This is an analysis view, not a second owner of decisions.

| Concern | State | Owner/result |
| --- | --- | --- |
| Failure/error semantics | COVERED | Application + Interface distinguish validation/auth/conflict, normal UNRESOLVED materialization, preflight dependency/internal failure before HTTP commit, and incomplete post-commit transport stream. |
| Concurrency | COVERED | Aggregate versions: Resource, Application, Interaction, BusinessProcess, AccessRequest, PolicyRule. Child objects cannot invent competing version semantics. |
| Transactions | COVERED | One semantic owner written per transaction; ALLOWED request finalization + Rule/evidence/initial justification atomic; shared peer reads permitted. |
| Consistency | COVERED | Strong owner writes; request/attachment validation and materialization use coherent DB snapshots; no silent rebinding. |
| Idempotency | COVERED | Target-scoped key/fingerprint, exact persisted original response replay before NEW-If-Match, no MVP TTL, atomic result recording, concurrent commit/rollback/503 resolution. |
| Time semantics | COVERED | Resource temporal history; materialization evaluationAt is PostgreSQL transaction_timestamp() from the exact REPEATABLE READ snapshot; PolicyRule absolute [effectiveFrom,effectiveUntil) window; OIDC exp/nbf use configured skew; no historical export API. |
| Current-access identity | COVERED | Access Policy: one Rule per source Deployment + destination Deployment + exact InteractionRevision; Need/address excluded. |
| Permission evidence | COVERED | Append-only ALLOWED AccessRequest evidence; multiple decisions for same semantic access may support one Rule. |
| Business justification | COVERED | Need includes participantComponentRef for independent source/destination attribution; associations append-only; currentness owned by Business Connectivity; zero-current justification becomes reconciliation flag, not revocation. |
| Cross-Application communication | COVERED | Application Communication: Interaction is an independent aggregate and may reference Components from different Applications. |
| Configuration | COVERED | Operability startup-only environment contract, validation, unknown-key failure, no runtime reload. |
| Logging/diagnostics | COVERED | Operability allow-listed structured evidence; PolicyRule operational history is authoritative business audit and separately queryable; logs are not. |
| Metrics/tracing | COVERED | Required dimensions/correlation; concrete telemetry library/exporter free. |
| Health/readiness | COVERED | Liveness process-only; readiness DB + usable OIDC validation material. |
| Retries/timeouts/cancellation | COVERED | No automatic DB mutation retry; bounded OIDC fetch; request cancellation and timeout propagate. |
| Reliability/resilience | COVERED for MVP semantics | Explicit dependency unavailable/unknown-commit/replay behavior; no HA/SLA claim. |
| Performance/capacity | DEFERRED_NONBLOCKING | No numeric source targets; bounded request timeout/history page size. |
| Recovery/backup/continuity | DEFERRED_NONBLOCKING for code closure | Authoritative state identified but no accepted RPO/RTO. Required before production continuity claims. |
| Data provenance | COVERED | Rule, all authorization evidence, Need participant attribution/currentness, revision/deployment/resource/endpoint facts carried to materialization. |
| Data lifecycle/governance | COVERED/DEFERRED | Accepted histories retained; no external privacy/retention obligation supplied. |
| Migrations | COVERED for greenfield | Ordered immutable versioned migrations; destructive future change reopens transition design. |
| Change/transition design | NOT_APPLICABLE | Blind target is greenfield; migration from old NAPMS is post-freeze. |
| External service dependencies | COVERED | OIDC and PostgreSQL trust/failure/cache/timeout contracts defined. |
| External normative obligations | NOT_APPLICABLE from source corpus | No law/regulation/contract/org mandate supplied as applicable input. |
| Asynchronous messaging | NOT_APPLICABLE | No accepted behavior requires async completion/eventual consistency. |
| Internationalization/localization | NOT_APPLICABLE to backend semantics | No locale-sensitive behavior/output requirement. |
| Provider/network device integration | NOT_APPLICABLE | Explicit MVP non-goal. |
| Brownfield evidence/reconciliation/remediation | PARTIALLY NOT_APPLICABLE | Device/config reconciliation excluded; only source-required NO_CURRENT_BUSINESS_JUSTIFICATION condition is represented. |
| Business criticality/impact scoring | DEFERRED_NONBLOCKING | Source says potentially useful but representation/propagation unresolved and current export does not consume it. |
| Recurring/periodic schedule language | DEFERRED_NONBLOCKING | Source requires supported declarative effective condition; MVP closes this with absolute effective window only. Recurrence reopens Product Requirements when concrete semantics are required. |
| Authorization scope granularity | COVERED for selected MVP / reopenable | Security treats current backend instance as the authorization scope; token validity supplies action time. Narrower tenant/resource/application scope requires new Product/Security input. |

No row creates a new requirement. Every state traces to accepted scope/design or a stated reopening condition.
