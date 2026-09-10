# Application Catalogue canonical wireframes

Status: `accepted target; implementation pending`.

Date: 2026-09-10.

Canonical semantics:
- `docs/decisions/ADR-012-application-definition-deployment-model.md`;
- `docs/ui/application-catalogue-target.md`.

These low-fidelity wireframes are the target screen-layout contract. Implementation may refine spacing, typography and responsive behavior, but must not introduce new information architecture, actions, columns or entity grouping without updating the accepted UX/domain documentation first.

## 1. Applications / Definitions

```text
Applications
[Definitions] [Deployments]

Definitions                                      [+ Add application]

[Search............................]
[Domain ▾] [Owner ▾] [More filters]

Name          Domain        Components   Interactions   Deployments
CRM           Sales              8            24            17
SAP ERP       Finance           15            63             8
Monitoring    Infrastructure    27           118            42

                                      1–50 of 327   < 1 2 3 >
```

Row name opens Application Definition detail.

## 2. Application Definition

```text
Applications / Definitions / CRM

CRM                                             [Edit] [⋮]
Customer Relationship Management

Domain: Sales
Owner: CRM Team

[Overview] [Components 8] [Interactions 24] [Deployments 17]
```

### Components

```text
CRM / Components                               [+ Add component]

[Search................] [Type ▾]

Name           Type          Description
Web            Frontend      Web frontend
API            Service       Backend API
Database       Database      Primary database
Reporting      Service       Reporting

                                      1–50 of 8
```

Component create/edit uses a compact drawer while the field set remains small.

### Interactions

```text
CRM / Interactions                            [+ Add interaction]

[Search................]
[Source ▾] [Destination ▾] [Protocol ▾]

Source       Destination    Traffic                          Deployments
Web          API            TCP (80, 443)                        17
API          Database       TCP (5432)                           12
API          DNS            UDP (53), TCP (53)                   15
API          Gateway        TCP (12 ports), UDP (4 ports)         7

                                      1–50 of 24
```

One row is one Interaction Definition. Large traffic collections are summarized and drilled into rather than wrapped.

### Definition-local Deployments

```text
CRM / Deployments                              [+ Deploy]

[Search................]
[Company ▾] [Environment ▾] [Scope ▾]

Company       Environment   Scope        Interactions
Company A     Production    Moscow          18 / 24
Company A     Test          Moscow          24 / 24
Company B     Production    SPb             11 / 24

                                      1–50 of 17
```

## 3. Applications / Deployments

```text
Applications
[Definitions] [Deployments]

Deployments                                    [+ Add deployment]

[Search...................................]
[Application ▾] [Company ▾] [Environment ▾] [Scope ▾]

Application   Company      Environment   Scope       Interactions
CRM           Company A    Production    Moscow        18 / 24
SAP ERP       Company A    Production    Moscow        52 / 63
CRM           Company B    Production    SPb           11 / 24

                                      1–50 of 846
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
[Source ▾] [Destination ▾] [Protocol ▾] [Binding state ▾] [More filters]

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

[Search........................] [Type ▾] [Scope ▾] [More filters]

Resource          Type        Scope
resource-001      Network     Moscow
resource-002      Host        Moscow
resource-003      Host        SPb
...

                                      1–50 of 327   < 1 2 3 >
```

The same surface is used for one resource or thousands of resources.

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
