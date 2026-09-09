# I15 WP1 — Connectivity Decision semantic decision packet

Status: `working proposal`.

Date: 2026-09-09.

## Design objective

Choose the smallest durable model that explains who may produce an `Allowed | NotAllowed` result, why it exists, when it may be consumed and how a later reconsideration is represented, without inventing an approval bureaucracy.

## Proposed decisions

### D1 — Semantic owner

Promote **Connectivity Decision** to a first-class Bounded Context.

Reason: decision identity, reason/provenance, validity, reconsideration and decision authority form an independent consistency/lifecycle boundary. Access Policy remains consumer of the final decision.

### D2 — Decision identity and subject

One `ConnectivityDecision` has:
- stable `DecisionId`;
- exact `RuleSemanticIdentity` subject;
- stable Decision Governance Scope equal to the accepted proposal authority scope in the first model.

Decision identity is not the Rule semantic identity. Multiple historical decisions may exist for the same subject/scope.

### D3 — Outcome vocabulary

Business outcome remains exactly:

`Allowed | NotAllowed`

No `Pending/Approved/Rejected` lifecycle is introduced. Absence of an effective decision is absence/unknown at the application boundary, not a third business decision result.

### D4 — Participation and Authority

Authority Management admits independent actions:
- `DecideConnectivity`;
- `ReadConnectivityDecision`.

`ProposeConnectivity` never implies `DecideConnectivity`.

A decision actor may be a human principal or a trusted service principal. Human vs automatic mechanism does not change Decision meaning.

First model requires one unambiguous effective `DecideConnectivity` authority. Quorum/SoD is deferred until a concrete product rule requires it.

### D5 — Validity

A Decision carries an offset-aware half-open validity interval:

`[validFrom, validUntil)`, with optional `validUntil`.

Access Policy may consume a decision only when it is effective at the proposal logical time.

Validity governs decision consumption. It does not silently mutate a Rule already materialized from an earlier Allowed decision.

### D6 — Reason and evidence

Every final decision records:
- non-empty stable reason code;
- non-empty human-readable reason;
- zero-or-more opaque evidence references.

Evidence may reference a Connectivity Requirement, policy/risk/compliance fact or another authoritative source. Referenced evidence remains owned by its source context.

A Connectivity Requirement may support a decision but never authorizes by itself.

### D7 — Provenance

Every decision records:
- deciding actor/principal;
- decision time;
- authority reference;
- proposal/subject correlation sufficient to explain what was decided.

### D8 — Reconsideration and supersession

Decisions are immutable.

Reconsideration creates another Decision for the same subject/scope and explicitly references the immediately superseded Decision.

At one logical time, the domain must not present multiple current effective Decisions for the same subject/scope. Ambiguity fails closed.

Supersession does not rewrite historical Decision records or historical Access Rule provenance.

### D9 — Relationship to Access Policy

For a valid proposal:
- effective `Allowed` -> Access Policy may materialize/resolve the Rule;
- effective `NotAllowed` -> no new materialization from that proposal;
- absent/expired/ambiguous decision -> fail closed as decision unavailable/unknown.

A later Decision change does not automatically change an existing Rule's operational state in I15/I16. Such revocation/change-management semantics require an explicit later requirement rather than a hidden cross-context side effect.

## Explicit deferrals

- multi-step approval cases/work queues unless I16 needs a user-managed pending process;
- quorum and separation-of-duties;
- automatic policy engine internals;
- decision-driven automatic Rule revocation;
- enterprise identity/source integration.
