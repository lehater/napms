# Backend cross-cutting applicability coverage

Status: ACCEPTED candidate

This document is an analysis view, not a second owner of the referenced decisions.

| Concern | State | Owner/result |
| --- | --- | --- |
| Failure/error semantics | COVERED | Application Design + API Contract distinguish validation, auth, conflict, unresolved, dependency and internal failure. |
| Concurrency | COVERED | Quality/Data: optimistic aggregate versions; snapshot-consistent validation/materialization. |
| Transactions | COVERED | Data/System: one semantic owner written per transaction; decision+rule atomic; shared peer reads allowed. |
| Consistency | COVERED | Strong owner writes; coherent current read snapshot for materialization; no silent rebinding. |
| Idempotency | COVERED | Data/API for duplicate-sensitive external mutations and final decision handling. |
| Time semantics | COVERED | Server-owned current evaluationAt; Resource history intervals; no historical policy export. |
| Configuration | COVERED | Operability: typed startup config, explicit failure, secret-capable sources. |
| Logging/diagnostics | COVERED | Operability allow-listed structured evidence; domain history remains authoritative. |
| Metrics/tracing | COVERED | Required diagnostic metrics/correlation; backend technology remains free. |
| Health/readiness | COVERED | Liveness independent; readiness checks DB/config/OIDC key material. |
| Retries/timeouts/cancellation | COVERED | Operability/Quality explicit retry/idempotency and cancellation rules. |
| Reliability/resilience | COVERED for MVP semantics | Explicit dependency/unavailable/unknown-commit behavior; no HA/SLA claim. |
| Performance/capacity | DEFERRED_NONBLOCKING | No numeric source targets. Bounded pagination/queries required; reopen on concrete load/SLO. |
| Recovery/backup/continuity | DEFERRED_NONBLOCKING for code closure | Authoritative state is identified, but no RPO/RTO exists. Must resolve before production continuity claims. |
| Data provenance | COVERED | Need/decision/rule/revision/realization provenance carried into materialization. |
| Data lifecycle/governance | COVERED/DEFERRED | Required domain histories retained; no external privacy/retention obligation supplied. Reopen on applicable obligation. |
| Migrations | COVERED for greenfield | Ordered versioned migrations; destructive future change requires Change Transition Design. |
| Change/transition design | NOT_APPLICABLE | Blind experiment defines a greenfield target, not migration from old NAPMS. Adoption is post-freeze work. |
| External service dependencies | COVERED | OIDC and database trust/failure contracts defined; concrete library acquisition verified downstream. |
| External normative obligations | NOT_APPLICABLE from source corpus | No law/regulation/contract/org mandate was supplied as applicable source input. |
| Asynchronous messaging | NOT_APPLICABLE | No accepted behavior requires async completion/eventual consistency. |
| Internationalization/localization | NOT_APPLICABLE to backend semantics | No locale-sensitive domain behavior or human-formatted backend output requirement. |
| Provider/network device integration | NOT_APPLICABLE | Explicit MVP non-goal. |
| Brownfield evidence/reconciliation/remediation | NOT_APPLICABLE to selected MVP | Retained as future problem-space evidence, not current capability. |
| Business criticality/impact scoring | DEFERRED_NONBLOCKING | Source says useful but model/propagation unresolved; current policy-export MVP does not consume it. |

No omission in this table should be interpreted as a new requirement; every state is derived from accepted scope or an explicit reopening condition.
