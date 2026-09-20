# Coding-Agent Challenge 08

Status: FAILED — OIDC validation/runtime lifecycle requires repair

## CAC-017 — P1 — JWT algorithm/time/audience semantics delegated to library defaults

Different maintained JWT libraries have different defaults for:
- allowed signature algorithms;
- HMAC/none rejection;
- audience string vs array;
- required exp;
- nbf tolerance / clock skew.

Repair:
- add required startup config `NAPMS_OIDC_ALLOWED_ALGS`;
- accepted values are a non-empty unique comma-separated subset of:
  `RS256,RS384,RS512,PS256,PS384,PS512,ES256,ES384,ES512,EdDSA`;
- `none`, every `HS*` algorithm and unknown names are configuration/token-invalid paths and are never accepted;
- token `alg` must be in configured allow-list and compatible with selected JWKS public key type;
- add required `NAPMS_OIDC_CLOCK_SKEW` duration >= 0;
- `iss` must exactly equal configured issuer;
- `aud` is required string or array<string> containing the exact configured audience;
- `exp` is required NumericDate and is valid only through configured skew;
- `nbf`, when present, is NumericDate and uses the same skew;
- `sub` is required non-empty string;
- `iat` is not an authorization criterion in this MVP.

## CAC-018 — P1 — OIDC key acquisition/readiness could deadlock recovery

Design required readiness=false without usable key material but left initial acquisition/recovery trigger open. With traffic removed while unready, a purely request-lazy refresh could never recover.

Repair:
- after config validation and before opening the listener, runtime performs the bounded initial OIDC metadata/JWKS acquisition;
- failure to obtain initial usable validation keys is a startup dependency failure: emit safe runtime.startup.failed and exit non-zero;
- after startup, cached keys remain usable only through max-stale semantics;
- unknown kid/protected request may trigger one bounded refresh sequence;
- when readiness observes no usable key material, it may trigger a **single-flight bounded refresh** and reports UP only if usable material is established; concurrent readiness/protected refresh callers share the in-flight refresh;
- refresh failure with still-usable cached keys does not force false DOWN;
- once cached keys are beyond max-stale and refresh fails, readiness is DOWN and protected token validity that cannot be established returns 503;
- no product/domain background worker is introduced.

Freeze remains prohibited until Security/Operability/Component/Verification/Test/Implementation encode this contract and Challenge 09 passes.
