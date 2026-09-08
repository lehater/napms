# NAPMS Web UI

First I8 browser-facing vertical slice.

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
npm install
npm run dev
```

Vite proxies `/api` and `/health` to `127.0.0.1:8000`.

The first slice contains only Login and Compose Connectivity. Additional navigation is added only with real backend use cases.
