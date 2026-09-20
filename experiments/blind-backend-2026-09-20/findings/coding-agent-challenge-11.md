# Coding-Agent Challenge 11

Status: FAILED — two final P1 consistency/security repairs required

## CAC-024 — P1 — provenance completeness for selected non-effective Rules

The accepted export contract now promises one complete MaterializedRuleProvenance for **every selected PolicyRule**, including INACTIVE/out-of-window Rules.

However the old completeness sentence still said COMPLETE requires no issue only for selected effective Rules. That is correct for **technical realization**, but too weak for required business/permission provenance.

Repair:
- every selected Rule must have resolvable Access Policy authorization evidence and associated Business Connectivity justification facts needed to construct complete MaterializedRuleProvenance;
- failure to resolve accepted provenance reference for any selected Rule produces REFERENCE_UNRESOLVABLE and overall UNRESOLVED, even if that Rule is technically non-effective;
- technical realization requirements (InteractionRevision traffic for row expansion, Deployments, current Resource addresses) apply only to selected effective Rules;
- INACTIVE/out-of-window selected Rule with complete provenance and missing technical realization remains non-blocking and may coexist with overall COMPLETE;
- missing current Need is not missing provenance: RETIRED/zero-current justifications remain resolvable and use reconciliation semantics.

## CAC-025 — P1 — OIDC issuer transport/test exception was not runtime-enforceable

Operability configuration allowed an HTTPS issuer “except explicitly local test issuer” without defining a runtime mode or enforcement mechanism. A coding agent could accidentally permit HTTP OIDC in serve production.

Repair:
- NAPMS_OIDC_ISSUER is always an absolute HTTPS URL in serve mode; no HTTP localhost exception exists in production contract;
- OIDC discovery metadata issuer must exactly equal configured issuer;
- discovered jwks_uri must be absolute HTTPS;
- redirects to non-HTTPS locations are rejected;
- tests use an HTTPS test issuer or a controlled in-process adapter below the HTTP boundary; no production config relaxation is introduced.

Freeze remains prohibited until Application/Interface/Quality/Security/Operability/Verification/Test/Implementation are synchronized and Challenge 12 passes.
