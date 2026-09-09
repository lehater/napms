# Active execution

Current: `PLAN-037-i23-enterprise-identity-authoritative-sources.md`

Goal: keep local authentication and local Authority/ACC/Resource data as the supported product mode while retaining only minimal dormant extension seams for possible future external adapters.

Current task: verify and close I23 Optional Integration Extension Skeleton.

## Working set

Read first:
- `docs/plans/active/PLAN-037-i23-enterprise-identity-authoritative-sources.md`
- `docs/requirements/enterprise-identity-authoritative-sources.md`
- `docs/architecture/enterprise-identity-authoritative-sources-boundary.md`
- `src/napms/runtime/enterprise_identity.py`
- `tests/runtime/test_enterprise_identity.py`

Expand only if needed:
- `docs/engineering/post-wave1-product-completion-roadmap.md`
- `docs/architecture/current-architecture.md`

Accepted direction:
- `LocalPasswordAuthenticator` remains the primary authentication path;
- local Authority/ACC/Resource data remains the current supported source of truth;
- the external identity seam is optional dormant infrastructure only;
- deterministic stubs are sufficient for I23;
- no OIDC/IdP/CMDB/MSSQL/enterprise source integration is required;
- no HTTP/runtime migration away from the local login flow is part of I23;
- Authority Management remains separate from authentication.

Implemented skeleton:
- `VerifiedExternalIdentity`;
- `ActorIdentityResolver`;
- deterministic provider-qualified actor mapping;
- explicit `Mapped | Unmapped | Ambiguous | Unknown` fail-closed outcomes;
- focused unit tests.

## Blockers

Only clean repository gates remain. No product/domain blocker remains for I23.

## Gate

Run repository gates against the final local-first skeleton. Real external integrations are explicitly out of scope.

## Next

If gates pass, absorb I23 as complete, remove the active plan, set `Current: none`, and promote I24 Local Deployment and Operational Hardening in the roadmap.
