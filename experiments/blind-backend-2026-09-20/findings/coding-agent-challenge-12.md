# Coding-Agent Challenge 12

Status: FAILED — OIDC cache-age / refresh-attempt semantics require one final repair

## CAC-026 — P1 — JWKS max-stale lifecycle underspecified

Current contract says cached keys remain usable while cache age <= NAPMS_JWKS_MAX_STALE, but does not define the age origin or the meaning of zero. Different libraries can use fetch time, HTTP cache headers, provider max-age, or stale-since-refresh-failure, producing different readiness/401/503 behavior.

Repair:
- NAPMS_JWKS_MAX_STALE must be duration > 0;
- keyset age is measured from lastSuccessfulValidationMaterialRefreshAt, using the runtime clock;
- one refresh attempt is one complete HTTPS discovery + exact issuer/jwks_uri validation + JWKS fetch/validation cycle;
- one refresh sequence performs at most NAPMS_OIDC_FETCH_MAX_ATTEMPTS complete attempts with configured backoff between failed attempts;
- successful refresh atomically replaces the usable keyset and metadata and resets lastSuccessfulValidationMaterialRefreshAt;
- failed refresh leaves the prior keyset/timestamp unchanged;
- prior keys may still validate tokens only while now - lastSuccessfulValidationMaterialRefreshAt <= NAPMS_JWKS_MAX_STALE;
- once age exceeds max-stale, those keys are unusable for protected validation/readiness until a successful refresh;
- provider HTTP cache headers may optimize fetches internally but cannot extend or redefine this application max-stale contract.

Freeze remains prohibited until Operability/Component/Security Analysis/Verification/Test/Implementation are synchronized and Challenge 13 passes.
