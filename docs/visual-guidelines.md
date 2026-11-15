# Visual guidelines

> **Status: agreed (v4).** v4 follows fabric-kit's report design rules and theme. Changes are recorded in the decisions log (section 11).

## 1. Canvas and spacing

v4 follows fabric-kit, my starter kit for Microsoft Fabric projects: its report design rules, its Fern & Stone Tidepool Light theme and its Report layout A (decisions 40–51).

- **Page size:** 1280 × 720 (16:9) on every page.
- **Spacing:** 8 px between panels, and 8 px between the body and the top bar, the rail, the footer and the right edge.
- There is no column grid. Positions follow the frame and spacing rules.
- **No mobile layout.**

The frame is symmetric, so the Arabic mirror is exact: `x_ar = 1280 − x_en − width`.

## 2. Page frame

These elements are fixed on every page (fabric-kit Report layout A). The body between them changes with each page.

```
EN                                                        AR (mirrored)
┌────────────────────────────────────────────┐            ┌────────────────────────────────────────────┐
│ Title  Filtered: …            [‹][›][عربي] │ 0–40       │ [English][›][‹]            … :Filtered Title │
├──┬─────────────────────────────────────────┤            ├─────────────────────────────────────────┬──┤
│☰ │ Headline (DAX)                          │ 48–82      │                          (DAX) Headline │ ☰│
│  │ ┌ KPI strip ──────────────────────────┐ │ 86–178     │ ┌──────────────────────────────────────┐ │  │
│  │ └─────────────────────────────────────┘ │            │ └──────────────────────────────────────┘ │  │
│  │ ┌ panel ──────────┐ ┌ panel ──────────┐ │ 186–688    │ ┌─────────────────┐ ┌─────────────────┐ │  │
│  │ │ key visual      │ │ supporting      │ │            │ │                 │ │                 │ │  │
│  │ └─────────────────┘ └─────────────────┘ │            │ └─────────────────┘ └─────────────────┘ │  │
├──┴─────────────────────────────────────────┤            ├─────────────────────────────────────────┴──┤
│ Source: GEM… · Refreshed: … · Data to: …   │ 696–720    │      … :المصدر                              │
└────────────────────────────────────────────┘            └────────────────────────────────────────────┘
```

### 2.1 Top bar and rail

- **Top bar** (40 px, page colour, 1 px border below): on the reading-start side a fern-green ■, the report name (12 pt Semibold) and the page name (12 pt, secondary text), as in the kit's app title; the filter line after it, and Back / Next and the language switch on the reading-end side. Buttons are 28 px, no fill, with a thin border.
- **Rail** (40 px, page colour, 1 px border on its body side) runs down the reading-start edge, below the top bar. It holds only the ☰ button that opens the filter pane.

### 2.2 Body

- The **headline** (the page's DAX finding, 12 pt, secondary text) is the first line of the body, on the canvas.
- Below it, the **KPI strip** (one panel, 92 px), then the main visuals in panels.
- Each page's layout follows its story. **The visual carrying the key message gets the most space and emphasis,** and the supporting visuals sit around it.
- **Panels:** a lighter tint of the page colour (`#fcfdfc`) with a 1 px border (`#d6ded8`), 6 px corners and 8 px padding. Visuals that belong together (the Overview chart, its legend and coverage note; the KPI strip) share one panel.

### 2.3 Footer (y 696–720, every page)

A bar in the page colour with a 1 px border above. It holds three items and no buttons:
- **Source:** Global Energy Monitor, *Global Integrated Power Tracker*; Ember, *Yearly electricity data* (both CC BY 4.0).
- **Refreshed:** the date and time the model last refreshed in Fabric, captured by a one-row Power Query table.
- **Data to:** `GEM Sep 2026, Ember 2023–2025` (the latest Ember year per country).

## 3. Filter pane

- The ☰ button on the rail opens the pane; ✕ closes it. Both use bookmarks.
- The pane is 232 px wide, in the page colour, with a border and a soft shadow, and covers the rail and the body's reading-start edge. **It is closed by default.**
- **It overlays the body instead of reflowing it:** Power BI bookmarks can show and hide visuals but cannot move or resize them, so a reflow would need two copies of every visual.
- It holds the page's **dropdown slicers** and the **notes** behind the numbers. On Overview it also holds the **Overview focus** slicer (Under construction / Came online), which switches the headline.
- **Power BI's own filter pane is hidden** on every page (report setting `outspacePane.visible = false`), so readers see only this pane.
- **Stacking:** the pane is always the top layer of the canvas (highest z-order).
- **Bookmarks:** one open/closed pair per page per language, so 4 pages × 2 languages × 2 states = 16. They do not capture data, so opening or closing the pane never resets the slicers. The mirror script generates the Arabic ones.

## 4. Navigation

- **Back / Next buttons only**, in the top bar. The Power BI service already shows its own page navigation.
- The arrows point the other way on Arabic pages.
- The language switch jumps to the same page in the other language.
- Drillthrough to Detail stays as in the scope document.

## 5. Mock-up

The mock-up comes **after every visual and the analysis behind it are confirmed.** It shows all four pages in English and Arabic for approval before building starts. v4's mock-up was a real render in the development workspace.

## 6. Colour

The report uses the **Fern & Stone Tidepool Light** theme from fabric-kit, registered as the report's custom theme (`theme/fernstone-tidepool-light.json`, copied from the kit). No colours outside the theme are used. Power BI has no dark mode that viewers can switch on, so the report is light only.

### 6.1 Series colours (technology and status)

The kit's four colour-blind-safe series colours plus its "Other" grey-green:

| Series | Hex | Technology | Status |
|---|---|---|---|
| 1 | `#28a19c` teal | Wind | Operating |
| 2 | `#b6801f` ochre | Solar | Under construction |
| 3 | `#5a71cd` blue | Hydro | Pre-construction |
| 4 | `#b25e6a` rose | | Announced |
| 5 | `#7a877f` grey-green | Other (bioenergy, geothermal) | Shelved / cancelled |

- **Status and technology share hues,** so colour never identifies them alone: every chart split by status or technology shows a legend or direct labels, and the table pairs the status dot with the status name.
- Status follows the stages in order. Faded twins (the colour at 40% over white) are kept for "the rest" when one item is picked out.
- Series 5 fails the colour-vision checks against series 4 (theme note in fabric-kit), so it is only used for "Other" and shelved / cancelled, always labelled.

### 6.2 Highlight

- One highlight per visual: the key item in **fern green `#1d6a44`**, everything else in the kit's context grey `#87938c` (clearly lighter than fern green), with a data label on the highlight. The chart's finding title names the highlighted item (section 10.9).
- The highlight is applied by model measures (`Accent Colour`, `Neutral Colour`, `Top Builder Colour`), not hand-picked bars.
- Good versus bad, where a measure has one, is blue versus burnt orange (`#3a64ad` / `#9c5520`) with an icon and a word, never green versus red.

### 6.3 Neutrals

| Role | Hex |
|---|---|
| Canvas | `#f8faf8` |
| Panel | `#fcfdfc` |
| Top bar, rail, footer, filter pane | `#f8faf8` (the page colour: only visual panels are lighter than the page) |
| Panel and bar borders | `#d6ded8` |
| Gridlines | `#e4eae5` |
| Axis line | `#c2ccc5` (the kit's chart axis) |
| Context (bars that are not highlighted) | `#87938c` |
| Neutral (table data bars, the hydrogen chart's rest of the pipeline) | `#c2ccc5` |
| Secondary text | `#46534b` |
| Primary text | `#111a15` |

Totals not split by stage and table data bars are neutral. The hydrogen chart's tied part is dark grey (`#46534b`) against neutral.

## 7. Typography

- **Font:** Segoe UI, regular and Semibold (the kit's theme fonts). Tahoma is the fallback.
- Sizes follow the kit's theme for a 1280 × 720 page; 9 pt is the minimum.

| Element | Size (pt) | Font |
|---|---|---|
| Report name / page name (top bar) | 12 | Segoe UI Semibold / Segoe UI, secondary text colour |
| Headline | 12 | Segoe UI, secondary text colour |
| Filter line | 10 | Segoe UI, secondary text colour |
| Visual title (the finding) | 12 | Segoe UI Semibold |
| Visual subtitle | 10 | Segoe UI, secondary text colour |
| KPI label | 10 | Segoe UI, secondary text colour |
| KPI value | 22 on the page's key KPI, 18 on the others | Segoe UI Semibold |
| KPI status line | 9 (primary text on the key KPI, secondary on the others) | Segoe UI |
| Axis labels, data labels, legend | 9 | Segoe UI |
| Table values / headers | 10 / 9 | Segoe UI / Segoe UI Semibold |
| Slicer header / items | 10 | Segoe UI Semibold / Segoe UI |
| Notes, footer | 9 | Segoe UI, secondary text colour |

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
| Positions | Mirrored: `x_ar = 1280 − x_en − width`: the rail and filter pane move to the right edge |
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

- **KPI strip about 18% of the body, main visuals about 80%** (v4: 92 px and about 500 px of the 640 px body). The Projects page has no KPI strip.
- The key visual of the page gets the most space; KPIs summarise, they don't compete.

### 10.2 KPI strip

One panel across the body, one cell per KPI, with a 1 px divider between cells (fabric-kit's KPI strip):

| Part | Height | Style |
|---|---|---|
| Label | ~26 px | Segoe UI 10 pt, secondary text |
| Value | ~34 px | Segoe UI Semibold, 22 pt on the page's key KPI and 18 pt on the others, left-aligned |
| Status line | ~28 px | A translated text measure with alternative wordings (▲ / ▼ / "Only…"), 9 pt; primary text on the key KPI, secondary on the others |

- Each status line keeps the visual filters it had under the v3 trend or bar chart (years 2015–2023 for shares, pipeline or delivery-risk statuses), so its numbers are unchanged.
- No trend lines or small charts inside KPIs (v4): the 720 px page has no room for them.
- Units go in the label (`Operating capacity (GW)`), not after the number.

### 10.3 Bar charts

- Bars are thin: the gap between bars is 50% of the category width (also on column charts).
- **Every bar chart is labelled.** Where each bar has one value, the label sits at its end; the hydrogen chart adds the % of the country's pipeline as a detail label (`107.6 · 96%`).
- **Stacked bars:** segment labels don't fit, so the chart shows a value axis with labels (9 pt, secondary text) instead. The hydrogen chart keeps its labels inside the tied segment and also gets the axis.
- **Axis line:** every bar and column chart has a 1 px axis line in `#c2ccc5` (the kit's chart-axis colour), lighter than the axis text. Power BI charts have no axis-line setting, so it is a constant line at 0 on the value axis: the baseline the bars grow from, and the zero line of the gap bars.
- Highlight by rule: the key bar takes fern green through a model measure; the rest take the context grey.
- No gridlines on bar charts; category labels 9 pt; categories sorted by value, or by stage order where the category has one (status).

### 10.4 Tables

- Headers Segoe UI Semibold 9 pt in secondary text; values Segoe UI 10 pt; horizontal rules only.
- Text and descriptive numbers (years) are left-aligned; values are right-aligned. Each header aligns with its column.
- Value columns carry data bars in neutral (`#c2ccc5`) with the number visible.
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
- **Label selectively.** Time series label the latest full year and anything forward-looking; a recessive value axis (solid hairline gridlines) carries the rest. Ranked bar charts keep a label per bar; stacked bars get a labelled value axis (10.3).
- **A label never collides with or is clipped by its mark.** Bar charts get axis headroom from a model measure; a label that doesn't fit inside a stacked segment is dropped to the tooltip.
- **One lead number per page:** the key KPI's value is larger than the others (section 7).
- **Say what the data can't cover** next to the chart (e.g. the share of under-construction capacity with no expected year).
- **Two or more series get a legend**; on custom legends the swatch is coloured and the label stays in text colour.

### 10.8 Filter line and tooltips (v2)

- **Filter line:** in the top bar, after the title, a text measure names the active slicer filters (`Filtered: Egypt, Oman · Solar`; more than three countries become a count). Blank when nothing is filtered.
- **Tooltip pages, value first:** the number leads (24 pt Semibold), then what was hovered (12 pt, secondary text), then detail.
  - Technology tooltip (Overview year chart, Breakdown country chart): GW, then year (came online / expected) or country · status, then GW by technology in technology colours. This replaces the technology split the v2 charts dropped.
  - Gap tooltip (Opportunity gap bars): the country's share, then country and Ember year, then the world share and the gap.
- Other charts keep the default tooltip.

### 10.9 Finding titles (v5)

Following the kit, a chart's title states what it shows, and the descriptive title moves to a muted subtitle (10 pt) below it.

- Each finding is a DAX measure (display folder *Findings*) that fills a translated template, so it updates with the slicers and follows the page language.
- **A finding must stay true under every filter:** with one item left it states that item's value; with a tie it says so (*"2 projects share the top spot"*) or falls back to the descriptive title; with nothing in view it shows the descriptive title.
- A highlighted bar is named in the title (the gap chart names the top builder whenever its bar is shown).
- Tables keep a plain title and get a subtitle.

| Chart | Finding (live values, 15 Nov 2026) |
|---|---|
| Overview: capacity coming online | 2027 is expected to bring 18.5 GW, more than any year so far (10.9 GW in 2025) |
| Breakdown: capacity by country and status | Mauritania has the most capacity: 112.9 GW, 22.7% of the total |
| Breakdown: pipeline tied to green hydrogen | Mauritania has the most tied to green hydrogen: 107.6 GW, 96% of its pipeline |
| Opportunity: share against the world | 16 of 22 countries trail the world's wind and solar share, including Egypt, which is building the most |
| Projects: ten largest projects | 2 projects share the top spot: 30.0 GW each |
| Projects: owners of operating capacity | ACWA Power Co owns the most operating capacity: 5.7 GW |

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
| 32 | Operating colour | Recessive purple-grey `#c9c6d6`; the pipeline stages carry the focus |
| 33 | Edge margins | Measured on the rendered text: title text starts at y 20, footer text ends at y 1060, footer text 20 px from the sides |
| 34 | Filter line | Active filters named on the title row (section 10.8) |
| 35 | Tooltips | Value-first tooltip pages; technology split moves into the tooltip (section 10.8) |
| 36 | Overview year highlight | None: the selective labels already pick out 2025 |
| 37 | Breakdown KPI 1 | Pipeline share of the top 3 countries, neutral bars for those countries; no repeat of the Overview pipeline panel |
| 38 | Drillthrough | Country level, to Projects; the Arabic Projects page binds `Country AR`, so each language drills to its own page |
| 39 | Unique Arabic plant names | Technology added where plants sharing a name differ by technology, else a site name; flagged `machine` |
| 40 | Kit alignment (v4) | Follow fabric-kit's report design rules and register its Fern & Stone Tidepool Light theme; no colours outside the theme. Supersedes 9, 21, 25 and 32 where they conflict |
| 41 | Page size and type | 1280 × 720 with the kit's type sizes (section 7); supersedes 1, 10 (sizes) and 28 |
| 42 | Frame | fabric-kit Report layout A: 40 px top bar (title, filter line, Back / Next, language), 40 px rail with ☰, footer bar; headline as the first body line. Supersedes 3, 4 (button placement), 19 and 33 |
| 43 | Spacing | 8 px between panels and around the body; supersedes 2 |
| 44 | Filter pane | 232 px pane of dropdown slicers and notes, opened from the rail, closed by default, overlaying the body (bookmarks can't move visuals, so no reflow). Supersedes 5 |
| 45 | Panels | Tint `#fcfdfc` with a 1 px `#d6ded8` border and 6 px corners on a `#f8faf8` canvas; replaces the white cards |
| 46 | Status and technology colours | The kit's series colours in stage order (section 6.1); the two share hues, so their charts always carry a legend or labels |
| 47 | Highlight | Fern green `#1d6a44` on light grey `#c2ccc5` (the kit's `#5b6960` is almost as dark as fern green); replaces the orange accent |
| 48 | KPIs | One KPI strip (label, value, status line); trend lines and small charts in KPIs dropped; key value 22 pt, others 18 pt. Supersedes the KPI panel in 18 and 28 |
| 49 | Alt text | On every chart, table, slicer, KPI value and button, from translation keys; Arabic machine-drafted |
| 50 | Axis line | 1 px `#7a877f` (lighter than the axis text) on every bar and column chart, drawn as a constant line at 0 on the value axis |
| 51 | Bar labels | Every bar chart is labelled; stacked bars, where segment labels don't fit, get a labelled value axis instead |
| 52 | Power BI filter pane | Hidden on every page (report-level setting); the report's own filter pane replaces it |
| 53 | Report title (v5) | Top bar shows a fern-green ■, the report name and the page name, like the kit's app title; 12 pt |
| 54 | Finding titles | Every chart's title is a DAX finding that stays true under every filter; the descriptive title becomes a 10 pt subtitle; tables keep plain titles with subtitles (section 10.9) |
| 55 | Kit chart greys | Bars that are not highlighted take the kit's context grey `#87938c`; the axis line takes the kit's `#c2ccc5`. Supersedes the colours in 47 and 50 |
| 56 | Frame colour | Top bar, rail, footer and filter pane in the page colour, with hairlines; only visual panels are lighter than the page |
| 57 | Highlight in the title | A highlighted bar is named in its chart's finding (Opportunity: the top builder, Egypt) |
