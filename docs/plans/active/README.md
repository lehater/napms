# Active execution

Current: `PLAN-I30-connectivity-request-decision-journey.md`
Goal: Validate J03 from connectivity need through final Decision to authoritative Rule without inventing an approval lifecycle.
Current task: WP-1 — executable browser baseline against accepted Request access / Requirement / Decision / Access Policy semantics.
Working mode: `user-journey-validation`.

## Read first

- `.agents/skills/user-journey-validation/SKILL.md`
- `docs/requirements/scoped-connectivity-inventory.md`
- `docs/requirements/connectivity-decision-core.md`

## Expand only if needed

- `docs/requirements/connectivity-requirements-core.md`
- `docs/requirements/access-policy-core.md`
- `web/src/features/connectivity/RequestConnectivityPage.tsx`
- `web/src/features/decisions/ConnectivityDecisionsPage.tsx`
- `tests/runtime/test_local_seed.py`

## Recovery facts

- J01 Application authoring and J02 Resource authoring are merged and remain browser regressions.
- Current accepted Request access orchestration may declare/reuse a Requirement and then immediately submit an Access Rule Proposal.
- Connectivity Decision has only final `Allowed | NotAllowed`; no persistent Pending/Approved request lifecycle is accepted.
- Seeded `local-demo` contains one ACC interaction `Demo Web Frontend -> Demo Orders API`, DCS `HTTPS Orders API`, TCP/443.
- Static candidate: local demo seed currently lacks `DecideConnectivity` and `ReadConnectivityDecision` authority actions.
- Static candidate: first Request access attempt without an effective Decision may leave an authoritative Requirement but fail the later proposal step.

## Gate

WP-1 closes only with executable evidence. Do not fix static candidates before proving which step blocks the user journey.

## Next

Create the smallest J03 Playwright baseline using only visible UI and the seeded local-demo fixture.
