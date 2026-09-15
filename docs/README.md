# NAPMS documentation

The working documentation tree is the project specification for the system as it exists and as it is currently designed to evolve. It must be sufficient to reconstruct the designed system from zero without inventing product, domain or architecture decisions.

Two kinds of current truth may coexist and must be labelled explicitly:

- **as-built** — the accepted design contract for capabilities that exist in the current product/runtime;
- **target** — the accepted design contract for the current intended model when it differs from as-built or is not implemented yet.

Implemented does not mean historical. A requirement, architecture contract, API contract, persistence decision, UI specification or ADR remains in the working tree while it is required to reproduce the current designed system.

Documentation ownership:

- `requirements/` — current product and quality contracts, including implemented/as-built behavior and current target behavior;
- `domain/` — current Strategic/Tactical DDD, semantic ownership and target/as-built domain contracts where both are needed;
- `architecture/` — current as-built and target architecture, boundaries, composition and structural constraints;
- `decisions/` — design decisions still required to understand or reproduce current as-built/target architecture; superseded-only decision history does not belong here;
- `engineering/` — current API, persistence, runtime, configuration, operational and implementation-facing contracts;
- `ui/` — current UI requirements, screen/wireframe specifications and reusable design guidance;
- `plans/active/` — selected execution state only;
- `process/` — reusable development and agent protocols.

The selected next implementation MVP is `requirements/first-mvp-vendor-neutral-policy-export.md`; its execution state is `plans/active/README.md`. The slice starts from current effective Access Policy truth and composes AP + ACC + AD + RC into one complete vendor-neutral table/export without firewall/device/provider context. That narrower next slice does not invalidate project documentation for already implemented capabilities or for the broader accepted target model.

Git history is the archive only for genuinely replaced material: superseded specifications that no longer describe any current as-built or target state, completed migrations, completed plans/checkpoints, audit snapshots and obsolete alternatives.

## Reconstruction test

Before deleting project documentation, ask:

> If production code disappeared, would the remaining documentation still let a competent team reconstruct the designed current system and distinguish as-built from target without making a new product/domain/architecture decision?

If the answer becomes no, the document or its still-required content must remain in the working project specification.
