# Coding-Agent Challenge 07

Status: FAILED — value-object normalization and request provenance require repair

## CAC-014 — P1 — TrafficClause protocol/port semantics underspecified

Current closure allowed a “normalized protocol name or IANA number” and said ports are allowed for protocols whose semantics use ports. A coding agent still had to choose:
- accepted aliases/names;
- canonical representation;
- which protocol numbers are treated as port-bearing;
- how unsupported port-bearing protocols such as SCTP are handled.

Repair decision:
- HTTP/domain canonical protocol is `ipProtocol`: integer 0..255 (IPv4/IPv6 Next Header / IP protocol number);
- selected MVP permits source/destination port ranges only for TCP(6) and UDP(17);
- for every other ipProtocol, both port arrays must be empty;
- protocol-only semantics for other numbers are representable;
- semantics requiring extra protocol-specific fields (for example ICMP type/code or SCTP port semantics) are outside the selected representation and must be rejected if the caller attempts to express them through ports/unsupported fields, never approximated;
- no protocol name aliases exist at the canonical HTTP boundary.

## CAC-015 — P1 — Host/Prefix normalization could silently change access meaning

Current closure allowed HostAddress/Prefix but did not decide IPv4/IPv6, canonicalization or host bits in a prefix.

Repair decision:
- both IPv4 and IPv6 are supported;
- HOST value is a single IP literal only, no CIDR suffix;
- PREFIX value is CIDR;
- input is parsed and emitted in canonical textual form using standards-compliant IP parsing;
- a PREFIX whose host bits are not zero is rejected rather than silently masked, because masking could broaden/narrow intended access;
- IPv4-mapped IPv6 textual forms are preserved/canonicalized as IPv6 according to the chosen standards parser rather than silently converted to IPv4 identity;
- address family is not part of Resource identity and source/destination families may differ at semantic storage level; provider feasibility is downstream/non-MVP.

## CAC-016 — P1 — export authorization evidence lacked request actor/time

Source requires end-to-end provenance from semantic request/intention through permission decision to current policy output.

Current AuthorizationEvidenceView exposed AccessRequestRef + decision actor/time but omitted request submitter/time.

Repair decision:
- AuthorizationEvidenceView includes `submittedBySubject`, `submittedAt`, `initialNeedRef` in addition to decision provenance;
- values are read from immutable AccessRequest owner state;
- export MaterializedRuleProvenance therefore explains request + decision + business justification without policy.read;
- no duplicate mutable source of request provenance is required.

Freeze remains prohibited until Domain/Interface/Data/Component/Verification/Test/Implementation are synchronized and Challenge 08 passes.
