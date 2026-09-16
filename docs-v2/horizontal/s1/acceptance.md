# NAPMS full-width acceptance outcomes

Status: CANDIDATE / non-canonical / S1 acceptance reconstruction from accepted `docs/**`.

These outcomes validate observable product semantics across the project breadth. They intentionally avoid HTTP, persistence, package, framework and test-realization detail. They are not an implementation test plan.

## Catalogue, deployment and resources

- **ACC-01** — Given one Application with Components A and B, a directed A -> B Interaction can exist only within that Application; an attempted cross-Application Interaction is rejected.
- **ACC-02** — Given Interaction A -> B with revision K1, changing traffic semantics creates K2 while K1 remains resolvable and K2 still resolves A/B as the Interaction endpoints.
- **ACC-03** — Given an exact Interaction Contract Revision, its owning Interaction and endpoint Components are resolvable without a duplicate deployment identity inside ACC.
- **AD-01** — Given Component A deployed on Resources R1 and R2, two distinct Component Deployments exist; policy for the first does not automatically authorize the second.
- **AD-02** — Given deployment CD1 = Component A on R1, changing R1's Address Space does not change CD1 identity; redeploying A on R2 creates another deployment.
- **RC-01** — Given a Resource with no trustworthy current Address Space, the Resource remains visible/known and technical realization is explicitly unresolved.
- **RC-02** — At one logical time a Resource has zero or one effective Address Space; when present it is exactly HostAddress or Prefix.
- **RC-03** — Resource responsibility or scope affiliation alone neither grants protected-action authority nor accepts/rejects access policy.

## Business need and access-policy lifecycle

- **AP-01** — Given a deliberate access proposal, a valid Process-backed Connectivity Need is required; the system does not fabricate business justification.
- **AP-02** — Given exact revision K1 and source/destination Component Deployments, submission is valid only when the deployments' ComponentRefs match K1's Interaction source/destination Components.
- **AP-03** — Given a Rule Change in Pending, current effective policy remains unchanged until an explicit Accepted outcome.
- **AP-04** — Given a Rejected Rule Change, the prior effective revision remains effective and rejection does not create a semantic deny rule.
- **AP-05** — Given an Accepted initial Rule Change, its exact revision becomes current effective policy for the concrete deployment pair; no bilateral endpoint-approval model is implied.
- **AP-06** — Given an effective Policy Rule, withdrawal clears current effectiveness without rewriting historical Accepted decisions.
- **AP-07** — Given a withdrawn Rule, an old Accepted decision cannot silently reactivate it; a new explicit change/decision is required.
- **AP-08** — Given an external customer workflow, an admitted integration may record the same formal Accepted/Rejected outcome without AP reproducing that workflow's internal stages.

## Authority

- **AM-01** — Given a protected action and actor/action/scope/time authority is Denied or Unknown, the action fails closed.
- **AM-02** — Given Resource membership/responsibility but no effective action authority, protected access is not admitted.
- **AM-03** — Given effective action authority but no Resource membership in a requested inventory scope, authority does not manufacture Resource affiliation.

## Technical evidence and recognition

- **TAE-01** — Recording a trustworthy source-qualified capture creates immutable evidence with stable source/capture/time/provenance and creates no authorization or desired-policy conclusion.
- **TAE-02** — An identical retry returns the existing evidence identity/history; the same source/capture identity with different normalized facts conflicts rather than replacing history.
- **TAE-03** — Duplicate source records with identical normalized predicates remain separately traceable when they are distinct source facts.
- **TAE-04** — Unknown source observation time remains Unknown; NAPMS recording time is not presented as source time.
- **TAE-05** — Traffic-derived presence does not imply configured Permit and absence of observed traffic does not prove Block.
- **TAE-06** — If one source item cannot be normalized faithfully, a complete capture is not reported by silently accepting the representable subset.
- **TAE-07** — An empty configured capture proves only that the capture contains zero entries; it does not prove global absence of technical access without an accepted completeness model.
- **TAE-08** — TAE records/reads technical facts only; technical-to-domain interpretation is performed by recognition, not by TAE itself.
- **EAR-01** — Given technical evidence that correlates uniquely through Resource, deployment and application semantics, recognition may produce a Recognized Access Candidate without making it effective policy.
- **EAR-02** — Given missing or ambiguous correlation, recognition reports unresolved/ambiguous and does not manufacture Resource, deployment, Interaction, Need or authorization truth.

## Scoped inventory and analysis

- **SCI-01** — Given admitted read authority for scope S, only Resources actually affiliated with S are local inventory roots; authority does not define membership.
- **SCI-02** — A local Resource appears even when it has no Component Deployment or no current Address Space, with explicit empty/unresolved child state.
- **SCI-03** — Direction shown relative to a local deployment may be incoming/outgoing while canonical Interaction direction remains unchanged.
- **SCI-04** — Need, current policy effect, pending change and realization are separate dimensions; one is not inferred from another.
- **SCI-05** — If optional enrichment such as Need/policy/realization is unavailable while the base row is trustworthy, the base row remains and only the affected dimension is Unknown.
- **SCI-06** — Top-level paging/search/filter preserves Resource-root grouping and does not silently split one Resource into unrelated top-level records.
- **CHK-01** — Given a technical tuple and `asOf`, Checker preserves zero/one/many candidate matches and explicit ambiguity rather than selecting a convenient winner.
- **CHK-02** — Checker keeps Required, Allowed/effective-policy, configured evidence and enforcement/network relevance as separate conclusions.

## Required policy and vendor-neutral export

- **RPM-01** — Given current effective Policy Rules with complete ACC/AD/RC/NEP inputs, materialization produces technical required-policy facts from the exact accepted revision and concrete deployment pair.
- **RPM-02** — Given missing/incomplete required input for a selected effective rule, materialization is unresolved rather than silently omitting that rule from a supposedly complete result.
- **RPM-03** — Prefix remains valid upstream Resource truth even where a downstream HostAddress-only placement edge cannot resolve it.
- **EXP-01** — A successful full vendor-neutral export is complete for the selected current effective policy set; unresolved selected policy prevents a successful partial export.
- **EXP-02** — Table/JSON and CSV representations of one export derive from the same immutable materialized result and therefore cannot disagree because of independent live re-reads.
- **EXP-03** — Vendor-neutral export does not claim configured reality, provider rendering, enforcement placement certainty, mutation execution or convergence merely because required policy was materialized.

## Realization, provider integration and network operations

- **APR-01** — Given trustworthy comparable required and configured-effective policy, comparison reports common, missing and excess semantics independently of Rule Change decision states.
- **APR-02** — Missing required access may produce additive remediation intent; excess access remains report/audit evidence in the current baseline and does not create automatic removal authority.
- **APR-03** — Missing/untrustworthy comparison input yields explicit unresolved/unknown rather than empty required/configured policy.
- **PPI-01** — Provider-native configured material is not treated as a trustworthy configured-effective snapshot when source scope/completeness/freshness/unsupported semantics are insufficient.
- **PPR-01** — Rendering a verified source-neutral change preserves its intended semantics; provider representation cannot silently broaden or narrow the requested change.
- **NEO-01** — A network mutation requires admitted authority and explicit operation identity/preconditions; failed or unknown execution is not reported as success.
- **NEO-02** — Successful execution records outcome/provenance but is not itself final convergence proof.
- **VER-01** — Convergence is reported only after later trustworthy configured/evidence input demonstrates the expected effective result.

## Cross-cutting quality

- **QUAL-01** — Unknown, ambiguous, unavailable or subject-mismatched trusted input never silently becomes permission, absence, denial, empty policy or success.
- **QUAL-02** — Semantic retries do not create duplicate authoritative business attempts/identities, and stale concurrent mutation cannot overwrite newer authoritative state.
- **QUAL-03** — Protected failures disclose no unrelated protected data, credentials, raw infrastructure/vendor exceptions or stack traces.
- **QUAL-04** — Actor identity, protected-action authority evidence and authoritative decision time are trusted server/integration inputs rather than caller assertions.
- **QUAL-05** — Operational correlation/logging supports diagnosis but does not replace domain identity, audit history or authoritative provenance.
- **QUAL-06** — Supported durable product state has a documented recoverability path whose verification distinguishes restored NAPMS truth from ephemeral runtime and external-system state.

## Extension acceptance boundary

Deferred capabilities — richer approval workflow, concurrent pending-change conflict semantics, nested/ABAC authority, multiple simultaneous Resource addresses, Prefix-aware placement, managed narrowing/removal, richer deployment history and additional enterprise/provider integrations — are not required to satisfy the current baseline acceptance outcomes above. When promoted, they require explicit requirements and acceptance additions rather than reinterpretation of existing outcomes.
