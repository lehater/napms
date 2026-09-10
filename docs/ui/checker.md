# Checker / Traffic Analysis UI — I26

Status: `implementation-oriented UI contract`.

## Purpose

Checker is the technical-to-domain lookup workspace for an explicit traffic tuple:

```text
source address + destination address + protocol + port/range + asOf
```

It presents the full available picture without collapsing owner facts into one generic status.

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
- source/destination resolution state;
- resolved resource/component/service context;
- requirement, decision, Access Rule and effective-policy summaries;
- relevant network-device candidate count;
- findings.

`Required`, `Allowed`, `Active`, configured evidence and Network Context relevance remain independent labels.

## Network Context

Network Context is an unordered list of relevant candidate devices/enforcement identities.

The UI shall never render candidates as a route or implied sequence. Deterministic list ordering has no network meaning.

For each candidate, show when available:
- device/provider realization identity;
- Logical Firewall / Enforcement Attachment identity;
- source relevance label without invented probability;
- provenance;
- last applicable configured-evidence snapshot;
- configured technical entries that match/cover/overlap the query.

The view shall state that candidate membership is not proof that traffic traverses the device and that an empty candidate set is not proof of no forwarding/no enforcement.

## Evidence

Configured firewall rules are read from stored Technical Access Evidence only. Checker shall not synchronously query a firewall/device.

For a selected snapshot show:
- snapshot/evidence-set identity;
- source/source scope;
- captured time when known;
- recorded time;
- matching technical entries;
- match relationship such as `Exact`, `CoversQuery`, `CoveredByQuery`, `Overlap` or `Unknown`.

The UI shall describe the snapshot as last-known configured evidence, not current device state. It may show neutral age-at-analysis but shall not invent a stale/fresh policy threshold.

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

All reads use explicit `asOf`.

Evidence captured or recorded after `asOf` shall not be shown as applicable to that historical analysis.

Mutation actions are outside I26 Checker.

## Current local target

The supported local target uses:
- PostgreSQL Resource Catalogue / Application Communication / Requirement / Decision / Access Policy data;
- PostgreSQL stored TAE configured snapshots;
- deterministic local Network Context candidate source;
- deterministic local Resource Responsibility source.

These stubs are explicit seams for absent external sources; they are not claims of enterprise/device integration.
