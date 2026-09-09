# Active execution

Current: `PLAN-037 — I23 Enterprise Identity and Authoritative Source Integration`.

Current task: WP1 domain/architecture re-entry.

Goal: replace local/demo identity and seed-only source dependencies with explicit enterprise-facing integration boundaries while preserving Authority Management, Application Communication Catalogue and Resource Catalogue semantic ownership.

Working set:
- `docs/plans/active/PLAN-037-i23-enterprise-identity-authoritative-sources.md`;
- `src/napms/runtime/auth.py`;
- Authority Management / Application Communication Catalogue / Resource Catalogue canonical requirements, domain and architecture artifacts.

Known constraint: no concrete corporate IdP or authoritative enterprise source product/schema/endpoint is selected in repository truth. Do not invent one. Deterministic stubs may prove source-neutral semantics; real provider transport remains unproven until selected evidence exists.

Gate: WP1 exits when identity != authority, external-subject -> NAPMS-actor mapping, source-import ownership and fail-closed ambiguity semantics are accepted canonically.

Next action: add/review the I23 requirements and architecture boundary, then open WP2 enterprise authentication seam only if WP1 is coherent.
