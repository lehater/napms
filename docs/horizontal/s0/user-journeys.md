# NAPMS full-width user journeys

Status: CANDIDATE / non-canonical / S0 reconstruction from accepted `docs/**`.

These journeys describe user/operator problems and observable outcomes. They intentionally do not assign Bounded Context ownership or prescribe transport/persistence/UI implementation.

## J1 — Curate application communication knowledge

A catalogue curator needs to register an Application, its Components and the directed communication definitions between Components, including complete traffic alternatives, so later connectivity reasoning can refer to stable application semantics rather than reconstructing intent from addresses.

Expected outcome: stable application/component/interaction identities and resolvable immutable communication revisions; historical references remain explainable.

## J2 — Record concrete application deployment

A curator/operator needs to record that a concrete Component instance is deployed on a concrete Resource so policy can govern actual deployed endpoints without making deployment identity part of reusable application communication meaning.

Expected outcome: independently governed ComponentDeployment identities connect Component semantics to Resource realization; replicas can be represented independently.

## J3 — Curate resource realization and responsibility

An operator needs to find or create a Resource, understand its current realization, scope affiliations and responsibilities, and change those temporal facts without rewriting history or implying that responsibility grants authority.

Expected outcome: current facts are easy to find, missing facts remain explicit, and historical/provenance information remains available.

## J4 — Express business connectivity need

A business/application stakeholder needs to state why an application interaction is needed and preserve that justification as deployments or communication revisions evolve.

Expected outcome: deliberate policy work has an explicit business basis, while the Need itself does not grant access.

## J5 — Propose and decide concrete access

An authorized actor needs to propose a concrete source-to-destination deployment access change using an exact application communication revision, receive a formal decision, and understand what policy is currently effective without pending/rejected attempts overwriting it.

Expected outcome: proposed, accepted/rejected, effective and withdrawn truth remain distinct and historically explainable.

## J6 — Recognize brownfield access from evidence

A security/network user needs to start from technical evidence, correlate it to known Resources, deployments and application communication semantics, and see whether a recognizable access candidate exists even when business attribution is not yet known.

Expected outcome: recognized, ambiguous and unresolved outcomes are explicit; evidence never manufactures authorization or desired policy.

## J7 — Investigate an explicit technical traffic tuple

A user needs to analyze `source address + destination address + protocol + port/range + asOf` and inspect the available cross-context picture: attribution, business/policy state, candidate enforcement context, responsibility and stored technical evidence.

Expected outcome: `Required`, `Allowed`, effective policy, configured evidence and network relevance remain separate facts; multiple/ambiguous matches remain visible; historical analysis does not use evidence from an invalid later time.

## J8 — Inspect scoped connectivity inventory

A user needs a resource-centric view of connectivity in a selected scope, including Resources/deployments with zero connectivity, without the read view becoming a new authority over its source facts.

Expected outcome: owner facts remain traceable to their sources and absence/unknown states are not collapsed into denial.

## J9 — Materialize and export required policy

A policy/network user needs the current effective semantic access transformed into complete source-neutral technical policy using the exact communication revision, concrete deployments, Resource realization and relevant enforcement placement.

Expected outcome: a coherent complete export is produced or the result is explicitly unresolved; partial selected policy is not presented as complete. Alternate representations of one export carry the same materialized truth.

## J10 — Compare required and configured access

A security/network operator needs to compare required effective policy with trustworthy configured-effective policy and distinguish common, missing and excess access.

Expected outcome: incomplete inputs remain explicit; current remediation may add verified missing access, while excess does not silently become removal authority.

## J11 — Render and execute a verified network change

A network operator needs a verified source-neutral change intent rendered for the target provider/environment and executed as a controlled mutation with authority, preconditions, outcome and provenance.

Expected outcome: provider representation preserves intent; execution failure/unknown remains explicit; execution success is not confused with later convergence verification.

## J12 — Explain and verify convergence

An operator needs to determine after execution whether configured-effective access actually converged toward required access and explain any remaining delta from authoritative evidence.

Expected outcome: `Executed` and `Verified` remain separate states and the system does not infer convergence from command acknowledgement alone.

## J13 — Operate and recover the supported product

A product/operator user needs to diagnose supported runtime operation, correlate failures safely, and recover durable NAPMS-owned state without confusing runtime logs, ephemeral state or external-provider state with authoritative product truth.

Expected outcome: operation/recovery has explicit success/failure evidence and clearly bounded recovery claims.

## J14 — Integrate enterprise authoritative sources when required

An enterprise deployment may need to correlate external identity or catalogue/inventory authority with NAPMS-owned semantics while preserving provider-qualified source identity and fail-closed ambiguity handling.

Expected outcome: external source truth terminates at an explicit context-owned boundary; authentication/correlation does not silently become business authorization.

Disposition: documented extension seam; current supported product may remain local-first without external authoritative systems.

## Deferred journey extensions

The accepted documentation also retains future journeys around customer-specific approval procedures, richer authority models, multiple simultaneous Resource addresses/interfaces/VIPs, Prefix-aware enforcement placement, richer deployment/runtime history, managed policy narrowing/removal, additional provider/evidence integrations and richer enterprise-source synchronization. They remain project problem space but are not promoted to current baseline behavior by this reconstruction.
