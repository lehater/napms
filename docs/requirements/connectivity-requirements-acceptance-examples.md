# Connectivity Requirements acceptance examples — I13

Status: `accepted I13 WP2 specification-by-example baseline`.

Date: 2026-09-09.

## Purpose

Make I13 behavior executable without choosing API, persistence, framework or deployment topology.

## R1 — Authorized declaration

Given:
- actor A has effective `DeclareConnectivityRequirement` authority for scope S at time T;
- Source Deployment X and Destination Deployment Y exist;
- immutable DCS revision D describes X -> Y;
- Dependent = X;
- applicability is Ongoing;
- justification is non-empty;
- no Active Requirement exists for S + X + (X,Y,D).

When A declares the need.

Then:
- one Active Connectivity Requirement is created;
- it receives one stable Requirement ID;
- S is stored as Requirement Governance Scope;
- declaration provenance includes A/T/S/authority reference;
- no Connectivity Decision or Access Rule is created as a side effect.

## R2 — Declaration authority is not permission

Given R1 succeeds.

Then the system still cannot conclude:
- `Allowed`;
- `NotAllowed`;
- Access Rule exists;
- access is configured.

Requirement existence means only that the semantic need is declared.

## R3 — Denied declaration

Given actor A lacks effective `DeclareConnectivityRequirement` authority for S/T.

When A attempts the same valid semantic declaration.

Then:
- declaration is rejected;
- no Requirement exists from that attempt;
- no business audit claims an accepted declaration;
- no Access Policy effect occurs.

## R4 — Unknown/ambiguous declaration authority

Given Authority Management cannot establish one unambiguous effective declaration authority for S/T.

Then declaration fails closed exactly as an unknown authority outcome.

No Requirement is created.

## R5 — Invalid ACC interaction

Given actor A has declaration authority, but D does not describe X -> Y.

When A attempts declaration.

Then:
- no valid Required Semantic Interaction exists;
- no Requirement is created.

## R6 — Dependent must participate

Given D validly describes X -> Y, but Dependent = Z where Z is neither X nor Y.

Then declaration is invalid and creates no Requirement.

## R7 — Mandatory justification

Given all semantic/authority facts are valid but justification is blank.

Then declaration is invalid and creates no Requirement.

## R8 — Idempotent repeated declaration

Given Active Requirement R already exists for S + Dependent X + interaction (X,Y,D).

When the same semantic need is declared again with the same or different applicability/justification.

Then:
- the existing Requirement ID R is resolved;
- no duplicate Active Requirement is created;
- the repeated declaration does not silently overwrite applicability/justification;
- property changes require their explicit commands.

## R9 — Concurrent duplicate declaration

Given two authorized declaration attempts race for the same active semantic key.

Then authoritative outcome contains exactly one Active Requirement ID.

Both successful/resolved callers must converge on that same ID.

## R10 — Applicability window boundaries

Given Active Requirement R has `AbsoluteWindow(start,end)`.

Then:
- at `asOf == start`, it is applicable;
- for `start < asOf < end`, it is applicable;
- at `asOf == end`, it is not applicable;
- outside the interval, it is not applicable.

The stored lifecycle state remains Active; applicability evaluation does not periodically mutate lifecycle.

## R11 — Authorized applicability change

Given R is Active and actor A has `SetConnectivityRequirementApplicability` authority for R's stored scope.

When A changes Ongoing -> AbsoluteWindow.

Then:
- Requirement ID is unchanged;
- Dependent and interaction are unchanged;
- the property change is business-audited with actor/effective-time/scope/authority reference.

## R12 — Same applicability is no-op

Given R already has applicability P.

When authorized actor sets P again.

Then:
- explicit no-op result;
- no duplicate property-change audit.

## R13 — Authorized justification change

Given R is Active and actor A has `SetConnectivityRequirementJustification` authority.

When A changes justification J1 -> J2.

Then:
- Requirement ID and semantic subject remain unchanged;
- J2 becomes authoritative;
- one accepted business-audit entry records J1 -> J2 and provenance.

## R14 — Identity-defining change is another Requirement

Given Active Requirement R for Dependent X and interaction (X,Y,D1).

When the business need becomes:
- Dependent Y; or
- X -> Z; or
- DCS D2.

Then R is not rewritten into the new subject.

A separate Requirement must be declared for the new semantic subject.

## R15 — Retirement

Given Active Requirement R and actor A has `RetireConnectivityRequirement` authority for R's stored scope.

When A retires R.

Then:
- R becomes Retired;
- the same Requirement ID/history remains;
- one lifecycle audit records Active -> Retired;
- no Access Rule is changed merely because R retired.

## R16 — Repeated retirement

Given R is already Retired.

When an otherwise authorized actor requests retirement again.

Then:
- explicit no-op;
- no duplicate lifecycle audit.

## R17 — Retired Requirement is immutable

Given R is Retired.

When an actor attempts to change its applicability or justification.

Then the mutation is rejected even if the actor otherwise has the relevant authority.

## R18 — Re-declaration after retirement

Given historical Requirement R1 for active semantic key K is Retired.

When an authorized actor later declares K again.

Then:
- a new Active Requirement R2 is created;
- R2 ID differs from R1;
- R1 history remains unchanged.

## R19 — Read authorization uses stored scope

Given Requirement R stores governance scope S1.

When caller requests R while supplying or implying another scope S2.

Then read authorization is evaluated only against stored S1.

Caller-controlled S2 cannot expose R.

## R20 — List ambiguity fails closed per scope

Given actor has unambiguous `ReadConnectivityRequirement` authority for S1 and ambiguous authority for S2.

Then list:
- may expose Requirements under S1;
- exposes no Requirement rows from S2;
- may report S2 as ambiguous without leaking its Requirement contents.

## R21 — Read does not imply mutation

Given actor can read R but lacks `SetConnectivityRequirementJustification`.

Then details may be returned, but changing justification is denied.

## R22 — Responsibility transfer preserves Requirement

Given R exists under governance scope S and Authority assignments later transfer from actor A to actor B.

Then:
- R ID/semantic subject/scope do not change;
- A may lose authority;
- B may gain authority;
- historical actions by A remain provenance.

## R23 — Persistence failure does not claim success

Given an authorized valid declaration/mutation but authoritative persistence fails before commit.

Then:
- operation is not reported as successful;
- no contradictory successful business truth/audit is claimed.

If commit outcome is unknowable, return explicit uncertain outcome rather than retrying as though no write occurred.

## R24 — Requirement creation has zero Access Policy side effect

Given there were zero Access Rules before a valid Requirement declaration.

After declaration:
- Requirement count may increase;
- Access Rule count remains zero.

This invariant is mandatory in core/runtime/PostgreSQL/Docker evidence.
