# Application Catalogue target wireframes

Status: `accepted target; implementation pending`.

Date: 2026-09-10.

These wireframes define screen structure and information priority for the I31 Application Catalogue target. They are not pixel-perfect visual specifications.

## 1. Applications / Definitions

```text
Applications

Definitions | Deployments

[Search................................................] [Domain ▾] [Owner ▾] [+ Add application]

Name                 Domain          Components   Interactions   Deployments
CRM                  Business        14           24             8
Payments             Finance         9            17             12
Identity             Platform        11           31             6
...

                                      1–50 of 327   < 1 2 3 >
```

The list is server-backed. Counts are server projections; the client does not load child collections to calculate them.

## 2. Application Definition

```text
Applications / Definitions / CRM

CRM                                              [Edit] [⋮]
Business · Owner: team-crm

Overview | Components | Interactions | Deployments
```

### Components

```text
[Search................................................] [Type ▾] [+ Add component]

Name              Type            Description
Users             Service         User-facing entry point
Web               Service         Web frontend
API               Service         CRM API
Database          Database        Primary data store
...
```

### Interactions

```text
[Search................................................] [Source ▾] [Destination ▾] [Protocol ▾] [+ Add interaction]

Source       Destination     Traffic                         Deployments
Users        Web             TCP (443)                       8
Web          API             TCP (443)                       8
API          Database        TCP (5432)                      6
API          DNS             UDP (53), TCP (53)              4
...
```

### Deployments

```text
[Search................................................] [Company ▾] [Environment ▾] [Scope ▾] [+ Add deployment]

Company          Environment     Scope          Interactions
Company A        Production      Moscow         18 / 24
Company A        Test            Moscow         24 / 24
Company B        Production      SPb            12 / 24
...
```

## 3. Applications / Deployments

```text
Applications

Definitions | Deployments

[Search................................................] [Application ▾] [Company ▾] [Environment ▾] [Scope ▾]

Application      Company          Environment     Scope          Interactions
CRM              Company A        Production      Moscow         18 / 24
CRM              Company B        Production      SPb            12 / 24
Payments         Company A        Production      Moscow         17 / 17
...

                                      1–50 of 634   < 1 2 3 >
```

## 4. Application Deployment

```text
Applications / Deployments / CRM / Company A / Production

CRM — Company A / Production                       [Edit] [⋮]

Application     CRM
Company         Company A
Environment     Production
Scope           Moscow

Connectivity 18 / 24                              [+ Add interaction]

[Search................................................]
[Source ▾] [Destination ▾] [Protocol ▾] [More filters]

Source       Source resources   Destination   Destination resources   Traffic
Users        327 resources      Web           12 resources            TCP (80, 443)
Web           12 resources      API           24 resources            TCP (443)
API            5 resources      Database       2 resources            TCP (5432)
API            8 resources      DNS            4 resources            UDP (53), TCP (53)
API          119 resources      Gateway        7 resources            TCP (14 ports)

                                      1–50 of 18
```

One row is one selected Interaction Definition in this Application Deployment.

Resource collections always render a count. The count itself is the drill-down/edit target; no adjacent `Manage` action is shown.

No synthetic `Binding state` taxonomy is part of I31. Source/destination Resource counts expose the current effective membership directly.

## 5. Deployment Interaction detail

```text
Deployment interaction

API → Database

Traffic
TCP (5432)

Source
API · 5 resources

Destination
Database · 2 resources

                              [Cancel] [Save]
```

Traffic is inherited from the Interaction Definition and is read-only in Deployment.

`API · 5 resources` and `Database · 2 resources` are clickable.

## 6. Resource-set drill-down

```text
Source resources
API → Database

327 resources

[Search........................] [Scope ▾] [More filters]

Resource                         Scope
Orders database                  Moscow
resource-002                     Moscow
resource-003                     SPb
...

                                      1–50 of 327   < 1 2 3 >
```

The same surface is used for one resource or thousands of resources.

Resource type/classification is intentionally absent from I31 because Resource Catalogue has no accepted Resource type attribute. It must not be inferred from addresses or other realization data.

## 7. Add interaction to Deployment

```text
Add interaction

[Search........................]
[Source ▾] [Destination ▾] [Protocol ▾]

Use    Source       Destination    Traffic
☐      API          SMTP           TCP (25)
☐      Reporting    Database       TCP (5432)
☐      API          LDAP           TCP (389, 636)
☐      Web          Gateway        TCP (443)

                              [Cancel] [Add selected]
```

Only Interaction Definitions belonging to the selected Application Definition are available. Partial selection is normal.

## 8. Create Deployment

```text
New deployment

Application     [CRM            ▾]
Company         [Company A      ▾]
Environment     [Production     ▾]
Scope           [Moscow         ▾]

                              [Cancel] [Create]
```

A new Deployment may initially contain zero selected interactions and be populated incrementally.

## 9. Retirement blocked by active references

```text
Cannot retire "Database"

Active references:
Interactions    5
Deployments     12

Counts are clickable and open the corresponding dependency list.

                                              [Close]
```

No hard-delete action exists in the MVP.

## Visual-regression follow-up

After implementation, representative deterministic fixtures for these screens should be covered by browser screenshot tests. The screenshots validate rendering against the accepted layout; this document and the accepted domain/UX specs remain the semantic source of truth.
