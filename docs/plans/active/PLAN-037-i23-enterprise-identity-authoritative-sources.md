# PLAN-037 — I23 Optional Integration Extension Skeleton

Status: `active — lightweight skeleton closure`.

Date: 2026-09-10.

## Goal

Keep the current local NAPMS runtime as the primary supported operating mode and add only minimal extension seams for possible future external identity/source integration.

I23 does **not** replace local authentication, local catalogue data or local Authority data. It does **not** select, implement or require any enterprise IdP, directory, CMDB, catalogue, MSSQL bridge or other external system.

## Accepted baseline

- local username/password authentication is the primary runtime path;
- server-side actor identity remains authoritative for request execution;
- Authority Management remains the owner of business authorization;
- ACC and Resource Catalogue remain NAPMS-owned contexts populated locally for the current product;
- deterministic stubs are sufficient to prove that future adapters have a place to attach;
- no real external transport/provider compatibility is claimed or required;
- external integration is optional future work and is not a prerequisite for continued product development.

## Scope

### WP1 — Extension boundary documentation

Status: `done`.

Keep a small source-neutral contract documenting:
- identity != authority;
- optional external subject -> NAPMS actor mapping;
- external source adapters, if ever added, must preserve bounded-context ownership;
- vendor/protocol types stay outside Domain.

Artifacts:
- `docs/requirements/enterprise-identity-authoritative-sources.md`;
- `docs/architecture/enterprise-identity-authoritative-sources-boundary.md`.

### WP2 — Deterministic identity skeleton

Status: `implemented; verification pending`.

Implemented:
- `VerifiedExternalIdentity` value;
- `ActorIdentityResolver` port;
- deterministic mapping stub;
- explicit `Mapped | Unmapped | Ambiguous | Unknown` fail-closed outcomes;
- focused unit tests.

This seam is dormant extension infrastructure. It is not wired as the primary login path and must not displace `LocalPasswordAuthenticator`.

Exit:
- local authentication remains unchanged and primary;
- optional future external authentication can terminate at a source-neutral mapping seam;
- no HTTP/OIDC/provider route is added;
- no business authority is inferred from external identity data.

### WP3 — Optional source-adapter skeleton

Status: `minimal documentation only; no implementation required`.

For Authority Management, ACC and Resource Catalogue, the architecture only records where a future source adapter would terminate. No synchronization engine, external schema, transport, scheduler or production source is required.

Exit:
- context ownership is documented;
- deterministic stubs remain sufficient if an executable proof is useful later;
- local data remains the supported source of truth for the current product.

### WP4 — Verification and absorption

Status: `blocked only on repository gates for the existing skeleton`.

Run the relevant tests/gates for the small extension seam, absorb the reduced scope into roadmap/current architecture, and close I23 without introducing real enterprise dependencies.

## Explicit non-goals

- replacing local username/password authentication;
- OIDC/OAuth2 implementation;
- corporate IdP integration;
- external Authority administration;
- CMDB/application catalogue/resource inventory synchronization;
- Legacy/MSSQL integration;
- production external-source availability/freshness/deletion semantics;
- making external integration a prerequisite for I24/I25 or other product work.

## Current gate

Only framework-level seams and deterministic stubs are open. Real external adapters remain deferred until a concrete future requirement explicitly selects them.

## Next action

Align canonical requirements, architecture and roadmap with local-first operation, then verify the already implemented deterministic identity skeleton. Do not generalize the existing HTTP login away from `LocalPasswordAuthenticator` as part of I23.
