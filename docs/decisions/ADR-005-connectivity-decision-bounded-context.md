# ADR-005 — Connectivity Decision as a first-class bounded context

Status: `superseded by ADR-019`.

Date: 2026-09-09.

Superseded: 2026-09-14 after G1 revalidation established bilateral source/destination consent, explicit revocation and governance history as required behavior.

## Historical context

ADR-003 had deferred Connectivity Decision semantics during Wave 1. ADR-005 later introduced a first-class `Connectivity Decision` Bounded Context so the implemented product could replace a deterministic allow adapter with durable explainable `Allowed | NotAllowed` decisions.

The accepted model used one immutable final Decision for one exact subject/scope/time, with reason/provenance and supersession. It explicitly deferred pending approval, quorum/separation-of-duties and revocation semantics because those requirements were not then established.

## Why it was superseded

The 2026-09-14 stakeholder/G1 revalidation established materially different semantics:

- every ordinary access request requires independent source-side and destination-side approval obligations;
- grant requires both sides' consent;
- either side may withdraw current consent unilaterally;
- rejection of a pending request and revocation of existing authorization are different facts;
- historical approval provenance survives later role loss/revocation;
- a single global `Allowed | NotAllowed` record is insufficient to represent this lifecycle.

The old Connectivity Decision boundary therefore no longer owns the target authorization semantics.

## Superseding model

ADR-019 assigns:

- Process-backed application-semantic Need to **Business Connectivity**;
- Request, side decisions, bilateral grant, revocation and governance history to **Access Governance**;
- effective actor/action/scope authority to **Authority Management**;
- current authoritative Policy Rule truth to **Access Policy**.

Existing Connectivity Decision code/data remain migration/current-state evidence until later implementation work retires or transforms them.

## Historical relation to ADR-003

ADR-005 superseded ADR-003 for the 2026-09-09 model. ADR-019 now supersedes ADR-005 for the current target model; ADR-003/ADR-005 remain provenance for how the authorization model evolved.
