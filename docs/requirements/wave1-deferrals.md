# Wave-1 deferred behavior register — PLAN-026 WP-07

Status: `accepted G2 deferral baseline`.

Date: 2026-09-08.

## Principle

A deferral is safe only when Wave 1 has a stable boundary and a concrete revisit trigger. Deferred behavior must not leak back into architecture as an assumed product rule.

| Deferred behavior | Wave-1 seam | Revisit trigger |
|---|---|---|
| Connectivity Decision reasons/policies/process | `AccessRuleProposal -> ConnectivityDecision(Allowed|NotAllowed) -> Access Policy` | selected wave must explain/manage why/how a decision is produced, its validity, exceptions, actors or supersession |
| human/automatic approval mechanics, quorum, SoD | opaque Decision Domain internals | selected behavior requires those roles/mechanics explicitly |
| Decision validity/re-evaluation/supersession lifecycle | historical decision is not silently rewritten; explicit superseding decision may affect current effect according to future contract | changing external facts must automatically affect current permission or product must manage decision history/lifecycle |
| Legacy Word/Excel/XUIT request compatibility | Wave 1 starts from domain-backed Proposal | transition/migration requirement selects Legacy intake compatibility |
| firewall/topology placement calculation | Wave 1 stops at vendor-neutral normalized desired-policy export | selected wave must determine concrete enforcement placement |
| Technical Access Evidence / configured-state reconciliation | J7 exports desired policy directly; no configured-vs-desired conclusion | selected wave must compare desired policy with observed/configured state |
| Configuration Rendering/vendor syntax | `Normalized Policy Export -> future renderer` | selected wave needs implementation-ready target/vendor representation |
| firewall/provider execution | future execution consumes rendered representation | selected wave must mutate managed devices/providers |
| execution retry/rollback/partial/unknown result | no device mutation in Wave 1 | execution becomes selected behavior |
| target-specific disable/remove/recreate mechanics | `Inactive` is domain desired-effect semantics only | renderer/executor must express operational suspension on a concrete target |
| richer Rule states beyond `Active/Inactive` | Wave-1 operational state remains binary | selected behavior requires distinguishable additional operational lifecycle states |
| rich Change Management/revocation workflow | direct domain mutations only with authority/audit | selected wave requires planned/batched change lifecycle independent of Rule state |
| numeric performance/availability SLA | no unsupported G2 numeric requirement | accepted workload/SLA/migration profile or architecture feasibility requires numeric envelope |

## Guardrails

- Deferred Decision Domain concepts must not be invented by Access Policy or architecture.
- Deferred rendering/execution must not redefine Rule identity, decision semantics or normalized desired-policy meaning.
- Legacy mechanisms are evidence/transition concerns, not implicit greenfield requirements.
- A later wave may promote a deferral only by updating the owning requirement/decision artifacts and, if boundaries materially change, Strategic DDD readiness.

## WP-07 result

Every touched out-of-Wave behavior has an explicit D0 seam and revisit trigger. No known deferral is required to make the selected Wave-1 propose -> decide-consume -> manage -> normalized-export behavior testable.
