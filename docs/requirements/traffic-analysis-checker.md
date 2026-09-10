# Traffic Analysis Checker Requirements — I26

Status: `accepted requirements baseline for planned I26`.

Date: 2026-09-10.

## Purpose

Define observable behavior for the technical-entry-point analysis currently code-named **Checker**.

Checker answers: given a technical traffic tuple, what does NAPMS know about the corresponding domain connectivity, policy/governance context, relevant network enforcement candidates, imported technical rules/evidence, and operational ownership/contact context?

Checker is a read/application composition over existing semantic owners. It does not become a new source of business or technical truth.

## REQ-CHK-001 — Technical traffic tuple is the primary input

Checker shall accept:
- source address;
- destination address;
- protocol;
- port or port range;
- explicit offset-aware `asOf`.

The first UI may use exact host addresses while the read contract remains extensible to CIDR/range predicates.

## REQ-CHK-002 — Resolve technical identities to domain context

Checker shall resolve the queried technical endpoints, when supported by current catalogue facts, to the corresponding Endpoint, Resource and application/component context.

Resolution shall distinguish at least:
- resolved;
- ambiguous;
- unknown;
- historical/not-current.

Ambiguity or missing mapping shall not be converted into an authorization claim.

## REQ-CHK-003 — Present the governance/policy chain without collapsing owners

For matching semantic connectivity, Checker shall present available Requirement, Connectivity Decision, Access Rule and Effective Policy facts while preserving their existing meanings and owners.

`Required`, `Allowed`, authoritative Access Rule state and configured technical evidence shall remain distinct facts.

## REQ-CHK-004 — Network Context is a candidate set, not a proven path

For the Checker use case, the available Network Context shall be presented as a set of relevant enforcement/network candidates for the queried traffic.

The product shall not claim that the candidates form a proven forwarding path, shall not invent an ordering between them, and shall not state that traffic definitely traverses a candidate unless a separately owned stronger source proves that fact.

The candidate set may be incomplete and may contain false positives. Where source semantics permit, Checker shall expose relevance/quality, provenance, ambiguity and knowledge-gap information rather than hide uncertainty.

## REQ-CHK-005 — Show technical rule evidence per network candidate

For each relevant enforcement/network candidate, Checker shall present technical access entries from stored Technical Access Evidence that match or overlap the query.

Checker shall not synchronously query live firewalls or devices to obtain rule lists.

## REQ-CHK-006 — Evidence is snapshot-based and explicitly dated

Configured technical rules shown by Checker shall come from the latest applicable stored evidence snapshot available for the requested `asOf`.

The result shall expose, when available:
- evidence/snapshot reference;
- evidence source/provider realization;
- captured-at timestamp;
- ingested/recorded-at timestamp when owned by the evidence source contract;
- provenance;
- source completeness/knowledge limitations.

The UI shall present such rules as last-known evidence, not as a guaranteed live device state.

## REQ-CHK-007 — Traffic matching supports containment and overlap

Rule/evidence matching shall not require literal tuple equality.

The backend shall provide deterministic matching semantics sufficient to distinguish exact coverage, broader/narrower containment, partial overlap, no match and unknown/ambiguous cases across supported address/protocol/port predicates.

The Web UI shall consume this semantic result rather than reimplement packet-set algebra independently.

## REQ-CHK-008 — Present operational ownership/contact context

For resolved source and destination resources, Checker shall present available operational responsibility information needed to identify who owns or supports the affected service/resource.

The model shall allow responsibility to refer to a person or team and shall distinguish resource responsibility/contact roles from Authority Management action authority.

Expected roles include, at minimum where data exists:
- service owner;
- technical owner;
- operations/support contact;
- responsibility scope.

Absence of owner/contact data shall be represented as unavailable/unknown rather than fabricated.

## REQ-CHK-009 — Full projection is one composition; presentation may be role-oriented

Checker shall expose one owner-preserving composed read model.

The Web UI may later choose different default tabs, density or field visibility for network operations, security/governance, application ownership or assurance users. Role-oriented presentation shall not create separate domain truth models or separate incompatible Checker APIs.

## REQ-CHK-010 — Historical analysis is time-consistent

For an explicit historical `asOf`, endpoint/resource mappings, policy/governance facts, Network Context candidates and Technical Access Evidence shall be selected according to their owning temporal contracts.

A future snapshot shall not be used to answer an earlier historical query merely because it is currently the newest snapshot.

## REQ-CHK-011 — Initial UI structure

The first Web slice shall provide a dedicated Checker/Traffic Analysis workspace with:
- query input;
- Overview;
- Network Context;
- Policy;
- Ownership;
- Evidence.

The UI shall be implementable first against deterministic fixtures/stubs so that information architecture and uncertainty states can be validated before every backend composition seam is complete.

## REQ-CHK-012 — Required first-slice states

The first implementation shall exercise, at minimum:
- fully resolved traffic with matching policy and evidence;
- ambiguous or unknown technical-to-domain resolution;
- multiple relevant network candidates;
- candidate with weak/possible relevance;
- matching configured evidence with explicit snapshot time;
- desired/authorized traffic with missing configured evidence;
- configured evidence without matching authorization;
- overlapping/broader technical rule match;
- missing ownership/contact information;
- incomplete/unknown evidence.

## Explicit non-goals for I26 planning baseline

The Checker requirement does not require:
- live firewall/device queries;
- a proven ordered network path from current Network Context;
- real provider/device transport;
- automatic remediation;
- hard-coded user job-title roles;
- automatic freshness trust decisions without an accepted freshness policy;
- a new Checker bounded context or independent persistence of composed truth.
