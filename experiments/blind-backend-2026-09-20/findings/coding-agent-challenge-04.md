# Coding-Agent Challenge 04

Status: FAILED — quality/interface consistency repair required

## CAC-009 — P1 — unbounded collection surfaces contradict Quality Design

Accepted Quality Design requires collection queries to be paginated/bounded even though no numeric performance SLO exists.

Current Interface Design embeds potentially unbounded collections:
- Resource endpoints;
- Application components;
- Interaction revision refs;
- BusinessProcess Needs;
- PolicyRule authorization evidence;
- PolicyRule justifications.

A coding agent would have to decide whether to:
- return unbounded arrays;
- invent hard cardinality limits;
- silently truncate; or
- design additional pagination endpoints.

Required repair:
- no silent truncation and no invented domain cardinality limit;
- growing read collections receive canonical cursor-paginated endpoints;
- parent/current views carry scalar state/counts, not unbounded child arrays;
- default/max page contract remains 50 / 200;
- materialization remains an export operation and may stream its normalized rows from one snapshot; RuleRef is the authoritative provenance correlation, while full evidence/justification audit remains available through paginated Rule endpoints.

## CAC-010 — P1 — Quality Design retained pre-amendment semantics

Quality Design still stated:
- first ALLOWED Rule materialization is idempotent “for one AccessRequest”;
- materialization coherence at a “requested logical asOf”.

Current accepted blind semantics are:
- one Rule per AccessSubject across multiple AccessRequests;
- server-owned current `evaluationAt`; caller historical asOf is unsupported.

Required repair:
- update Quality Design to the amended AccessSubject/evidence/justification/effectiveness model;
- include whole-Rule version scope;
- include cross-Application Interaction aggregate boundary;
- include bounded collection/read requirements consistent with Interface Design.

Freeze remains prohibited until repaired and Challenge 05 passes.
