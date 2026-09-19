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
