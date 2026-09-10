# I30 — J03 Connectivity request to decision journey

Status: `active`

## Goal

Validate one cross-role connectivity journey without inventing a ticket/approval lifecycle:

1. requester identifies an exact ACC interaction in Connectivity;
2. requester records/reuses the Connectivity Requirement;
3. decision maker records a final `Allowed` Decision for the exact subject/scope with a reason and Requirement evidence where available;
4. requester resubmits the exact Access Rule Proposal;
5. the resulting Rule becomes visible as authoritative policy state.

The journey must preserve the accepted separation `Required != Authorized`, `Proposal != Decision`, `Decision != Access Rule`.

## Fixture

Use the seeded local-demo interaction:
- scope `local-demo`;
- Demo Web Frontend -> Demo Orders API;
- DCS `HTTPS Orders API` / TCP 443;
- requester and decision maker may be the same local demo principal only as a local single-account convenience; authority actions remain independent.

## WP-1 — Baseline

Execute the smallest browser path through Connectivity, Request access, Needs, Decisions and back to Connectivity/Rules. Record reproducible P0-P3 findings only.

Expected semantic gate to validate, not assume: the product has no accepted persistent waiting/approval lifecycle; therefore the UI must not invent Pending/Approved states.

## WP-2 — Route findings

- accepted implementation gap -> implement the smallest vertical slice;
- missing/conflicting workflow semantics -> stop implementation and route through the repository decision/domain-change protocol;
- demo authority/configuration gap -> fix only if it prevents exercising already accepted behavior.

## WP-3 — Regression

After P0/P1 closure, add deterministic browser coverage for the supported cross-role sequence and rerun J01/J02.

## Exit criteria

- supported J03 path is executable through normal UI without UUID entry or API/database bypass;
- requester can understand whether need, final Decision and Rule each exist;
- decision maker can identify the exact subject and record a final Decision with accepted authority semantics;
- no P0/P1 journey findings remain, or the journey is explicitly blocked by an unresolved product-semantic decision rather than papered over in UI;
- applicable core/Web/PostgreSQL/Harness/Knowledge/Docker/browser gates are green before integration.
