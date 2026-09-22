# NAPMS Web UI

React browser adapter for NAPMS.

## Local development

Start the supported local stack from the repository root:

```bash
make dev-up
```

Open `http://127.0.0.1:8080` and sign in with the fixed development credentials:

```text
login: admin
password: admin
```

The fixed credentials are available only when the backend is composed with
`NAPMS_ENVIRONMENT=local-dev`. They bootstrap a short-lived token from the local
OIDC issuer; all product API requests still use the canonical
`Authorization: Bearer <token>` path and normal backend authorization.

For standalone frontend development:

```bash
cd web
npm ci
npm run dev
```

Vite proxies `/v1`, `/dev-auth`, and `/health` to `127.0.0.1:8000`, so the
backend must be running in the supported local-dev composition.

`package-lock.json` is repository-owned and CI/Docker use `npm ci`.

Current product behavior is defined by `docs/requirements/`; current UI behavior
and frontend design are owned by `docs/contracts/ui/`,
`docs/architecture/mvp-frontend-*.yaml`, and
`docs/plans/mvp-frontend-*.yaml`. Existing runtime routes/components are
implementation evidence and do not define product semantics when they disagree
with those owners. `docs-legacy/ui/` is retired migration evidence only.
