# Coding-Agent Challenge 01

Status: CLOSED BY DESIGN REPAIR

The challenge assumes a coding agent receives only the blind IMPLEMENTATION closure and may make local coding choices, but no product/domain/architecture/interface/data/security/operability decisions.

## CAC-001 — P1 — incomplete Interface Design artifact

Classification: `incomplete concrete design artifact`.

The registered `napms.backend.api-contract` capability was structurally present, but a coding agent still had to decide material external semantics:

- exact request/response representations for most operations;
- whether create commands require idempotency keys;
- which aggregate ETag guards nested mutations;
- exact mutation success/status semantics;
- whether UNRESOLVED policy materialization is an HTTP error or a successful computation with a non-complete application result;
- stable unresolved issue codes;
- several required read surfaces, including Application read;
- how BusinessProcess/Need and Application child mutations expose concurrency.

This violates the Coding-Agent Challenge because these are Interface Authority decisions, not private implementation choices.

Repair: strengthen `api-contract.md` with canonical DTOs, status/header semantics, per-operation concurrency/idempotency rules and materialization outcome semantics.

## CAC-002 — P1 — incomplete configuration/operability semantics

Classification: `incomplete concrete design artifact`.

The registered operability capability described configuration categories but left the coding agent to choose:

- configuration-source precedence;
- runtime reload/mutability;
- which timeout/retry controls exist;
- hidden defaults versus explicitly supplied values;
- cached OIDC key behavior on dependency failure.

These choices affect startup/readiness/fail-closed and retry behavior.

Repair: define a single startup configuration source, explicit logical keys and validation, no runtime reload, explicit OIDC retry/cache behavior, and no mutation retry.

## CAC-003 — P2 — tactical/interface drift introduced speculative operations

Classification: `incomplete concrete design artifact`.

Tactical models exposed operations with no selected-MVP consumer or interface:
- Resource rename;
- Site update;
- ResponsibilityGroup update;
- BusinessProcess description update;
- ConnectivityNeed description update.

They were not required by admitted source input and would create unnecessary implementation decisions and test surface.

Repair: remove these operations; keep only current MVP mutations.

## H-FIND-001 — P1 — Artifact Skill routing/coverage

Classification: `missing/insufficient Artifact Skill routing`.

Separately reproduced by current Harness CI. Major blind graph knowledge kinds are `NO_REGISTERED_SKILL`; some have an existing Skill that is simply not registered, while others lack a dedicated artifact Skill.

This finding is not repaired inside NAPMS artifacts. It remains a Harness research-branch defect.

## Result before repair

Current Harness structurally evaluated IMPLEMENTATION as `COMPLETE`, proving that Core/provider closure is not semantic sufficiency by itself. This is consistent with Harness Core's documented boundary; semantic acceptance and Coding-Agent Challenge remain necessary.

The NAPMS design is not frozen until all P1 challenge findings are repaired and the challenge is rerun.
