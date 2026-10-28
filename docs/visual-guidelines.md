# Visual guidelines

> **Status: agreed (v1).** Changes are recorded in the decisions log (section 10).

## 1. Canvas and spacing

- **Page size:** 1920 × 1080 (16:9) on every page.
- **Edge margin:** every header, visual and footer sits at least **20 px** from each canvas edge.
- **Gap between visuals:** **20 px**, made of 10 px on each visual's side. This applies to visuals side by side and visuals stacked vertically.
- There is no column grid. Positions follow the spacing rules above.
- **No mobile layout.**

Equal left and right margins keep the Arabic mirror exact: `x_ar = 1920 − x_en − width`.

## 2. Page frame

These elements are fixed on every page. The body between them changes with each page.

```
EN                                                        AR (mirrored)
┌ 20 ───────────────────────────────────── 20 ┐           ┌──────────────────────────────────────────┐
│ Page title            [◀ ▶] [EN|ع] [☰]      │ 20–120    │ [☰] [EN|ع] [▶ ◀]             عنوان الصفحة │
│ Headline (DAX)                              │           │                           (DAX) العنوان  │
├─────────────────────────────────────────────┤           ├──────────────────────────────────────────┤
│                                    ┌────────┤ 140–1000  ├────────┐                                 │
│  body: key visual + supporting     │ menu   │           │ menu   │   body                          │
│                                    │ panel  │           │ panel  │                                 │
│                                    └────────┤           ├────────┘                                 │
├─────────────────────────────────────────────┤           ├──────────────────────────────────────────┤
│ Source: GEM… · Refreshed: … · Data to: …    │ 1020–1060 │    … :المصدر                              │
└─────────────────────────────────────────────┘           └──────────────────────────────────────────┘
```

### 2.1 Header (y 20–120)

- The page title (20 pt Semibold) sits on the reading-start side: left in English, right in Arabic. The dynamic headline sits below it as a subtitle (18 pt regular, secondary text) and may wrap to two lines.
- The header sits on the canvas: no white card behind the title, headline or buttons. Buttons have no fill, only a thin grey outline. Only visuals have white cards.
- The buttons sit on the reading-end side, in this order: Back / Next, language switch, menu toggle.

### 2.2 Body (y 140–1000)

- Each page's layout follows its story. **The visual carrying the key message gets the most space and emphasis,** and the supporting visuals sit around it.
- Body layouts are approved in the mock-up (section 5) before they are built.

### 2.3 Footer (y 1020–1060, every page)

The footer holds three items and no buttons:
- **Source:** Global Energy Monitor, *Global Integrated Power Tracker*; Ember, *Yearly electricity data* (both CC BY 4.0).
- **Refreshed:** the date and time the model last refreshed in Fabric, captured by a one-row Power Query table.
- **Data to:** `GEM tracker Sep 2026 · Ember 2024 (latest year per country)`.

## 3. Menu panel

- The menu opens and closes with bookmarks.
- It holds the page's **slicers** and any **KPI explanations** that need one. On Overview it also holds the **Overview focus** slicer (Under construction / Came online), which switches the headline.
- **Icons:** ☰ when closed, ✕ when open, as custom SVGs. Both are symmetric, so the Arabic pages use the same icons.
- **Opening:** it slides in over the body from the side where its button sits (right in English, left in Arabic). It does not push the body aside.
- **Stacking:** the menu panel is always the top layer of the canvas (highest z-order), so it never opens behind a visual.
- **Bookmarks:** one open/closed pair per page per language, so 4 pages × 2 languages × 2 states = 16. They do not capture data, so opening or closing the menu never resets the slicers. The mirror script generates the Arabic ones.

## 4. Navigation

- **Back / Next buttons only**, in the header. The Power BI service already shows its own page navigation.
- The arrows point the other way on Arabic pages.
- The language switch jumps to the same page in the other language.
- Drillthrough to Detail stays as in the scope document.

## 5. Mock-up

The mock-up comes **after every visual and the analysis behind it are confirmed.** It shows all four pages in English and Arabic for approval before building starts.

## 6. Colour

Light theme: Power BI has no dark mode that viewers can switch on. All categorical palettes were checked with a colour-vision-deficiency validator.

### 6.1 Technology (categorical)

| Technology | Hex |
|---|---|
| Solar | `#daa932` |
| Wind | `#189e8c` |
| Hydro | `#3a70b3` |
| Other (bioenergy, geothermal) | `#b3b2ac` |

- Bioenergy and geothermal fold into "Other" (about 0.5 GW operating). A fourth hue failed the validator.
- Solar and Other sit below 3:1 contrast on white, so any visual using them shows a legend or data labels.
- The first palette (`#eda100`, `#1baf7a`, `#2a78d6`) clashed: its lightness and saturation were uneven. These three hues have matched lightness and saturation, and solar's gold stays clear of the orange accent.

### 6.2 Status (ordinal, one hue)

| Status | Hex |
|---|---|
| Operating | `#2b2570` |
| Under construction | `#4a3fb0` |
| Pre-construction | `#7368d9` |
| Announced | `#a49cea` |
| Shelved / cancelled | grey hatch (`#9e9d97` lines on `#e6e5e1`) |

Darkest means furthest along. A traffic-light scale was rejected: "announced" is not "bad".

The Overview year chart uses the same two steps: operating (came online) and under construction (by expected year).

**Purple means project status and nothing else.** Charts split by stage use this scale on every page. Totals that aren't split by stage are neutral (`#d3d2cc`), and so are table data bars. Operating against planned capacity uses dark grey (`#5c5b57`) against neutral: Power BI can't colour bars by category when a chart has two measures, so the technology colours can't be used there.

### 6.3 Accent

- One accent for the whole report: orange `#eb6834`. Red stays free for risk.
- **Single-series visuals:** the key item is in the accent; everything else is neutral `#d3d2cc`.
- **Visuals already coloured by category:** the key item keeps full colour; everything else uses the faded tint (the colour at 40% opacity over white, precomputed as hex, since conditional formatting takes plain hex codes).
- The accent is applied by conditional-formatting rules, not hand-picked bars.

### 6.4 Neutrals

| Role | Hex |
|---|---|
| Canvas | `#f4f4f2` |
| Visual card | `#ffffff` |
| Gridlines, borders | `#e4e3df` |
| Neutral (not highlighted) | `#d3d2cc` |
| Secondary text | `#5c5b57` |
| Primary text | `#1d1d1b` |

Greys run lightest to darkest: gridlines → neutral → Other.

## 7. Typography

- **Headline and titles:** Segoe UI (Semibold where the table says so).
- **Body text:** Segoe UI regular (labels, tables, notes, footer, menu). Light was dropped after the font test: regular reads better in both scripts.
- **Fallback:** Tahoma. A font test page (English and Arabic in Segoe UI Semibold, Segoe UI, Segoe UI Light and Tahoma) was rendered in Fabric and checked on a Mac: all read fine, Segoe UI regular best.

| Element | Size (pt) | Font |
|---|---|---|
| Page title | 20 | Segoe UI Semibold |
| Page headline (subtitle) | 18 | Segoe UI, secondary text colour |
| KPI value | 44 on the page's key KPI, 30 on the others | Segoe UI Semibold |
| KPI label / status line | 13 | Segoe UI |
| Visual title (charts and KPI panels alike) | 16 | Segoe UI Semibold |
| Axis labels, data labels, legend | 12 | Segoe UI (trend axes 11) |
| Table text | 12 | Segoe UI (headers Semibold) |
| Notes (outliers, caveats) | 12 | Segoe UI, secondary text colour |
| Footer / menu text | 11 / 13 | Segoe UI |

**Arabic pages:** every size of 16 pt or below is 1 pt larger. The mirror script applies this.

## 8. Numbers and dates

| Item | Rule | Example |
|---|---|---|
| Capacity totals, KPIs, chart labels | GW, 1 decimal | 49.8 GW |
| Project table | MW, no decimals, thousands separator | 1,500 MW |
| Percentages | 1 decimal | 3.8% |
| Ratios | no decimals | 28× |
| Years | 4 digits, no separator | 2025 |
| Ember figures | year in brackets | Jordan (2024) |
| Dates | `dd mmm yy` where it fits, 24-hour time | 28 Oct 26, 14:05 |
| Month-only labels | `mmm`, or the initial if `mmm` doesn't fit | Oct / O |

- Never the American month-first format.
- **Digits:** Western (0–9) on every page. Power BI visuals can't show Arabic-Indic digits, so text measures don't use them either, to keep each page consistent.
- **Translation never changes formats.** Numbers, unit symbols (GW, MW, %, ×) and dates look exactly the same on English and Arabic pages, including English month abbreviations (`28 Oct 26`). Only words are translated.
- Axis titles carry the unit; data labels are plain numbers.

## 9. RTL rules (Arabic pages)

Arabic pages are generated from the English pages by the mirror script.

| Element | Arabic page |
|---|---|
| Positions | Mirrored: `x_ar = 1920 − x_en − width` |
| Text alignment | Right-aligned |
| Time axes (column, line) | Time runs right to left (earliest year on the right); value axis on the right. Done with a categorical year axis sorted descending, since a continuous axis can't be reversed |
| Horizontal bars | Bars grow right to left; category labels on the right; legend top-right |
| Opportunity scatter | Mirrored: X axis reversed (higher share further left), Y axis on the right; quadrant notes move with it |
| Tables | Column order reversed (plant name rightmost), alignment mirrored (text right, values left), data bars grow from the right. The native grid always starts at the left edge, so column widths fill the visual (section 10.4) |
| Headers, tooltips | Arabic column names, set per visual by the mirror script |
| Slicer values | Arabic columns from the model (country, status, technology) |
| Text size | +1 pt for sizes of 16 pt or below (section 7) |
| Not mirrored | Digits, unit symbols, dates, the ☰ / ✕ icons, Latin plant names with no Arabic name |

- **Arabic text direction:** Power BI text boxes and titles are left-to-right. Every Arabic sentence (static text from the mirror script, and the headline, KPI and footer measures) is wrapped in a right-to-left embedding (U+202B … U+202C); otherwise text that starts with a number comes out in the wrong order.
- **Tables:** the native table visual is tested first. If it can't mirror correctly (column order, alignment, data-bar direction), the fallback is a custom visual (an HTML visual or Deneb), checked for Publish to web support before adoption.
- **Service page list:** all 8 pages are visible, English 1–4 then Arabic 1–4, with Arabic page names.

## 10. Visual patterns

Agreed from a rendered sample page (KPI panels, bar chart, table). The patterns were studied from public examples; every file is our own.

### 10.1 Proportions

- **KPI row ≈ 30% of the body, main visuals ≈ 70%.** On 1920 × 1080: KPI row about 260 px, main visuals about 600 px, with the 20 px spacing rules.
- The key visual of the page gets the most space; KPIs summarise, they don't compete.

### 10.2 KPI panel

Stacked with no gaps, on one white card:

| Part | Height | Style |
|---|---|---|
| Title | ~40 px | Same as visual titles: Segoe UI Semibold 16 pt, primary text |
| Value | ~66 px | Segoe UI Semibold 36 pt, left-aligned (multi-row card, no category label, no scrolling) |
| Status line | part of the trend | A translated text measure with alternative wordings (▲ / ▼ / "Only…"), 13 pt. Accent colour only on the page's key message; otherwise secondary text |
| Trend strip | ~120 px | Dark line = the measure, light grey line = comparison (e.g. world), dot and label on the latest point only. No value axis or gridlines; small year axis |

- A comparison legend, when needed, sits on the status line row, right-aligned.
- Units go in the title (`Operating capacity (GW)`), not after the number.

### 10.3 Bar charts

- Bars are thin: the gap between bars is 50% of the category width (also on column charts).
- Labels show the value and, as a detail label, the **% of total** in the current view (e.g. `19.6 · 38%`). Percentages under 1% are hidden instead of showing `0%`.
- Highlight by rule: the key bar takes the accent through a model measure; the rest are neutral.
- No value axis or gridlines; category labels 12 pt; categories sorted by value, or by stage order where the category has one (status).

### 10.4 Tables

- Headers Segoe UI Semibold 12 pt in secondary text; values Segoe UI 12 pt; horizontal rules only.
- Text and descriptive numbers (years) are left-aligned; values are right-aligned. Each header aligns with its column.
- Value columns carry data bars in neutral (`#d3d2cc`) with the number visible.
- Column formatting only where it adds information, through dynamic format strings on table-only measures (the number underneath is unchanged, so sorting still works):
  - Wind + solar share: `▲` / `▼` against the world share in the same year.
  - Pipeline: the multiple of operating capacity (`101.4 · 11×`), shown only when both are at least 0.1 GW.
  - Status: a `●` in the status colour before each status.
- Glyph bars (▉ characters) are not used: they don't mirror on Arabic pages. Native data bars do.
- Column widths are set to fill the visual (less the scroll bar), so there is no horizontal scroll bar and the mirrored grid leaves no gap.

### 10.5 Scatter

- Both axes start at 0 and end at 1.2 × the largest value in view (a model measure), so the biggest bubbles are never clipped.
- v2: the Opportunity scatter was replaced by gap-to-world bars (10.7); the rule stays for any future scatter.

### 10.7 Chart checks (v2, from the dataviz skill)

Every chart is checked against these before review:

- **Pick the form from the question.** Gap to a baseline → bars either side of zero (Opportunity: share minus the world's). One item matters → accent on it, the rest neutral. A single number → a KPI, not a chart.
- **One value axis.** Never two y-scales on one chart. Two measures of different scale → two charts.
- **Label selectively.** Time series label the latest full year and anything forward-looking; a recessive value axis (solid hairline gridlines) carries the rest. Ranked bar charts keep a label per bar.
- **A label never collides with or is clipped by its mark.** Bar charts get axis headroom from a model measure; a label that doesn't fit inside a stacked segment is dropped to the tooltip.
- **A KPI's trend shows the same thing as its number** (operating capacity → cumulative line, not yearly additions).
- **One lead number per page:** the key KPI's value is larger than the others (section 7).
- **Say what the data can't cover** next to the chart (e.g. the share of under-construction capacity with no expected year).
- **Two or more series get a legend**; on custom legends the swatch is coloured and the label stays in text colour.

### 10.6 Checking

Every page is rendered to PNG through the Power BI export API and looked at before review. Schema checks alone don't catch formatting that Fabric silently ignores.

## 11. Decisions log

| # | Question | Decision |
|---|---|---|
| 1 | Page size | 1920 × 1080 |
| 2 | Spacing | 20 px from the canvas edges; 20 px between visuals (10 px each side), across and down |
| 3 | Footer | On every page: source, last refresh time, last data period. No buttons |
| 4 | Navigation | Back / Next in the header next to the language switch; the service handles the page list |
| 5 | Menu | Bookmark-toggled panel holding slicers and KPI explanations; ☰ / ✕ icons; overlays the body from the button's side; always the top layer |
| 6 | Body layout | Driven by each page's story: key visual emphasised, supporting visuals around it |
| 7 | Mobile layout | None |
| 8 | Mock-up timing | After all visuals and the analysis are confirmed |
| 9 | Colour | Technology, status, accent and neutrals as in section 6; light theme; reviewed on a swatch page |
| 10 | Typography | Segoe UI for headline/titles, Segoe UI Light for body, sizes as in section 7; Tahoma fallback after a font test page |
| 11 | Arabic text size | +1 pt for every size of 16 pt or below |
| 12 | Numbers | GW 1 dp; project table MW 0 dp; % 1 dp; Western digits everywhere |
| 13 | Dates | `dd mmm yy` where it fits; month labels `mmm` or initial; never month-first |
| 14 | Translation and formats | Translation changes words only; numbers, unit symbols and dates are identical in both languages |
| 15 | RTL rules | Everything mirrors, including time axes and the scatter (section 9); all 8 pages visible in the service |
| 16 | Tables | Native table first; custom visual (HTML or Deneb) only if native mirroring fails |
| 17 | Body font | Segoe UI regular replaces Light after the font test |
| 18 | Visual patterns | KPI panel, bar, table and proportion rules in section 10, agreed from a rendered sample |
| 19 | Page header | Page title above the headline subtitle (20 / 18 pt); header and buttons on the canvas, no cards or button fill |
| 20 | Bar thickness | 50% gap between bars on every bar and column chart |
| 21 | Colour roles | Purple only for status; totals not split by stage, and table data bars, in neutral; operating vs planned in dark grey vs neutral |
| 22 | Table alignment | Text and years left, values right (English), mirrored on Arabic pages; headers follow their column; widths fill the visual |
| 23 | Scatter axes | 0 to 1.2 × the largest value, so bubbles aren't clipped |
| 24 | Unit column | Dropped from the projects table: GEM's unit names are partly Arabic-only |
| 25 | Technology palette | Gold, teal, blue (candidate B): matched lightness and saturation so the hues don't clash; passes the colour-vision checks |
| 26 | Table column formatting | ▲ / ▼ vs world share, pipeline × operating, status dot; native data bars kept |
| 27 | v2 chart checks | Section 10.7, adopted from the dataviz skill review: form from the question, one value axis, selective labels, no clipped labels, trend matches the KPI, one lead number per page |
| 28 | Key KPI size | 44 pt on the page's key KPI, 30 pt on the others (was 36 pt on all) |
| 29 | Overview main chart | Came online by year (2015–2025) plus under construction by expected year (2026–2029), status colours, with a coverage note |
| 30 | Opportunity main chart | Gap-to-world bars replace the scatter |
| 31 | Breakdown supporting chart | Hydrogen-tied vs rest of the pipeline by country replaces operating vs planned by technology |
