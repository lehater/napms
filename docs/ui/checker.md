# Checker / Traffic Analysis UI — I26

Status: `implementation-oriented UI contract`.

## Purpose

Checker is the technical traffic analysis and attribution workspace for an explicit traffic tuple:

```text
source address + destination address + protocol + port/range + asOf
```

It presents the available cross-context picture without collapsing owner facts into one generic status.

Checker terminology does not define the target Access Policy Realization domain model. APR target semantics are owned by `docs/domain/access-policy-realization/README.md` while revalidation is active.

## Screen structure

Top-level route: `#checker`.

Input fields:
- Source address;
- Destination address;
- Protocol;
- Port / range;
- explicit logical `As of`.

Result tabs:
- `Overview`;
- `Network Context`;
- `Policy`;
- `Ownership`;
- `Evidence`.

## Overview

Overview shows the compact cross-layer summary:
- source/destination attribution state;
- resolved resource/component/service context;
- requirement, decision, Access Rule and effective-policy summaries;
- relevant network-device candidate count;
- findings.

`Required`, `Allowed`, `Active`, configured evidence and Network Context relevance remain independent labels.

## Network Context

Network Context is an unordered list of relevant candidate devices/enforcement identities for this Checker use case.

The UI shall never render candidates as a route or implied sequence. Deterministic list ordering has no network meaning.

For each candidate, show when available:
- device/provider realization identity;
- target/policy locator information published by the network-context source;
- source relevance label without invented probability;
- provenance;
- applicable stored configured-evidence snapshot;
- configured technical entries that match/cover/overlap the query.

These Checker presentation semantics do not become APR target-selection semantics. APR receives supplied targets and does not reevaluate why they were selected.

## Evidence

Configured firewall rules are read from stored Technical Access Evidence only. Checker shall not synchronously query a firewall/device.

For a selected snapshot show:
- snapshot/evidence-set identity;
- source/source scope;
- captured time when known;
- recorded time;
- matching technical entries;
- match relationship such as `Exact`, `CoversQuery`, `CoveredByQuery`, `Overlap` or `Unknown` when supported by the Checker matching contract.

The UI shall describe the snapshot as stored configured evidence, not guaranteed current device state. It may show neutral age-at-analysis but shall not invent a stale/fresh policy threshold.

No applicable snapshot is `Unavailable/Unknown` evidence, not proof that no matching configured rule exists on the live device.

## Ownership

Ownership shows Resource Catalogue operational responsibility independently for source and destination resources:
- Service Owner;
- Technical Owner;
- Operations Contact;
- Business Owner;
- person/team identity and optional contact point where available.

Operational Resource Responsibility is not Authority Management action authority.

If one address maps ambiguously to multiple Resources, the UI must preserve each Resource candidate and its responsibility assignments rather than selecting one owner.

## Policy

Policy shows matching semantic connectivity and existing owner summaries:
- DCS / access summary;
- Requirement;
- Connectivity Decision;
- Access Rule;
- effective desired policy state;
- governance scope where available.

Multiple matching semantic connectivity projections are preserved and displayed as multiple matches; the UI shall not silently choose one.

## Historical mode

All reads use explicit `asOf` where the owning source supports historical selection.

Evidence captured or recorded after `asOf` shall not be presented as applicable to that historical analysis unless the owning evidence-time contract explicitly supports it.

Mutation actions are outside I26 Checker.

## Current local target

The supported local target uses:
- PostgreSQL Resource Catalogue / Application Communication / Requirement / Decision / Access Policy data;
- PostgreSQL stored TAE configured snapshots;
- deterministic local Network Context source where applicable;
- deterministic local Resource Responsibility source.

These local sources are explicit seams for absent external systems; they are not claims of enterprise/device integration.
