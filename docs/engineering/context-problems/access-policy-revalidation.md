# Access Policy — G1 Revalidation Evidence

Status: `non-authoritative stakeholder evidence / S1 revalidation input`.

Date: 2026-09-14.

## Purpose

Preserve stakeholder clarification of what is proposed, approved and materialized in Access Policy while the project performs breadth-first S0/S1/G1 revalidation across bounded contexts.

This file is not Tactical DDD and does not redefine aggregate identity, persistence or integration topology.

## Stakeholder clarification

Access is not authorized for IP addresses.

The authorization subject is a concrete interaction between two concrete Component Deployments under an already-described Application interaction contract:

```text
source Component Deployment
        +
destination Component Deployment
        +
existing described Interaction
```

A Component Deployment is one side of the interaction: a concrete Component of a concrete Application deployed on a Resource. The opposite Component Deployment is the other side.

When two Deployments correspond to Components for which an Interaction is already defined, that combination may form a candidate for an Access Rule. Before approval it is a proposal / rule candidate rather than an authoritative rule.

After that proposal is approved, it materializes as an authoritative Access Rule with its own stable identifier.

## S1 interpretation candidates

The following statements are candidate observable requirements for the Access Policy G1 pass:

- Authorization is attached to semantic interaction between concrete Deployments, not to their current IP addresses.
- A current or future address change of either Deployment does not by itself constitute approval of a different semantic interaction.
- A rule proposal can exist before authorization and must remain distinguishable from an authoritative Access Rule.
- Approval is the transition that allows the accepted proposal to materialize as an authoritative Access Rule.
- An Access Rule refers to the source Deployment, destination Deployment and an already-existing valid Interaction definition; it does not invent application communication semantics.
- Access Rule identity/state and current technical address realization are separate concerns.

## Boundary consequence

This clarification leaves a deliberate downstream seam:

```text
approved Access Rule
    = source Deployment + destination Deployment + Interaction
                |
                | unresolved ownership
                v
current Resource/Endpoint address realization
                |
                v
technical traffic pair(s)
                |
                v
Network Enforcement Placement
```

Access Policy has no reason, from this evidence, to own current address realization or firewall-placement reasoning merely because its rule is the authorization source.

The G1 cross-context review must assign responsibility for turning an authorized semantic rule into current technical traffic pairs before NEP can evaluate candidate enforcement locations.

## Terminology note

The stakeholder used the concept of a pre-approval "proposal" / "candidate rule" and a post-approval materialized "rule". Exact domain names and lifecycle mechanics remain S2 work; G1 only requires the user-visible distinction between proposed and authoritative/approved access.
