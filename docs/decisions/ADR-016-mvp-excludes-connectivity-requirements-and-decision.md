# ADR-016 — MVP excludes Connectivity Requirements and Connectivity Decision

Status: `superseded by ADR-019`.

Date: 2026-09-12.

Superseded: 2026-09-14 after stakeholder G1 revalidation established Process-backed Connectivity Need and bilateral Access Governance as required MVP behavior.

## Historical context

The implemented product contained first-class `Connectivity Requirements` and `Connectivity Decision` bounded contexts modelling a declared connectivity need and a single immutable `Allowed | NotAllowed` decision before Access Rule materialization.

At the time of this ADR, the intended MVP was deliberately simplified to avoid forcing that existing `Requirement -> Decision -> Rule` workflow into the target model merely because it was already implemented.

## Historical decision

ADR-016 therefore removed both existing contexts from the then-current MVP target and allowed Authority Management-admitted creation of an Access Rule directly from a valid ACC subject.

That decision correctly rejected automatic preservation of the old CR/CD implementation boundaries, but its stronger assumption — that MVP did not require durable business Need or requester/approver governance capabilities — was invalidated by later stakeholder evidence.

## Superseding decision

ADR-019 retains the useful part of this ADR and replaces the obsolete part:

- the old `Connectivity Requirements` and `Connectivity Decision` Bounded Contexts are still not preserved as target boundaries;
- Process-backed application-semantic Need is now owned by **Business Connectivity**;
- request, bilateral side approval, authorization grant and revocation are now owned by **Access Governance**;
- **Access Policy** remains the owner of current authoritative Policy Rule truth rather than approval workflow history;
- current CR/CD runtime and documents remain migration/historical evidence until explicitly migrated or retired.

See `ADR-019-business-connectivity-and-access-governance-boundaries.md` for the current strategic decision and contracts.
