# Web UI design tokens

## Color

### Navigation

| Token | Value | Usage |
|---|---|---|
| `nav.bg` | `#0B1628` | primary sidebar |
| `nav.bg.secondary` | `#111F35` | secondary navigation surfaces |
| `nav.selected` | `#172E50` | selected navigation item |
| `nav.text` | `#D9E4F2` | primary sidebar text |
| `nav.text.muted` | `#8FA6C2` | group labels / secondary text |

### Surface

| Token | Value | Usage |
|---|---|---|
| `surface.page` | `#F5F7FA` | page background |
| `surface.card` | `#FFFFFF` | tables/forms/cards |
| `surface.subtle` | `#F8FAFC` | secondary sections |
| `border.default` | `#E2E8F0` | borders/dividers |

### Text/action

| Token | Value | Usage |
|---|---|---|
| `text.primary` | `#172033` | primary readable text |
| `text.secondary` | `#5F6B7D` | secondary readable text; AA on page/card surfaces |
| `text.muted` | `#667085` | lower-emphasis informative text; still readable |
| `text.disabled/decorative` | `#94A3B8` | disabled/decorative non-essential presentation only |
| `primary` | `#2563EB` | primary action |
| `primary.hover` | `#1D4ED8` | primary action hover |
| `primary.active` | `#1E40AF` | primary action active |
| `focus.ring` | `#93C5FD` | focus indication |

Do not use `text.disabled/decorative` for required explanatory text, metadata or status meaning.

Broad CSS color transitions are discouraged for text/background pairs whose interpolated colors can momentarily fail contrast. Prefer immediate state changes or transitions limited to non-contrast-affecting properties.

### Semantic status

| Token | Value | Usage |
|---|---|---|
| `success` | `#16A34A` | Allowed / Active / healthy |
| `warning` | `#D97706` | warning / expiring where supported |
| `danger` | `#DC2626` | NotAllowed / destructive / expired |
| `info` | `#0284C7` | neutral information |

Status must always include text and, where useful, an icon; color alone is insufficient.

## Typography

System/Inter-compatible sans-serif.

| Role | Size | Weight |
|---|---:|---:|
| Page title | 28px | 700 |
| Section title | 18px | 600 |
| Card title | 16px | 600 |
| Body/table | 14px | 400 |
| Metadata | 12px | 400/500 |

Default line-height: `1.4-1.5`.

## Spacing

4px base grid: `4, 8, 12, 16, 24, 32, 48`.

Typical:
- page horizontal padding: 24px desktop;
- card/section padding: 16-24px;
- control gap: 8px;
- section gap: 24px;
- table-row vertical padding: 8-12px.

## Radius/elevation

- control radius: 6px;
- card radius: 8px;
- dialog/drawer radius: 10px where applicable;
- prefer borders over heavy shadows.

## Density

Primary mode is information-dense enterprise/operations UI.

Rules:
- avoid oversized cards/hero whitespace;
- keep table/body text near 14px unless a specific readability need requires otherwise;
- keep controls compact but keyboard/accessibility usable;
- use available desktop width for comparison-heavy data;
- density must not reduce WCAG contrast, focus visibility or semantic clarity.
