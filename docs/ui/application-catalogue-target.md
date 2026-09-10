# Application Catalogue target UX

Status: `accepted target; implementation pending`.

Date: 2026-09-10.

Canonical target domain decision: `docs/decisions/ADR-012-application-definition-deployment-model.md`.

Canonical screen-layout contract: `docs/ui/application-catalogue-wireframes.md`.

## Applications / Definitions

Dense server-backed table:

```text
Name | Domain | Components | Interactions | Deployments
```

Controls:
- search;
- primary filters plus `More filters`;
- sortable columns where useful;
- server paging;
- `Add application`.

Normal lists exclude Retired rows.

## Application Definition detail

Tabs:

```text
Overview | Components | Interactions | Deployments
```

### Components

Dense table:

```text
Name | Type | Description
```

No normal `Status` column. Retired Components are excluded from the normal list.

Component create/edit uses a compact drawer/panel while fields remain simple.

### Interactions

One row represents one component-pair interaction definition:

```text
Source | Destination | Traffic | Deployments
```

`Traffic` may contain multiple protocol/port alternatives. Short values render inline; large sets render a compact summary and drill down.

Create/edit owns source Component, destination Component and traffic alternatives.

### Deployments

Definition-local deployment list:

```text
Company | Environment | Scope | Interactions
```

`Interactions` is shown as selected/defined count, for example `18 / 24`. Partial use is normal.

## Applications / Deployments

Global dense server-backed table:

```text
Application | Company | Environment | Scope | Interactions
```

Supports search, filters, sort and server paging for hundreds/thousands of rows.

## Application Deployment detail

The primary workspace is one connectivity table, not separate Binding/Interaction/Effective tables.

```text
Source Component | Source Resources | Destination Component | Destination Resources | Traffic
```

One row = one selected Interaction Definition in this Application Deployment.

Resource cells never concatenate arbitrary resource names. They render counts consistently:

```text
1 resource
12 resources
327 resources
```

The count is clickable. Clicking it opens the resource set for that interaction side in a server-paged/searchable/filterable Resource table.

Traffic uses the same progressive disclosure principle:

```text
TCP (80, 443)
UDP (53), TCP (53)
TCP (17 ports), UDP (6 ports)
```

### Deployment interaction detail

Compact detail/edit surface:

```text
Source
<Component> · <N resources>

Destination
<Component> · <N resources>

Traffic
<read-only Definition traffic>
```

`<Component> · <N resources>` is itself the drill-down/edit target. No separate `Manage` button is used.

### Add interaction

`Add interaction` selects one or more Interaction Definitions already belonging to the Application Definition. It does not author new traffic semantics and does not create an exception/override.

After selection, source and destination Resource bindings are curated in the context of that selected Deployment Interaction.

## Resource-set filtering

Resource-set membership is ACC truth, while Resource display metadata and effective Responsibility Scope remain Resource Catalogue truth.

The I31 executable surface supports Resource search and effective Scope filtering. A Resource `Type` filter is not exposed because Resource Catalogue does not currently own a Resource type/classification attribute; adding one requires a separate accepted Resource Catalogue domain change rather than inferring a type from technical realization.

## Scale rules

All potentially unbounded tables:
- use server-side paging/search/filter/sort;
- keep compact bounded row height;
- avoid unbounded wrapping and comma-separated collections;
- aggregate collections by count and use drill-down;
- keep shareable filter/query state in the URL where reasonable.

## Lifecycle UX

Hard delete is absent.

`Retire` is available only when there are no active incoming references. If blocked, the UI shows active dependency counts and allows drilling into those dependencies.

Retired entities are excluded from ordinary working lists and appear only where required to explain retained historical references.
