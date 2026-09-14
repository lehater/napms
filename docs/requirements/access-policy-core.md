# Access Policy product requirements

Status: `G1 revalidated target behavior; S2 lifecycle/details pending`.

Date: 2026-09-14.

## Purpose

Define externally observable Access Policy behavior after access governance has established or withdrawn authorization for one concrete semantic interaction subject.

Access Policy owns current authoritative Policy Rule truth and effective authorized-policy projection. Access request submission, bilateral approval/rejection, consent withdrawal and governance history are owned upstream by Access Governance and are not reimplemented inside Access Policy.

Exact aggregates, state machines, persistence and command mechanics remain S2 work.

## Authorization subject

A Policy Rule refers to one exact semantic subject published from trusted catalogue facts:

```text
source Component Deployment
+ destination Component Deployment
+ immutable Interaction Contract Revision
```

The referenced interaction revision must describe the directed interaction between the parent Components of the two Deployments.

Technical ResourceEndpoint/IP realization is not part of Policy Rule semantic identity. Address or Endpoint changes on the same Resource do not by themselves create a different authorization subject.

Changing either Deployment or materially changing the interaction contract requires a different authorization subject and renewed authorization.

## Authorization consumption

Access Policy consumes authorization semantics produced by Access Governance for the exact subject.

For ordinary access, a grant exists only after the required source-side and destination-side approval obligations are both satisfied with valid authority. A pending, rejected, ambiguous or authority-unknown request is not authorization.

Conceptually:

```text
source-side consent
AND destination-side consent
        -> Authorization Grant
        -> current authoritative Policy Rule truth

source-side withdrawal
OR destination-side withdrawal
        -> Authorization Withdrawal
        -> subject is no longer effectively authorized
```

Access Policy must not infer authorization from Resource ownership/administration, Connectivity Need existence, IP addresses or a legacy single global `Allowed | NotAllowed` decision.

## Authoritative Policy Rule

For one exact semantic subject there shall be at most one authoritative current Policy Rule meaning.

Requirements:

- the first effective authorization for a subject establishes an authoritative Rule with stable identity;
- repeated or concurrent processing of equivalent authorization grants must resolve the same authoritative Rule rather than create duplicates;
- multiple Connectivity Needs and multiple approved Requests may justify/provenance the same Rule without creating duplicate current Rules;
- a rejected Request creates no deny Policy Rule;
- Request/approval history is not encoded as duplicate Policy Rules;
- technical address/Endpoint changes do not redefine Rule identity;
- later governance-scope/responsibility metadata changes do not silently rewrite historical authorization provenance.

A withdrawal makes the subject no longer effectively authorized even though historical approvals and the Rule's historical identity/provenance remain explainable. Exact reactivation/revision/state representation is intentionally deferred to S2.

## Effective authorized policy

Access Policy shall expose the current effective set of semantically authorized Policy Rules for an admitted query scope/time.

The projection must distinguish:

- an authorized empty result;
- denied authority;
- unknown/ambiguous authority;
- technical/persistence failure.

A Rule contributes to effective authorized policy only while a valid current authorization basis exists for its semantic subject and any accepted applicability constraints are satisfied.

Time-bounded authorization is supported as product semantics, but this G1 requirement does not freeze one `EffectiveWindow`, state-machine or storage representation. S2 must choose a model that preserves the observable rule above.

Effective authorized-policy selection is Access Policy truth. Translation to Resource/Endpoint/address predicates, placement, configured-policy comparison, rendering and network execution are downstream concerns.

## Authorized reads and actions

Read authority is independent from mutation/governance authority.

The product shall:

- expose Rule data only when the actor is admitted for the relevant action/scope;
- distinguish not-found, denied and authority-unknown outcomes without leaking Rule data;
- keep request initiation, side approval/revocation, Policy Rule administration and network execution independently authorizable even when one actor holds several permissions.

Authority Management owns effective actor/action/scope evaluation. Access Policy consumes that result rather than inferring permission from owner/administrator metadata.

## Provenance and history

Policy Rule truth shall preserve enough correlation/provenance to explain why the subject is or was authorized without replacing the Access Governance journal.

At minimum, the system must be able to correlate current/historical Rule authorization with the relevant authorization grant/withdrawal basis and semantic subject.

Later loss of an approver's role must not rewrite a historically valid approval or Rule provenance.

Operational logs do not replace durable business provenance.

## Failure and safety behavior

The system fails closed when authorization or semantic-subject validity is unknown or ambiguous.

In particular:

- pending/incomplete bilateral approval -> no authorization;
- either-side rejection -> no authorization grant;
- unknown/ambiguous authority -> no successful authorization transition;
- authorization subject mismatch -> no Rule materialization/change;
- structurally invalid/unknown interaction subject -> no Rule materialization;
- uncertain persistence outcome is not reported as success unless the authoritative result is established.

## Acceptance examples

1. The source side approves but the destination side is pending: no effective Policy Rule authorization exists yet.
2. Both required sides approve the same subject: one authoritative Rule becomes current authorization truth.
3. Reprocessing the same grant or processing concurrent equivalent grants does not create duplicate Rules.
4. A rejected Request creates no deny Rule.
5. Several approved Requests/Needs for the same subject may correlate to one current Rule.
6. Either authorized side withdraws consent: the subject stops contributing to effective authorized policy without rewriting the original approved Request as rejected.
7. A later address or Endpoint change on the same Resource does not create a new Rule.
8. Replacing a source or destination Component Deployment requires renewed authorization for the new subject.
9. An authorized Rule whose technical address/placement evidence is currently unavailable remains semantic authorization truth; downstream realization reports it as unresolved rather than silently dropping it.

## Canonical references

- bilateral governance behavior: `docs/requirements/access-governance-g1.md`;
- business justification/Need behavior: `docs/requirements/business-connectivity-g1.md`;
- catalogue subject semantics: `docs/requirements/application-catalogue-domain-target.md`;
- realization/reconciliation behavior: `docs/requirements/policy-realization-reconciliation-g1.md`;
- current revalidation checkpoint: `docs/engineering/context-problems/capability-revalidation-checkpoint-2026-09-14.md`.

Older Connectivity Decision `Allowed | NotAllowed` requirements and ADR-005 remain historical/current-implementation evidence only where they conflict with this revalidated target behavior.
