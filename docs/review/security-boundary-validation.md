# Security boundary validation — NAPMS

Status: research evidence only. Uses accepted design artifacts as authority; production code is not design evidence.

## Case

NAPMS first MVP is a long-running browser/HTTP modular monolith with PostgreSQL, backend-established session identity and Authority Management admission for protected actions. Canonical design already contains a security architecture and a STRIDE-oriented threat model.

## Existing ownership observed

Accepted security architecture owns:
- backend session as authenticated identity boundary;
- rejection of caller-supplied actor identity;
- local username/password + server-side session baseline;
- fail-closed protected-action admission through Authority Management;
- the rule that UI visibility/domain metadata do not substitute for admission.

It explicitly does **not** redefine Authority Management domain semantics.

The HTTP contract consumes the security architecture to represent authentication/admission externally. Persistence owns physical state. Threat analysis evaluates the accepted design and references controls rather than silently redefining them.

## Atomicity result

### SECURITY-ARCHITECTURE — PASS

Semantic cohesion: trust, identity and protected-action enforcement structure.

Independent change: authentication/session mechanism or enforcement placement can evolve while Authority Management entitlement semantics remain stable.

Public contract: HTTP/interface, quality, threat analysis, operability, verification and implementation consume the security boundary.

### SECURITY-ANALYSIS — PASS

The canonical threat model covers spoofing, tampering, repudiation, disclosure, denial-of-service and elevation-of-privilege against accepted system/security/data/interface decisions.

Its controls point back to owning artifacts. It also records production-edge protections, TLS topology, secret rotation/infrastructure hardening and external IdP threats as deferred/not applicable when the corresponding deployment/identity baseline does not exist.

This is materially different from choosing security architecture. Analysis can evolve as threats change and can create upstream Questions without owning the resolution.

## Ownership pressure tests

| Concern | Owner/result |
| --- | --- |
| Actor may perform action/scope | Authority Management / Product-Domain semantics |
| Actor identity source and trust | SECURITY-ARCHITECTURE |
| Admission placement/fail-closed enforcement | SECURITY-ARCHITECTURE |
| 401/403/public failure representation | INTERFACE-DESIGN |
| Session credential non-disclosure | Security constraint projected into Interface/Operability |
| PostgreSQL physical protection/state | DATA + deployment architecture, constrained by Security |
| Threat/control coverage | SECURITY-ANALYSIS |
| Diagnostic redaction/correlation | OPERABILITY-DESIGN consuming security constraints |
| Proof of bypass resistance/outcome separation | VERIFICATION/TEST-DESIGN |
| TLS termination/secret rotation | unresolved only when a production deployment baseline makes them applicable |

## Gap found in current generic Harness wording

The reference SECURITY-ARCHITECTURE catalog currently emphasizes authentication, identity, authorization boundaries, protected actions and trust zones. NAPMS plus the negative Nutrition case suggest the reusable boundary should be slightly broader: security-specific trust, identity, admission, protection and enforcement structure.

This must not make it a catch-all owner for privacy, configuration, storage, interface or reliability semantics.

SECURITY-ANALYSIS wording is directionally correct but a reusable skill should explicitly require:
1. threat/control coverage against accepted design;
2. applicability decisions;
3. owner routing for every discovered gap;
4. prohibition on silently repairing upstream design;
5. explicit deferred/not-applicable findings;
6. verification obligations derived from accepted controls.

## Blocking-question examples demonstrated

IMPLEMENTATION must not invent:
- trusted actor source;
- authorization/admission semantics;
- fail-open/fail-closed behavior;
- caller-vs-server ownership of security-critical identity/time/scope;
- public disclosure behavior when the interface contract is unresolved;
- secret/session handling where a credential lifecycle is required.

Private middleware structure, guard/helper syntax, framework exception classes and equivalent realization mechanics remain implementation freedom after the contracts are accepted.

## Harness conclusion from this case

The existing two-Authority split survives a real HTTP/session/authorization case. No broad SECURITY Authority or Core change is justified.

## Extended security-surface review

### Session and credential lifecycle

The accepted design chooses username/password authentication and a server-side session plus HTTP-only cookie, but does not define session expiry/idle timeout, rotation on authentication, logout invalidation, password storage/verification, credential provisioning/reset or concurrent-session policy. These are not private framework mechanics when they determine whether an old/stolen credential remains trusted. Applicable first-MVP properties must be accepted by Security Architecture before implementation.

### Browser request trust: CSRF / origin policy

A cookie-authenticated browser mutation surface creates a browser-to-backend request-trust question independent of Authority Management entitlement. Current design does not state how the backend distinguishes an intended mutation from a cross-site request carrying ambient credentials. This is a material P1 research finding: Security Architecture must accept a request-origin/anti-CSRF trust rule, or an architecture fact making the threat inapplicable, before implementation chooses SameSite/origin/token mechanics. CORS is realization/interface policy constrained by that trust rule, not the semantic owner.

### Transport and secrets

TLS termination topology is explicitly deferred until a production deployment baseline exists. That is coherent, but if accepted deployment permits non-local/untrusted transport, secure transport and cookie transmission constraints become Security/System Architecture blockers. Database credentials, session secrets (if needed) and bootstrap credentials are security-sensitive configuration: Security owns protection/lifecycle requirements; System/Deployment owns runtime source/topology; parsing APIs remain implementation freedom.

### Password protection

Because password authentication is accepted, password verifier storage is not merely optional hardening. Security Architecture must define a technology-neutral verifier requirement sufficient to prohibit recoverable/plaintext password storage and unsafe comparison. Concrete algorithm/parameters may come from accepted organizational policy; otherwise a project decision is required before production-grade implementation.

### Fail-closed and unsafe input

Authority Management already fails closed for unknown/ambiguous authority. Missing/invalid/unverifiable session identity likewise must not degrade to authorized execution. JSON/CSV/HTTP validation semantics remain with Interface/Application/Domain; Security Analysis checks injection/unsafe-interpretation threats and routes structural fixes to those owners rather than owning every validation rule.

### Supply chain

Package provenance/signing/vulnerability SLAs are not accepted project truth. They belong to Engineering Policy/organizational secure-development policy unless a specific dependency creates a project-specific threat.

## New blocking Questions discovered

The Authority split remains valid, but current security closure is insufficient for implementation of the authentication/session boundary without invention:

1. **SEC-Q-SESSION-LIFECYCLE** — what establishes session validity over time, rotation and invalidation/logout?
2. **SEC-Q-BROWSER-REQUEST-TRUST** — what anti-CSRF/request-origin rule protects cookie-authenticated mutations?
3. **SEC-Q-PASSWORD-VERIFIER** — what protection contract governs stored password verifiers and credential comparison?
4. **SEC-Q-SECRET-LIFECYCLE** — which runtime credentials/secrets exist and what source/lifecycle/protection constraints apply?
5. **SEC-Q-TRANSPORT-APPLICABILITY** — for which deployment boundary is TLS/secure-cookie transport required versus explicitly local/trusted-only?

These are Security Architecture gaps, with Interface/System/Data consumers where applicable; they do not justify new Harness Core entities.

## Revised pilot conclusion

Security Analysis is valuable precisely because it can invalidate a premature `security_questions_remaining: []` claim. It discovers missing architecture decisions and routes them back without taking ownership of their resolution.
