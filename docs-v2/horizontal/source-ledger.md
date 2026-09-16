# Full-width source disposition ledger

Status: IN PROGRESS / non-canonical.

This ledger prevents legacy file placement or vocabulary from silently becoming v2 ownership. `docs/**` is read as accepted design evidence; each source is routed to the earliest semantic stage it actually supports.

## Root documentation contract

| Source | Horizontal disposition |
|---|---|
| `docs/README.md` | reconstruction/source-authority policy; informs horizontal guardrails, not product requirements by itself |

## Requirements sources

| Source | S0/S1/S2 routing |
|---|---|
| `docs/requirements/README.md` | inventory/status evidence; individual referenced contracts are authoritative content |
| `business-connectivity-g1.md` | S0 problem evidence + S1 Business Intent requirements; strategic ownership -> Business Connectivity |
| `application-catalogue-domain-target.md` | S1 ACC/AD/RC target behavior; S2 boundary evidence split across ACC, AD, RC |
| `application-catalogue-target.md` | retained as-built behavior; compatibility facts do not override newer target ownership |
| `catalogue-curation.md` + acceptance/security | S1 catalogue curation behavior; split among ACC/AD/RC/AM boundaries; RC MVP cardinality follows current revalidated S2 |
| `access-governance-g1.md` | S1 proposal/formal-decision behavior retained; legacy Access Governance ownership is superseded by current Access Policy ownership |
| `access-policy-core.md` | S1 concrete PolicyRule behavior; S2 owner Access Policy |
| `network-enforcement-placement-core.md` | S1 placement/relevance behavior; S2 owner NEP |
| `technical-access-evidence-core.md` + acceptance | S1 evidence behavior; S2 owner TAE; acquisition separated as integration capability |
| `policy-realization-reconciliation-g1.md` + `access-policy-realization-mvp.md` | S1 comparison/delta/change/verification behavior; S2 owner APR |
| `provider-policy-renderer-mvp.md` | S1 semantic-preserving rendering behavior; S2 disposition integration capability |
| `network-environment-operations.md` | S1 controlled mutation behavior; S2 owner NEO |
| `policy-export-core.md` + `first-mvp-vendor-neutral-policy-export.md` | S1 export/materialization behavior; strategic disposition RPM composition over authoritative contexts |
| `scoped-connectivity-inventory.md` + acceptance | S1 owner-preserving read behavior; S2 non-peer read composition |
| `traffic-analysis-checker.md` | S1 technical-entry/read-analysis behavior; strategic routing to owner-preserving composition over existing contexts, not a new peer BC |
| `web-ui-requirements.md` | S1 product-facing interaction/quality requirements; UI remains outer adapter and does not create semantic ownership |
| `enterprise-identity-authoritative-sources.md` | current local-first behavior + optional extension seams; authentication/source integration remains outside peer domain ownership, AM remains authority owner |

## Domain sources

| Source family | Horizontal disposition |
|---|---|
| `strategic-model.md`, `context-map.md`, `semantic-ownership.md`, `capabilities.md`, `bounded-contexts.puml` | primary current strategic S2 baseline; normalized into `s2/strategic-model.md` |
| `mvp-ddd-convergence-checkpoint.md` | accepted convergence/evidence record; not a separate semantic owner |
| per-context `docs/domain/<context>/**` | tactical S2 evidence used to verify strategic boundaries/terms; tactical reconstruction is downstream of this horizontal pass |
| `resource-role-model.md` | RC/authority/responsibility boundary evidence; responsibility does not imply authority |
| legacy/as-built domain compatibility material | retained only where current docs explicitly require reconstruction; does not override revalidated target strategic ownership |

## Architecture / engineering / UI sources

Architecture, engineering and UI documents are inspected only to recover upstream problem/requirement/strategic facts that are explicitly accepted there and missing from earlier-stage docs. Their transport, persistence, package, runtime and deployment choices are not promoted into S0/S1/S2 unless they express an accepted non-negotiable constraint or strategic semantic boundary.

Known examples already routed upstream:

- Web outer-adapter rule -> S1/QREQ ownership guardrail;
- provider-native isolation -> QREQ-004 and integration-capability disposition;
- local-first identity operation -> S1 current behavior;
- catalogue HTTP plural-address legacy wording -> not migrated because current S2 explicitly supersedes it and MVP decision is one effective AddressSpace.

## Deferred/future material

Deferred material is retained as `EXTENSION` where it describes a real accepted future problem/capability. It is not promoted to current MVP behavior and does not create a new Bounded Context without an independent authoritative lifecycle/model.

## Remaining ledger work

The full tree still requires mechanical source-by-source coverage marking for all architecture, engineering, decisions and UI files. This is coverage accounting, not permission to derive semantics from implementation. Any material contradiction discovered during that accounting is escalated as a documentation decision.
