# Page proposals (v1)

> **Status: draft for review.** Built overnight as v1 on the `report-v1` branch so the pages can be judged rendered, not on paper. Nothing here is agreed until reviewed; `main` is unchanged. Numbers are the live values from the model.

Every page follows the agreed frame (visual-guidelines.md sections 2–4 and 10): dynamic headline, Back / Next, language switch and ☰ menu in the header; KPI row ≈ 30% and main visuals ≈ 70% of the body; footer with source, refresh time and data period; a bookmark menu panel holding slicers and notes.

## v2 changes (branch `report-v2`, for comparison with v1)

v1 stays live in the `bilingual-report` workspace (main); v2 is in `bilingual-dev`. Changes come from the dataviz skill review (visual-guidelines.md section 10.7) and two new analyses.

| Page | v1 | v2 | Why |
|---|---|---|---|
| Overview main | Came online each year 2010–2025, stacked by technology, a label on every year | Came online 2015–2025 plus **under construction by expected year 2026–2029**; labels only on 2025 and the expected years; value axis with hairlines; note: expected year known for 59% of the 51.6 GW under construction (21.4 GW has none) | Analysis 1: what comes online next (2–3-year persona). Selective labels; 2010–2014 was near zero |
| Overview KPI 2 | 49.8 GW over a line of yearly additions | Same value over the **cumulative** line | Trend now shows what the number shows |
| Pipeline KPI (all pages) | `247.0` label ran into its bar | More axis headroom | Labels never collide with their mark |
| Key KPI | All values 36 pt | Key KPI 44 pt, others 30 pt (Overview: share; Breakdown: pipeline; Opportunity: under construction) | One lead number per page |
| Breakdown supporting | Operating vs planned by technology | **Pipeline tied to green hydrogen by country**: tied (dark grey, labelled GW · %) vs rest (neutral) | Analysis 3: Mauritania 96%, Djibouti 98%, Oman 85%, Morocco 58% hydrogen-tied |
| Opportunity main | Scatter: share × under construction | **Gap-to-world bars**: each country's wind + solar share minus the world's (pts), Egypt (top builder) in the accent | Answers Q8 directly; the scatter's labels overlapped |

Not built from the review:
- **Dumbbell (operating vs planned by country):** on one linear scale operating (≤ 12 GW) collapses against planned (up to 113 GW); the scorecard's pipeline multiple carries this instead.
- Filter-state line in the header and value-first tooltips (review items C and D): not in this round.

Trade-off to review: the Overview no longer shows the technology split of added capacity, and Breakdown no longer compares operating vs planned by technology. Technology now shows only in the hydrogen KPI and the slicers.

## 1. Overview: "Building is accelerating, but from a very small base"

| Part | Proposal | Today's values |
|---|---|---|
| Headline | `Headline Overview` (focus slicer switches scale / speed) | 51.6 GW under construction, more than the 49.8 GW running; wind and solar 5.5% of electricity (2023–2025) |
| KPI 1 (key message, accent) | Wind and solar share vs the world, trend 2015–2023 | 3.8% · ▼ 9.6 pts below the world (13.4%) in 2023 |
| KPI 2 | Operating capacity, GW added per year 2015–2025 | 49.8 GW · ▲ 10.9 GW came online in 2025 |
| KPI 3 | Pipeline by stage, % of pipeline | 447.1 GW · only 11.5% under construction |
| Main | Capacity that came online each year 2010–2025, stacked by technology, year totals | 10.9 GW in 2025 vs 8.8 GW in 2010–2019 |
| Menu | Headline focus, technology, country; notes on the three KPIs | |

## 2. Breakdown: "The pipeline is concentrated, and most of it is still on paper"

| Part | Proposal | Today's values |
|---|---|---|
| Headline | `Headline Breakdown` | Only 11.5% of the 447.1 GW pipeline is under construction; Mauritania alone plans 112.7 GW |
| KPI 1 | Pipeline by stage | 447.1 GW |
| KPI 2 | Tied to green hydrogen, by technology | 253.2 GW · 56.6% of the pipeline |
| KPI 3 | Shelved or cancelled | 80.7 GW · 61.1 shelved, 19.6 cancelled |
| Main (key, 58%) | Capacity by country, stacked by status | Mauritania and Egypt lead; most of it pre-construction or announced |
| Main (supporting) | Operating vs planned capacity by technology | Wind 6.3 operating vs 178.7 planned |
| Menu | Technology, country; notes on totals and hydrogen | |

## 3. Opportunity: "Where is the transition gap?"

| Part | Proposal | Today's values |
|---|---|---|
| Headline | `Headline Opportunity` | Egypt is building the most (19.6 GW), while wind and solar supply 7.9% of its electricity (2025) |
| KPI 1 | Emissions intensity, region trend 2015–2023 | 631 g/kWh (2023) |
| KPI 2 | Under construction, top 3 countries with % of total | 51.6 GW · Egypt 38% |
| KPI 3 | Announced only, pipeline by stage | 148.5 GW · 33.2% of the pipeline |
| Main (key) | Scatter: wind + solar share × GW under construction, bubble = generation, top builder in accent | |
| Main (supporting) | Country scorecard: Ember year, share, intensity, operating, under construction (data bars), pipeline | |
| Menu | Technology, country; how to read the scatter | |

## 4. Projects: "A few megaprojects and a few owners"

| Part | Proposal | Today's values |
|---|---|---|
| Headline | `Headline Detail` | The 10 largest projects hold 35.4% of the pipeline; 56.6% is tied to green hydrogen |
| Top left | Ten largest pipeline projects, stacked by status, H₂ marker | Two 30 GW Megaton Moon entries in Mauritania |
| Top right | Owners of operating capacity, share-weighted | ACWA Power 5.7 GW |
| Bottom | All projects table: project, country, technology, status, MW (data bars), start year, owner, hydrogen | |
| Menu | Status, technology, country; notes on owners and Arabic names | |

No KPI row here: this page is the detail behind the other three.

## 5. Open questions for review

1. **Overview main visual.** Should 2025 be highlighted (other years faded)? The legend uses technology colours, so the guideline's "fade the rest" would need per-year colour rules.
2. **Breakdown KPI 1** repeats Overview KPI 3 (pipeline by stage). Keep it, or swap for something new (e.g. pipeline-to-operating ratio)?
3. **Opportunity scatter.** Add reference lines at the regional weighted share (agreed in scope) and quadrant labels?
4. **Drillthrough** from Breakdown and Opportunity to Projects isn't built yet.
5. ~~**Projects table**: keep the Unit column?~~ Dropped (visual-guidelines.md decision 24): GEM's English unit field holds Arabic for 6 units in 3 plants.

## 6. Known issues in v1

- **Arabic plant names are not unique.** GEM gives some separate plants the same Arabic name (e.g. AMUN wind and AMUN solar are both "آمون للهيدروجين الأخضر"), so Arabic visuals grouped by plant merge them: the Arabic top-10 differs from the English one. Needs a decision: make `Plant AR` unique (e.g. add the technology) or group by plant ID and show the name as a label.
- Projects page: the top-10 bars show no value or H₂ labels (seen in English too in the v2 render; this page is unchanged from v1).
- Slicer UI words ("Select all", "All") stay in English on Arabic pages; they come from Power BI, not the report.
- Scatter labels overlap for the small countries near the origin (v1 only; v2 replaces the scatter).
- The language button keeps the current page; filters chosen on one language page don't carry over.

## 7. How v1 is built and checked

- `scripts/build_report.py` writes the four English pages; every static string carries its translation key.
- `scripts/mirror_pages.py` writes the Arabic twins: mirrored positions, right alignment, Arabic text and columns, reversed axes and table columns, data bars from the right, +1 pt text, Arabic language filter, navigation and menu bookmarks remapped.
- Arabic text: Power BI text boxes are left-to-right, so every Arabic sentence (static text and the headline, KPI and footer measures) is wrapped in a right-to-left embedding (U+202B … U+202C). Without it, sentences that start with a number come out in the wrong order.
- Each run is validated against Microsoft's schemas, imported into `bilingual-dev` with the Fabric CLI, refreshed, and every page (and the open menu) is exported to PNG and checked.
