# Active execution

Current: `PLAN-037 — I23 Enterprise Identity and Authoritative Source Integration`.

Current task: WP2 enterprise authentication seam.

Goal: replace local/demo identity and seed-only source dependencies with explicit enterprise-facing integration boundaries while preserving Authority Management, Application Communication Catalogue and Resource Catalogue semantic ownership.

Working set:
- `docs/plans/active/PLAN-037-i23-enterprise-identity-authoritative-sources.md`;
- `docs/requirements/enterprise-identity-authoritative-sources.md`;
- `docs/architecture/enterprise-identity-authoritative-sources-boundary.md`;
- `src/napms/runtime/auth.py`;
- `src/napms/runtime/enterprise_identity.py`;
- `tests/runtime/test_enterprise_identity.py`.

Semantic result so far:
- identity and business authority are explicitly separate;
- verified external subjects are qualified by provider identity;
- actor mapping has explicit `Mapped | Unmapped | Ambiguous | Unknown` outcomes and only `Mapped` exposes an actor;
- deterministic in-process mapping proof exists without claiming a real IdP;
- login/display hints are non-authoritative and do not manufacture actor mappings.

Known constraint: no concrete corporate IdP or authoritative enterprise source product/schema/endpoint is selected in repository truth. Do not invent one. Deterministic stubs may prove source-neutral semantics; real provider transport remains unproven until selected evidence exists.

Gate: WP2 exits when the runtime authentication dependency can be expressed through the source-neutral seam while retaining the local password flow as a local/test adapter and without changing Authority Management admission semantics.

Next action: generalize the HTTP/runtime authentication dependency away from `LocalPasswordAuthenticator`, preserve the current local UI/session contract, and add an executable composition proof for verified external identity -> mapped actor -> existing Authority admission.
