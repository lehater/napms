# Backend implementation completion criteria

Status: ACCEPTED after Source Corpus amendments 01–02

Depends on: `implementation-design.md`, Verification Strategy and Test Design.

IMPLEMENTATION may claim realization complete only when every item below has executable evidence.

1. **External contract** — every accepted HTTP route, DTO, status, Problem code, Location, ETag, correlation and Idempotency-Key rule exists exactly as Interface Design states.

2. **Source/domain validity** — cross-Application Interaction is accepted when both Components/traffic semantics are valid; no blanket same-Application rule exists anywhere in API/domain/schema.

3. **Aggregate concurrency** — Resource, Application, Interaction, BusinessProcess, AccessRequest and PolicyRule own exactly the versions declared in design; child objects cannot create alternative optimistic-concurrency semantics.

4. **Resource truth/history** — current address/Site/singular OWNER/singular ADMINISTRATOR and required history are preserved; replacement/no-op behavior is proven.

5. **Current-access identity** — exactly one PolicyRule exists per AccessSubject(source Deployment, destination Deployment, exact InteractionRevision); NeedRef and technical realization are not Rule identity.

6. **Permission evidence** — ALLOWED request finalization is atomic with Rule resolve/create, AuthorizationEvidence and initial Need justification; DENIED creates no Rule/evidence; concurrent equal subjects converge on one Rule.

7. **Business justification** — additional current matching Need can attach without new permission evidence or duplicate Rule; Need status is not copied as Access Policy truth; later Need retirement changes derived justification status only.

8. **Reconciliation** — zero current Need produces `NO_CURRENT_BUSINESS_JUSTIFICATION` and does not automatically deactivate/revoke Rule or make materialization incomplete by itself.

9. **Operational effectiveness** — first Rule is ACTIVE/unbounded; ACTIVE/INACTIVE and absolute effective window preserve Rule/permission identity; same operational values are no-op; evaluation uses inclusive lower/exclusive upper bounds.

10. **Policy selection/materialization** — all/current subset selection, nonEffective handling, exact endpoint/traffic expansion, COMPLETE/UNRESOLVED and stable issue semantics match Application/Interface Design. Only selected effective Rules impose realization completeness.

11. **Provenance** — normalized output preserves independent PolicyRule identity, authorization evidence, Need justifications/currentness/reconciliation, interaction/deployment/resource/endpoint realization provenance; technically equal independent Rules are not provenance-erased.

12. **Idempotency/concurrency recovery** — idempotency scope includes concrete target; same committed replay precedes current If-Match evaluation; different fingerprint conflicts; different targets do not collide; concurrent identical commands create at most one authoritative result; no automatic DB mutation retry.

13. **Persistence ownership** — PostgreSQL schema/migrations match Data Design: no cross-owner write coupling/FKs, no false `interaction.application_ref`, unique AccessSubject Rule, evidence/justification uniqueness, temporal history and owner-local constraints.

14. **Security** — OIDC invalid credential vs unavailable-validation dependency distinction, exact operation permissions, request/decide/manage/read/export separation, secret handling and Security Analysis obligations are proven.

15. **Operability** — startup-only configuration, unknown-key failure, no hidden required defaults, OIDC retry/cache policy, no mutation retry, structured evidence, health/readiness, cancellation, graceful shutdown and redaction are proven.

16. **Architecture/components** — dependency checks prove domain independence from adapters, API independence from repositories, Interaction independence from Application write ownership, Access Policy non-ownership of Need currentness, and read-only Policy Materialization.

17. **Executable Test Design** — every accepted Test Design contract has evidence at its required domain/application/PostgreSQL/API/security/operability level.

18. **Fresh start** — all migrations initialize an empty PostgreSQL database and the complete public-HTTP journey (including cross-Application Interaction) succeeds without manual database fabrication.

19. **No downstream redesign** — source code/tests introduce no new product/domain/architecture/interface/data/security/operability/verification semantic convention absent from accepted closure.

Any failure remains implementation/evidence work unless it exposes a genuine upstream semantic gap. A genuine gap reopens its owning Authority and invalidates IMPLEMENTATION COMPLETE until repaired.
