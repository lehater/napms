# Active execution

Current: `PLAN-037-i23-enterprise-identity-authoritative-sources.md`.

Current task: verify and close I23 Optional Integration Extension Skeleton.

Goal: keep the current local authentication and local data sources as the supported product mode while retaining only minimal dormant seams for possible future external identity/source adapters.

Working set:
- `docs/plans/active/PLAN-037-i23-enterprise-identity-authoritative-sources.md`;
- `docs/requirements/enterprise-identity-authoritative-sources.md`;
- `docs/architecture/enterprise-identity-authoritative-sources-boundary.md`;
- `src/napms/runtime/enterprise_identity.py`;
- `tests/runtime/test_enterprise_identity.py`;
- `docs/engineering/post-wave1-product-completion-roadmap.md`;
- `docs/architecture/current-architecture.md`.

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

Gate: repository verification for the completed local-first skeleton. Real external integrations remain future optional work triggered only by a concrete accepted requirement.

Next action: obtain clean repository gates, absorb I23 as complete, remove the active plan, and promote I24 Local Deployment and Operational Hardening.
