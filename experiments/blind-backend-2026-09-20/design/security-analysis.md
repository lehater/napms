# Backend security analysis

Status: ACCEPTED candidate

Scope: selected blind backend MVP. This analysis reviews accepted design; it does not introduce product entitlement semantics.

## Trust boundaries

1. Untrusted API caller -> HTTPS API.
2. API/runtime -> configured OIDC issuer/JWKS.
3. Application/persistence adapters -> relational database.
4. Runtime -> secret/configuration source.
5. Internal module boundaries are ownership boundaries but not separate network trust zones in the modular monolith.

## Threat/control coverage

| Concern | State | Owning accepted control / rationale |
| --- | --- | --- |
| Forged/expired/wrong-audience bearer token | COVERED | Security Architecture requires signature, issuer, audience, exp/nbf validation against fixed configured issuer. |
| Caller spoofs actor/permission in payload | COVERED | Principal/permissions come only from validated token; API fields cannot override them. |
| Unauthorized mutation/export/decision | COVERED | Explicit permission per protected operation; fail closed on missing/unknown. |
| Request authority confused with allow decision | COVERED | Separate access.request and access.decide permissions plus domain decision separation. |
| Resource Owner/Admin treated as security authority | COVERED | Domain and Security contracts explicitly prohibit this inference. |
| Decision tampering/replay | COVERED | Final decision immutable per request; authenticated deciding principal/provenance; idempotency/finality conflict. |
| Duplicate create/unknown retry creates extra semantic state | COVERED | Idempotency-Key contract + transactionally stored idempotency result for material creates. |
| Concurrent lost update | COVERED | ETag/version optimistic concurrency and stale-write conflict. |
| Cross-context race lets retired Need validate incorrectly | COVERED | Submission validation reads and Access Policy write share one database transaction snapshot; accepted submission currentness is defined on that snapshot. |
| SQL/injection through input | COVERED | Engineering Policy mandates bound parameters; API/domain validation normalizes structured values. |
| Mass assignment/internal-field mutation | COVERED | Explicit DTO-to-command mapping; domain models are not deserialized directly. |
| Secret/token disclosure in logs/errors | COVERED | Allow-listed diagnostic fields, redaction, token non-persistence. |
| Sensitive internal stack/schema disclosure | COVERED | Stable external error model; stacks only protected server logs. |
| Insecure transport | COVERED | HTTPS mandatory outside loopback/dev. |
| JWT key/issuer substitution through request data | COVERED | issuer/audience/JWKS source is startup configuration, not request-controlled. |
| SSRF | NOT_APPLICABLE | No accepted operation fetches caller-provided URLs or arbitrary network destinations. Reopen if external source connectors are added. |
| CSRF on protected mutations | NOT_APPLICABLE for current contract | Auth is bearer Authorization header, not ambient cookie authority. Reopen if browser cookie/session auth is introduced. |
| CORS/browser-origin policy | DEFERRED_NONBLOCKING | Frontend/browser design is outside this experiment. Must be resolved before exposing browser deployment if origins require policy. |
| Rate limiting/abuse quotas | DEFERRED_NONBLOCKING | No accepted public-internet/capacity target. Bounded pagination/timeouts limit accidental amplification; reopen for hostile/public exposure. |
| Per-Resource/Application authorization scopes | DEFERRED_NONBLOCKING | Current Security Architecture intentionally defines instance-wide permissions because no accepted product input requires narrower scopes. Reopen on tenant/customer/scoped-authority requirement. |
| Encryption at rest/key rotation | DEFERRED_NONBLOCKING | No regulated/sensitivity requirement beyond ordinary infrastructure confidentiality. Deployment may provide it; reopen on external obligation/threat requirement. |
| Supply-chain compromise | DEFERRED_NONBLOCKING to dependency verification | Dependency selection must be pinned/reproducible and checked by implementation/CI, but no package inventory is semantic design truth. |
| Network-provider/device credential risk | NOT_APPLICABLE | Provider/device rendering/mutation is outside MVP. |

## Security verification obligations

- reject missing, malformed, expired, wrong-issuer and wrong-audience tokens;
- reject every protected operation without its required permission;
- prove request and decide permissions are independent;
- prove responsibility/business fields never grant authorization;
- prove decision finality/idempotent repeat/conflicting repeat;
- prove Idempotency-Key same-input replay vs different-input conflict;
- prove secrets/tokens do not appear in representative logs/problem responses;
- prove unsupported/malformed network/traffic input is rejected rather than broadened;
- prove SQL input passes only through bound parameters at persistence integration boundary;
- prove stale version conflicts instead of overwriting.

Blocking security Questions: none for selected MVP. Deferred items have explicit reopening conditions above.
