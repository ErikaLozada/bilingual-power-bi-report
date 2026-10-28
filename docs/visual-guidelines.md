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
│ Headline (DAX)        [◀ ▶] [EN|ع] [☰]      │ 20–100    │ [☰] [EN|ع] [▶ ◀]          (DAX) العنوان  │
├─────────────────────────────────────────────┤           ├──────────────────────────────────────────┤
│                                    ┌────────┤ 120–1000  ├────────┐                                 │
│  body: key visual + supporting     │ menu   │           │ menu   │   body                          │
│                                    │ panel  │           │ panel  │                                 │
│                                    └────────┤           ├────────┘                                 │
├─────────────────────────────────────────────┤           ├──────────────────────────────────────────┤
│ Source: GEM… · Refreshed: … · Data to: …    │ 1020–1060 │    … :المصدر                              │
└─────────────────────────────────────────────┘           └──────────────────────────────────────────┘
```

### 2.1 Header (y 20–100)

- The dynamic headline sits on the reading-start side: left in English, right in Arabic.
- The buttons sit on the reading-end side, in this order: Back / Next, language switch, menu toggle.

### 2.2 Body (y 120–1000)

- Each page's layout follows its story. **The visual carrying the key message gets the most space and emphasis,** and the supporting visuals sit around it.
- Body layouts are approved in the mock-up (section 5) before they are built.

### 2.3 Footer (y 1020–1060, every page)

The footer holds three items and no buttons:
- **Source:** Global Energy Monitor, *Global Integrated Power Tracker*; Ember, *Yearly electricity data* (both CC BY 4.0).
- **Refreshed:** the date and time the model last refreshed in Fabric, captured by a one-row Power Query table.
- **Data to:** `GEM tracker Sep 2026 · Ember 2024 (latest year per country)`.

## 3. Menu panel

- The menu opens and closes with bookmarks.
- It holds the page's **slicers** and any **KPI explanations** that need one.
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
| Solar | `#eda100` |
| Wind | `#1baf7a` |
| Hydro | `#2a78d6` |
| Other (bioenergy, geothermal) | `#b3b2ac` |

- Bioenergy and geothermal fold into "Other" (about 0.5 GW operating). A fourth hue failed the validator.
- Solar, wind and Other sit below 3:1 contrast on white, so any visual using them shows a legend or data labels.

### 6.2 Status (ordinal, one hue)

| Status | Hex |
|---|---|
| Operating | `#2b2570` |
| Under construction | `#4a3fb0` |
| Pre-construction | `#7368d9` |
| Announced | `#a49cea` |
| Shelved / cancelled | grey hatch (`#9e9d97` lines on `#e6e5e1`) |

Darkest means furthest along. A traffic-light scale was rejected: "announced" is not "bad".

### 6.3 Accent

- One accent for the whole report: orange `#eb6834`. Red stays free for risk.
- **Single-series visuals:** the key item is in the accent; everything else is neutral `#d3d2cc`.
- **Visuals already coloured by category:** the key item keeps full colour; everything else drops to 40% opacity.
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
- **Body text:** Segoe UI Light (labels, tables, notes, footer, menu).
- **Fallback:** Tahoma. The first Fabric deployment is a font test page (English and Arabic, Segoe UI, Segoe UI Light and Tahoma), checked on a Mac and, if possible, on Windows. The Power BI service can't load web fonts, and Segoe UI isn't installed on macOS.

| Element | Size (pt) | Font |
|---|---|---|
| Page headline | 24 | Segoe UI Semibold |
| KPI value | 36 | Segoe UI Semibold |
| KPI label | 13 | Segoe UI Light |
| Visual title | 16 | Segoe UI Semibold |
| Axis labels, data labels, legend | 12 | Segoe UI Light |
| Table text | 12 | Segoe UI Light |
| Notes (outliers, caveats) | 12 | Segoe UI Light, secondary text colour |
| Footer / menu text | 11 / 13 | Segoe UI Light |

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
| Tables | Column order reversed (plant name rightmost), text right-aligned, data bars grow from the right |
| Headers, tooltips | Arabic column names, set per visual by the mirror script |
| Slicer values | Arabic columns from the model (country, status, technology) |
| Text size | +1 pt for sizes of 16 pt or below (section 7) |
| Not mirrored | Digits, unit symbols, dates, the ☰ / ✕ icons, Latin plant names with no Arabic name |

- **Tables:** the native table visual is tested first. If it can't mirror correctly (column order, alignment, data-bar direction), the fallback is a custom visual (an HTML visual or Deneb), checked for Publish to web support before adoption.
- **Service page list:** all 8 pages are visible, English 1–4 then Arabic 1–4, with Arabic page names.

## 10. Decisions log

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
