# Deferred research — Connectivity Decision Domain

Status: `explicit D1 deferral with safe semantic seam`.

Date: 2026-09-08.

## Purpose

Preserve the unresolved internal domain behind the decision whether a concrete proposed Access Rule is allowed, without forcing premature concepts such as `approver`, `admissibility`, `authorization workflow`, `policy engine`, or a new Bounded Context into Wave 1.

## Current minimum contract

```text
AccessRuleProposal
    subject = complete proposed Access Rule semantic identity

ConnectivityDecision
    subject = same proposed semantic identity
    result  = Allowed | NotAllowed
    provenance = opaque source/reference where available
    reasonReference = opaque reference where available
```

Access Policy consumes the decision. It does not own how or why the decision was produced.

For Wave 1:

```text
Allowed
    -> Access Policy may materialize or resolve the authoritative Access Rule

NotAllowed
    -> no authoritative Access Rule is materialized from that proposal
```

The exact decision lifecycle is intentionally unresolved. Do not infer `Pending/Approved/Rejected/Revoked`, human approval, automatic approval, quorum, exception workflow, or policy evaluation until evidence requires them.

## What is explicitly unknown

Future research must determine the reasons and mechanisms behind `Allowed / NotAllowed`, including where applicable:

- security and business policies;
- data/security classification and trust boundaries;
- resource/application constraints;
- risk and compliance rules;
- business justification / necessity;
- exceptions and overrides;
- who or what is authorized to contribute facts, decisions or attestations;
- whether decisions are automatic, human-mediated or mixed;
- decision validity/effective time and what later changes invalidate or supersede a decision;
- whether multiple independent decisions are required;
- whether `admissibility`, `authorization`, `approval`, `review` or other terms are genuinely distinct domain concepts;
- whether the model/language/lifecycle/authority justifies a separate Bounded Context.

## Boundary guardrails for current Wave 1

- A human actor is not treated as the semantic reason for `Allowed / NotAllowed`; at most the actor participates in a future decision process according to rules/authority not yet modeled.
- Authority Management owns `who may perform which domain action for scope/time`; it does not own the connectivity decision reason.
- Access Policy owns authoritative Access Rule identity/state/properties and consumes the decision result; it must not invent security/governance reasons.
- Application Communication Catalogue owns the semantic communication contract used in the proposal.
- Resource/Application catalogues own their authoritative facts; Access Policy must not mutate those facts to make a decision pass.
- Technical realization changes remain distinct from semantic decision identity.

## Revisit trigger

Promote this research when one of the following becomes D1 for a selected wave:

- the product must explain *why* a proposal is allowed/not allowed;
- the product must execute or manage the decision workflow;
- policy rules, classifications, exceptions or decision validity become product-managed data;
- multiple decision authorities/roles must coordinate;
- current facts can change the applicability of an existing decision;
- architecture cannot proceed without knowing the decision-domain owner/lifecycle.

Until then the stable seam is only:

```text
Proposal -> ConnectivityDecision(Allowed | NotAllowed) -> Access Policy
```
