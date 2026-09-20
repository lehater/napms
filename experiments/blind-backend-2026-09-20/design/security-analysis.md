# Backend security analysis

Status: ACCEPTED after Coding-Agent Challenge 02 repairs

Scope: selected blind backend MVP. This analysis reviews accepted design and routes gaps; it does not invent entitlement/business permission semantics.

## Trust boundaries

1. Untrusted caller -> HTTPS API.
2. API/runtime -> configured OIDC issuer/JWKS.
3. Application/persistence adapters -> PostgreSQL.
4. Runtime -> startup environment/secret injection.
5. Internal module ownership boundaries inside one process/database.

## Threat/control coverage

| Concern | State | Accepted control |
| --- | --- | --- |
| Forged/expired/wrong issuer/audience/signature token | COVERED | Exact configured asymmetric alg allow-list/key compatibility, issuer/audience, required exp/optional nbf with explicit skew, non-empty sub; fail closed. |
| OIDC key dependency unavailable is misreported as invalid user | COVERED | Invalid token with established key -> 401; inability to establish validity -> 503. |
| OIDC discovery/JWKS transport downgrade or issuer substitution | COVERED | Serve requires HTTPS issuer; discovery issuer exact-match; jwks_uri HTTPS-only; non-HTTPS redirects rejected. |
| JWT algorithm confusion / unsafe library default | COVERED | none/HS*/unknown/unconfigured algorithms rejected; token alg must match configured asymmetric allow-list and JWKS key type. |
| Cold-start or unready key-cache recovery deadlock/fetch storm | COVERED | Initial validation-material acquisition gates listener; runtime readiness/protected validation share one bounded single-flight refresh; age is measured from last successful full refresh, >0 max-stale is authoritative, and provider cache headers cannot extend it. |
| Caller spoofs actor/permissions/scoped authority | COVERED | Principal, instance permissions and AuthorityGrants only from validated bearer token claims; body/query/forwarded headers cannot override them. |
| Permission claim missing/wrong type interpreted inconsistently | COVERED | Missing claim = empty permission set; present claim must be array<string>; wrong type/non-string = invalid credential; unknown values grant nothing. |
| Unauthorized read/mutation/export/decision | COVERED | Exact operation admission matrix; request/export require all relevant effective scope grants at server-owned time; no implication. |
| Request authority confused with permission decision | COVERED | scoped `access.request` authority and instance `access.decide` permission are independent; request authority evidence is preserved. |
| Business Need grants permission | COVERED | Need required as justification for request/attachment but never creates permission/Rule without ALLOWED evidence. |
| Resource Owner/Admin or Process organization grants app authorization | COVERED | Explicitly forbidden by Product/Security contracts. |
| Unauthorized Rule operational/effective-window change | COVERED | `access.manage` + PolicyRule If-Match. |
| Unauthorized justification attachment | COVERED | `access.manage` + current matching Need validation + Rule If-Match/idempotency. |
| Retired/mismatched/foreign-participant Need attached | COVERED | Same-snapshot Need currentness + Interaction match + participantComponentRef membership before association. |
| Need retirement silently revokes or silently remains “current” | COVERED | Currentness owned/read from Business Connectivity; Access Policy stores only association; zero-current Need is reconciliation flag, not auth mutation. |
| Duplicate PolicyRule through concurrent ALLOWED requests | COVERED | Unique AccessSubject + atomic resolve/create; evidence/association append in same transaction. |
| Duplicate AuthorizationEvidence | COVERED | AccessRequestRef unique evidence constraint. |
| Duplicate Need association | COVERED | RuleRef+NeedRef uniqueness. |
| Decision tampering/finality replay | COVERED | Request finalization once, authenticated decider, immutable evidence, idempotency/finality conflict. |
| Idempotency key collision across different target entities | COVERED | Scope includes principal + method + route + normalized path target + key. |
| Retry after successful mutation falsely fails stale ETag | COVERED | Same-fingerprint committed replay is resolved before NEW-command If-Match evaluation. |
| Different body reuses idempotency key | COVERED | Canonical request fingerprint -> 409 conflict. |
| Unknown commit/retry duplicates state | COVERED | Idempotency state commits atomically; unknown never fabricates success; no automatic mutation retry. |
| Lost update on aggregate/child | COVERED | Owner aggregate ETag/version; no child version bypass. |
| Cross-context Need race at request/attach | COVERED | Validation read + Access Policy write share one DB snapshot. |
| Export subset probes unauthorized data | COVERED | selected Rules' Resource scopes are resolved internally; effective `policy.export` grant is required for every selected scope at evaluationAt before result/rows are exposed. |
| Inactive/out-of-window Rule leaks technical realization unnecessarily | COVERED | Materializer evaluates effectiveness before technical realization and does not need peer technical facts for non-effective Rule. |
| SQL injection | COVERED | Bound parameters + strict structured value normalization. |
| Mass assignment | COVERED | Explicit DTO/command mapping; server-owned fields rejected. |
| Token/secret/DSN disclosure | COVERED | Allow-listed diagnostics, secret redaction, no token persistence. |
| Internal stack/schema disclosure | COVERED | Stable Problem contract; stack only protected internal log. |
| Insecure transport | COVERED | External HTTPS terminates at trusted deployment ingress; internal plaintext listener is deployment-private and never directly exposed to untrusted network. |
| Request-controlled issuer/JWKS/URL SSRF | COVERED/NOT_APPLICABLE | OIDC source is startup config, not request input; no caller-provided URL fetch operation. |
| CSRF | NOT_APPLICABLE | Bearer Authorization header, no ambient cookie/session auth. Reopen if browser cookie auth appears. |
| CORS | DEFERRED_NONBLOCKING | Frontend/browser deployment excluded; resolve before cross-origin browser exposure. |
| Rate limiting/abuse quotas | DEFERRED_NONBLOCKING | No public-internet/capacity target; bounded timeout/pagination constrain accidental amplification. |
| Resource/domain-policy authorization scope | COVERED | Resource owns immutable AuthorityScopeRef; request/export admission checks exact action/scope/time grants; Site/responsibility/Process metadata never manufacture scope. |
| Encryption at rest/key rotation | DEFERRED_NONBLOCKING | No supplied regulatory/sensitivity obligation beyond ordinary deployment confidentiality. |
| Supply-chain compromise | DEFERRED to implementation verification | Pin/reproduce/check selected dependencies in CI; package identity is not domain truth. |
| Provider/device credentials | NOT_APPLICABLE | Rendering/execution outside MVP. |

## Security invariants for implementation

- authentication runs before any application-data operation;
- authorization runs before semantic mutation/read/export;
- idempotency replay never bypasses authorization for the current caller;
- replay returns prior semantic response but uses the current correlation id;
- If-Match bypass is permitted only for an authenticated/authorized exact idempotent replay of the same committed command;
- a new idempotency command cannot bypass stale-version checks;
- AccessSubject equality is exact opaque-ref equality; no attacker-controlled normalization can merge distinct IDs;
- attaching justification does not add AuthorizationEvidence or change operational state; participantComponentRef is read from trusted Business Connectivity Need, never supplied as a Rule-side override;
- Rule reads/materialization resolve Need currentness through Business Connectivity rather than trusting copied status;
- zero current Need never implies automatic permission/revocation behavior;
- no permission is inferred from Resource ownership, Process organization, Need existence, ALLOWED evidence from a different AccessSubject, or technical address equality.

## Verification obligations

- invalid credential variants -> 401, including malformed permission-claim type/non-string elements; missing permission claim yields authenticated empty permissions; unavailable validation key material -> 503;
- exact instance-permission + scoped-authority matrix, including request and subset/ALL export scope/time coverage;
- caller-supplied actor/permission/server-owned fields rejected;
- request vs decide vs manage vs read/export independence;
- concurrent ALLOWED requests converge on one Rule;
- duplicate evidence/justification cannot be created;
- retired/mismatched Need or Need whose participantComponentRef is not an Interaction participant cannot be newly attached;
- Need retirement is reflected on subsequent read/materialization without Access Policy mutation;
- same-target same-key replay succeeds before stale ETag; different target with same key is independent; different fingerprint conflicts;
- no mutation retry after unknown DB outcome;
- secrets/tokens absent from Problem/log samples;
- hostile strings never alter SQL query shape;
- inactive/out-of-window selected Rule does not require/expose current technical realization in output rows;
- PolicyRule operational history requires policy.read and reveals only accepted business-audit fields, not tokens/secrets.

Blocking security Questions: none for the current MVP as presently scoped. Deferred concerns have explicit reopen conditions.
