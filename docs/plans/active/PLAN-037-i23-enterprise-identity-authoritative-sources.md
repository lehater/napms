# PLAN-037 — I23 Optional Integration Extension Skeleton

Status: `active — verification`.

Date: 2026-09-10.

## Goal

Keep the current local NAPMS runtime as the primary supported operating mode and add only minimal extension seams for possible future external identity/source integration.

I23 does **not** replace local authentication, local catalogue data or local Authority data. It does **not** select, implement or require any enterprise IdP, directory, CMDB, catalogue, MSSQL bridge or other external system.

## Inputs

Accepted baseline:
- local username/password authentication is the primary runtime path;
- server-side actor identity remains authoritative for request execution;
- Authority Management remains the owner of business authorization;
- ACC and Resource Catalogue remain NAPMS-owned contexts populated locally for the current product;
- deterministic stubs are sufficient to prove that future adapters have a place to attach;
- no real external transport/provider compatibility is claimed or required;
- external integration is optional future work and is not a prerequisite for continued product development.

Canonical inputs:
- `docs/requirements/enterprise-identity-authoritative-sources.md`;
- `docs/architecture/enterprise-identity-authoritative-sources-boundary.md`;
- `docs/architecture/current-architecture.md`;
- `docs/engineering/post-wave1-product-completion-roadmap.md`.

## Work packages

### WP1 — Extension boundary documentation

Status: `done`.

Documented:
- identity != authority;
- optional external subject -> NAPMS actor mapping;
- external source adapters, if ever added, preserve bounded-context ownership;
- vendor/protocol types stay outside Domain.

### WP2 — Deterministic identity skeleton

Status: `implemented; verification pending`.

Implemented:
- `VerifiedExternalIdentity` value;
- `ActorIdentityResolver` port;
- deterministic mapping stub;
- explicit `Mapped | Unmapped | Ambiguous | Unknown` fail-closed outcomes;
- focused unit tests.

The seam is dormant extension infrastructure. It is not wired as the primary login path and does not displace `LocalPasswordAuthenticator`.

### WP3 — Optional source-adapter skeleton

Status: `done as documentation-only scope`.

Authority Management, ACC and Resource Catalogue retain context-owned import/projection boundaries for any future adapter. No synchronization engine, external schema, transport, scheduler or production source is implemented or required.

### WP4 — Verification and absorption

Status: `active`.

Run repository gates for the small extension seam, then absorb the reduced scope into canonical state and remove this plan from `docs/plans/active/`.

## Exit criteria

I23 exits when all of the following are true:
- local username/password authentication remains unchanged and primary;
- local Authority/ACC/Resource state remains the supported current source of truth;
- optional external identity can terminate at a source-neutral provider-qualified actor-mapping seam;
- unmapped, ambiguous and unknown external identities fail closed;
- no HTTP/OIDC/provider route or real external source integration is introduced;
- Authority Management remains independent from authentication mechanics;
- canonical architecture and roadmap state external integrations are optional future work;
- relevant repository gates pass.

## Explicit non-goals

- replacing local username/password authentication;
- OIDC/OAuth2 implementation;
- corporate IdP integration;
- external Authority administration;
- CMDB/application catalogue/resource inventory synchronization;
- Legacy/MSSQL integration;
- production external-source availability/freshness/deletion semantics;
- making external integration a prerequisite for I24/I25 or other product work.

## Blockers

No product/domain blocker remains. Closure is blocked only on clean repository verification for the final branch state.

## Next

Obtain clean repository gates. If they pass, mark I23 complete in roadmap/current state, promote I24 Local Deployment and Operational Hardening, delete this active plan, and return `docs/plans/active/README.md` to `Current: none`.
