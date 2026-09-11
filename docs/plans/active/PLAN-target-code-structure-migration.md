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

The long-range roadmap owns detailed stage rules. The active capsule selects the current task.

## M1 — Repository backend boundary

Status: `complete` in `f0e281e`.

M1 moved the backend workspace under `backend/`, preserved behavior, and passed local and hosted gates before M2 started.

## M2 — Bounded contexts

Status: `active` on branch `refactor/m2-network-environment-operations`.

M2 is integrated as one milestone PR. One bounded context remains one atomic commit; hosted PR gates run only on the final M2 PR.

Execution policy:
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

All completed contexts use the final `napms.contexts` namespace and have no legacy implementation package.

### Current M2 work package

Migrate only `access_policy_realization`.

Target outer structure:

```text
contexts/access_policy_realization/
  domain/
  application/
  infrastructure/
    integrations/
    rendering/
  presentation/        # only if actual inbound responsibility exists
```

Current adapter classification:
- `catalogues.py` -> `infrastructure/integrations/catalogues.py`;
- `desired_policy.py` -> `infrastructure/integrations/desired_policy.py`;
- `placement.py` -> `infrastructure/integrations/placement.py`;
- `technical_access_evidence.py` -> `infrastructure/integrations/technical_access_evidence.py`;
- `configured_evidence.py` -> `infrastructure/integrations/configured_evidence.py`;
- `cisco_asa.py` -> `infrastructure/rendering/cisco_asa.py`;
- `cisco_asa_semantics.py` -> `infrastructure/rendering/cisco_asa_semantics.py`.

No generic `adapters/` remains. Do not move `composition/access_policy_realization_postgres.py` or workflow ownership in this slice; only repair imports required by the context move.

## Exit criteria

M2 closes only when all accepted bounded contexts are under `napms.contexts`, legacy top-level context packages are absent, architecture guards enforce the new boundaries, full local checks pass, PostgreSQL integration evidence is exercised in a configured environment, and one final M2 PR passes required hosted gates.

## Blockers

None for the current context slice. Configured PostgreSQL execution remains a deferred M2 milestone-exit requirement.

## Next

Migrate only `access_policy_realization` as one atomic commit, push the milestone branch, and stop for architectural review. Do not start `application_catalogue`, `access_policy`, or M3.
