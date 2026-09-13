# NAPMS Web UI

Browser-facing operator UI for the supported local NAPMS product path.

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

`package-lock.json` is repository-owned and CI/Docker use `npm ci`, so dependency resolution is reproducible for a source revision.

Vite proxies `/api` and `/health` to `127.0.0.1:8000`.

Current accepted workspaces cover Connectivity, Needs, Decisions, Rules, Effective Desired Policy and Normalized Policy export. The runtime may still expose the older read-only `Realization` screen while APR migration is pending; its existing stages/statuses are legacy implementation behavior and are not the target Access Policy Realization contract. Current APR semantics are defined only by `docs/domain/access-policy-realization/README.md` until the redesign is locked.

Authority remains enforced by backend owner use cases; navigation does not grant business authority.
