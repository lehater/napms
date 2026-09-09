# Connectivity Decision Acceptance Examples

Status: `accepted I15 executable-specification baseline`.

Date: 2026-09-09.

## A1 — authorized Allowed decision

Given actor D has effective `DecideConnectivity` authority for scope S,
and proposal subject R is valid,
when D records `Allowed` for R/S with valid reason, validity and provenance,
then a new immutable DecisionId exists and the Decision is effective during its validity interval.

## A2 — proposal authority is insufficient

Given actor P may `ProposeConnectivity` for scope S but may not `DecideConnectivity`,
when P attempts to record a Decision,
then no Decision is created and the operation fails closed.

## A3 — NotAllowed is a valid business result

Given an effective `NotAllowed` Decision for exact subject R/scope S,
when Access Policy asks for a Decision at a time inside its validity,
then `NotAllowed` is returned for R/S and no new Rule is materialized from that proposal.

## A4 — requirement does not imply Allowed

Given an active applicable Connectivity Requirement exactly matching R,
and no effective Connectivity Decision exists,
when a proposal for R is evaluated,
then the Requirement may be cited as evidence but no Allowed result is inferred.

## A5 — expired decision is unavailable for consumption

Given Decision D is `Allowed` with validity `[T1,T2)`,
when the proposal logical time is T2 or later,
then D cannot authorize materialization.

An existing Rule previously materialized from D is not silently mutated.

## A6 — supersession preserves history

Given D1 is current for subject R/scope S,
when an authorized principal records D2 for the same R/S with `supersedesDecisionId=D1`,
then D1 remains unchanged in history and D2 becomes the candidate current Decision according to validity.

## A7 — supersession cannot change subject/scope

Given D1 is for R1/S1,
when a new Decision claims to supersede D1 but uses R2 or S2,
then the operation is rejected and D1 remains current.

## A8 — ambiguous current decisions fail closed

Given persistence/state would expose two non-superseded effective Decisions for the same R/S/asOf,
when a consumer selects the Decision,
then no Allowed/NotAllowed result is trusted and the outcome is explicit ambiguity/unknown.

## A9 — automatic and human principals have equal semantic outcome

Given a trusted service principal and a human principal each independently have valid `DecideConnectivity` authority,
when either records a valid Decision,
then the Decision semantics are identical; principal type does not redefine Allowed/NotAllowed.

## A10 — read authority is independent

Given actor R may `ReadConnectivityDecision` but may not `DecideConnectivity`,
then R may inspect Decision data admitted for scope S but cannot create/supersede a Decision.
