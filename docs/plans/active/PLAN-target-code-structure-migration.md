# PLAN — Target Code Structure Migration

Status: `active`

## Goal

Move NAPMS to the accepted final physical taxonomy without product/domain semantic change:

```text
backend/src/napms/
  contexts/
  workflows/
  platform/
```

## Inputs

- `docs/architecture/code-structure.md`
- `docs/engineering/target-code-structure-migration-roadmap.md`
- `docs/decisions/ADR-014-target-code-structure-taxonomy.md`

## Execution order

```text
M1 backend repository boundary
-> M2 bounded contexts + final Clean layers
-> M3 workflows + remove generic composition
-> M4 platform consolidation
-> M5 capability-oriented internals where justified
-> M6 Web final locality
-> M7 compatibility purge + final enforcement
```

## M1 — Repository backend boundary

Status: `complete` in `f0e281e`.

## M2 — Bounded contexts

Status: `active` on branch `refactor/m2-network-environment-operations`.

M2 is one milestone PR. Each bounded-context move remains an atomic commit. Hosted gates run only on the final M2 PR.

Execution rules:
- preserve product/domain behavior;
- move each context directly to `backend/src/napms/contexts/<context>/`;
- normalize only real responsibilities to `domain / application / infrastructure / presentation`;
- update all consumers, package-data/migrations and tests;
- remove the legacy top-level implementation package;
- add architecture guards;
- run targeted unit + architecture tests after every context;
- run `make test`, harness and knowledge checks after each work package;
- configured PostgreSQL evidence is mandatory before final M2 closure;
- do not move workflow/composition ownership until M3.

### Completed M2 slices

1. `network_environment_operations` — `8dac6ff40fc82732b14ec7aeca80dabc84af062a`
2. `technical_access_evidence` — `3dd64d4167838bcd3f90933f6aef54940f6ef88b`
3. `network_enforcement_placement` — `a17ba404496932d70ee21ccb3ff7806ca52e7344`
4. `connectivity_requirements` — `a8842d21eeaa7da22993d9af7ae2dd71a16de82d`
5. `connectivity_decision` — `7c75e448c755a37774dd7bbd4d5ff09708559eac`
6. `authority_management` — `3ad1015cd71daf81231d6e717302e1f448a48e84`
7. `resource_catalogue` — `3ca10ac360672536b6858a48f55d1d269fe159a4`
8. `access_policy_realization` — `46fa4d97dd8c8bf1658a75677161e88171ab949a`

All completed contexts use only the final `napms.contexts` namespace.

### Final M2 work package

Migrate the two remaining bounded contexts as separate commits, in this order:

1. `application_catalogue`
2. `access_policy`

`application_catalogue` target outer structure:

```text
contexts/application_catalogue/
  domain/
  application/
  infrastructure/
    persistence/postgres/
    integrations/
    local/
  presentation/http/
```

Classification:
- existing HTTP tree -> `presentation/http/`;
- PostgreSQL tree -> `infrastructure/persistence/postgres/`;
- `access_policy.py`, `connectivity_decision.py`, `connectivity_requirements.py`, `policy_export.py`, `resource_binding_target.py`, `scoped_connectivity_inventory.py` -> `infrastructure/integrations/`;
- `dcs_authoring.py` and `dcs_json_codec.py` -> `infrastructure/integrations/` because they translate to/from existing policy-export normalization contracts;
- `curation_support.py` -> `infrastructure/local/curation_support.py`.

`access_policy` target outer structure:

```text
contexts/access_policy/
  domain/
  application/
  infrastructure/
    persistence/postgres/
    integrations/
  presentation/http/
```

Classification:
- `http.py` -> `presentation/http/routes.py`;
- `http_errors.py` -> `presentation/http/errors.py`;
- PostgreSQL tree -> `infrastructure/persistence/postgres/`;
- `connectivity_decision.py`, `requirement_policy_alignment.py`, `scoped_connectivity_inventory.py` -> `infrastructure/integrations/`.

Do not move generic `composition/` or workflow ownership in this package; repair only imports needed by context moves.

## Exit criteria

M2 closes only when all ten accepted bounded contexts are under `napms.contexts`, legacy top-level context packages are absent, architecture guards enforce the final boundaries, full local checks pass, PostgreSQL integration evidence runs in a configured environment, and one final M2 PR passes required hosted gates.

## Blockers

None for the final context-migration package. Configured PostgreSQL execution remains a milestone-exit requirement after the two context commits.

## Next

Migrate `application_catalogue` and then `access_policy` as separate atomic commits. Push and stop for final M2 architectural review. Do not start M3 or create the PR before that review.
