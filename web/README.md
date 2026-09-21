# NAPMS Web UI

React browser adapter for NAPMS.

## Local development

Backend:

```bash
python -m pip install -e ".[dev,postgres,runtime]"
export NAPMS_ENVIRONMENT=local-dev
export NAPMS_DATABASE_DSN=postgresql://...
export NAPMS_LOCAL_AUTH_LOGIN=alexey
export NAPMS_LOCAL_AUTH_ACTOR_ID=actor-1
export NAPMS_LOCAL_AUTH_PASSWORD_HASH='...'
napms-http
```

Frontend:

```bash
cd web
npm ci
npm run dev
```

`package-lock.json` is repository-owned and CI/Docker use `npm ci`. Vite proxies `/api` and `/health` to `127.0.0.1:8000`.

Current product behavior is defined by `docs/requirements/`; current UI behavior and frontend design are owned by `docs/contracts/ui/`, `docs/architecture/mvp-frontend-*.yaml`, and `docs/plans/mvp-frontend-*.yaml`. Existing runtime routes/components are implementation evidence and do not define product semantics when they disagree with those owners. `docs-legacy/ui/` is retired migration evidence only.
