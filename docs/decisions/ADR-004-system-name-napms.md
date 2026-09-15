# ADR-004 — System name NAPMS

Status: `accepted`.

Date: 2026-09-08.

## Context

The new product repository represents a concrete information system rather than only the management discipline or one Bounded Context. The former working name NAPM was ambiguous between the product and the activity "Network Access Policy Management".

## Decision

Use **Network Access Policy Management System (NAPMS)** as the product/system name.

Repository and Python package use `napms`.

Bounded Context names remain semantic names such as Access Policy, Authority Management and Application Communication Catalogue; they are not renamed to match the system acronym.

## Consequences

- NAPMS denotes the whole product/system.
- Access Policy remains one Bounded Context within NAPMS.
- Legacy names and the old working `napm` package name are not carried into the new codebase.
