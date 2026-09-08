# Current implementation state

Status: `I8 PASS — first Web UI and HTTP runtime boundary implemented`.

Date: 2026-09-09.

Current execution is owned by `docs/plans/active/README.md`.

## Completed through I7

- I1 authoritative Access Rule materialization core;
- I2 PostgreSQL uniqueness/concurrency/rollback proof;
- I3 authorized Active/Inactive mutation with durable business audit;
- I4 EffectiveWindow mutation/evaluation and authorized effective desired-policy selection;
- I5 coherent immutable Export Snapshot;
- I6 vendor-neutral normalized policy transformation;
- first-class greenfield Authority Management, Application Communication Catalogue and Resource Catalogue bounded contexts;
- PostgreSQL-only persistence with module-owned schemas/repositories and cross-module persistence guards;
- fail-closed temporal Authority/catalogue semantics;
- typed local-dev PostgreSQL configuration/composition;
- direct end-to-end proposal -> Authority -> ACC -> Connectivity Decision -> Access Policy -> effective selection -> snapshot -> normalized export proof.

## I8 result

`PASS` for the explicitly bounded `local-dev` Web UI + HTTP JSON runtime.

Implemented:
- accepted Web UI product/UX baseline and implementation handoff under `docs/ui/`;
- first Web UI vertical slice: Login -> Compose Connectivity -> Access Rule Proposal -> Materialized/Resolved/NotAllowed result;
- React + TypeScript + Tailwind + shadcn-oriented frontend foundation with dark-navy enterprise shell;
- FastAPI HTTP JSON outer adapter derived from application use cases rather than database CRUD;
- local login/password authentication with scrypt-hashed configured credentials and opaque server-side sessions;
- trusted authenticated backend actor identity feeding Authority Management; request-payload `actorId` spoofing is rejected;
- authority-aware proposal-scope discovery and paginated ACC directed-interaction discovery;
- explicit `local-dev` Connectivity Decision adapter returning `Allowed` only after existing Authority and structural-validity checks, with `local-dev:allowed` provenance;
- normalized-policy JSON handoff preserving Rule/decision/Authority/ACC/RC semantics and provenance;
- no partial normalized rows when snapshot facts are stale, missing, ambiguous or correlation-invalid;
- structured JSON completion events, bounded correlation IDs, safe dependency/outcome context and generic public unexpected-error responses;
- explicit liveness/readiness and startup/configuration failure behavior;
- safe mappings for authentication, authority denied/unknown, invalid/unknown interaction, decision unknown/mismatch, persistence uncertainty, not-found, stale/correlation and normalization failures;
- final I8 architecture/security review has no open P0/P1 findings;
- final core, PostgreSQL, Web, harness and knowledge gates passed.

## I8 scope boundary

I8 intentionally does **not** define Connectivity Decision Domain internals.

The following remain deferred:
- approval/review workflow, approver roles and `Pending/Approved/Rejected` lifecycle;
- persistent generic `Access Request` business identity;
- external OIDC/OAuth2/corporate IdP;
- production authentication/session topology;
- dashboard and secondary aggregate UI;
- full Access Rule workspace/state-management UI;
- Effective Desired Policy and Normalized Policy Web UI screens beyond the implemented HTTP handoff;
- generic IAM/CMDB administration;
- CSV/XLSX serializers;
- vendor rendering, configured-state reconciliation and device execution.

## Current infrastructure boundary

Implemented:
- Access Policy PostgreSQL;
- Authority Management PostgreSQL;
- Application Communication Catalogue PostgreSQL;
- Resource Catalogue PostgreSQL;
- strict internal DCS projection codec;
- typed local-dev configuration/composition;
- FastAPI HTTP runtime;
- local-dev authentication/session boundary;
- explicit local-dev Connectivity Decision adapter;
- public normalized-policy JSON serializer;
- React Web UI first vertical slice;
- structured runtime observability/correlation and health/readiness.

The implementation remains greenfield: Legacy, MSSQL and vendor/device execution are not dependencies.
