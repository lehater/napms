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

Status: `implementation complete; final PR gates pending` on branch `refactor/m2-network-environment-operations`.

All ten accepted bounded contexts now live only under `backend/src/napms/contexts/<context>/` with responsibility-based Clean outer layers. Legacy top-level context packages are absent. Workflow/composition/platform ownership remains intentionally transitional for M3/M4.

Completed slices:

1. `network_environment_operations` — `8dac6ff40fc82732b14ec7aeca80dabc84af062a`
2. `technical_access_evidence` — `3dd64d4167838bcd3f90933f6aef54940f6ef88b`
3. `network_enforcement_placement` — `a17ba404496932d70ee21ccb3ff7806ca52e7344`
4. `connectivity_requirements` — `a8842d21eeaa7da22993d9af7ae2dd71a16de82d`
5. `connectivity_decision` — `7c75e448c755a37774dd7bbd4d5ff09708559eac`
6. `authority_management` — `3ad1015cd71daf81231d6e717302e1f448a48e84`
7. `resource_catalogue` — `3ca10ac360672536b6858a48f55d1d269fe159a4`
8. `access_policy_realization` — `46fa4d97dd8c8bf1658a75677161e88171ab949a`
9. `application_catalogue` — `80f99bbc14b169887b8f8092d51ec7d60e6cdf51`
10. `access_policy` — `a363f313e058be69631a3dc08822f77b8d8544f4`

Validation evidence before final PR:
- targeted tests passed for every context slice;
- `make test`: 796 passed, 141 deselected;
- `make harness-check`: passed;
- `make knowledge-check`: passed;
- configured PostgreSQL run: 141 passed, 0 skipped.

## Exit criteria

M2 closes when the final milestone PR passes all required hosted gates and is squash-merged to `main`.

## Blockers

None.

## Next

Open the final M2 milestone PR, run all required hosted gates, and squash-merge if green. Do not start M3 or make material changes after the final gate without returning the PR to draft and gating again.
