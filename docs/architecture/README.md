# Architecture map

This directory contains current target architecture only.

Start with the smallest relevant artifact:

- `current-architecture.md` — cross-cutting target structure, dependency/ownership rules, runtime boundary and architecture drivers.
- `code-structure.md` — current backend/Web physical taxonomy, ownership boundaries and executable structural enforcement.
- `application-catalogue-target-boundary.md` — target ACC compatibility projection, cross-context dependency ports and external-correlation boundary.
- `scoped-connectivity-inventory.md` — target Scoped Connectivity Inventory application/read composition.
- `technical-access-evidence-boundary.md` — Technical Access Evidence boundary.
- `network-enforcement-placement-boundary.md` — Network Enforcement Placement boundary.
- `enterprise-identity-authoritative-sources-boundary.md` — local-first runtime with dormant external identity/source extension seams.

Connectivity Requirements, Connectivity Decision and Requirement-to-Policy Alignment target architecture documents were removed after ADR-019/global Strategic convergence replaced those semantics with Business Connectivity, Access Governance and the current policy/materialization chain. Their executable remnants belong to current-state/migration documentation, not this target architecture index.

Access Policy Realization architecture is currently being redesigned from the single problem statement in `../domain/access-policy-realization/README.md`. No separate APR architecture contract is current until that revalidation is completed.

Consequential choices are recorded in `docs/decisions/`. Product behavior belongs in `docs/requirements/`; architecture should reference those contracts rather than restate them.

Historical implementation/design packets are not current architecture. Git history is the archive; only migration-relevant current-state facts should remain in the working documentation corpus.
