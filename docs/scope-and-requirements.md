# Scope and requirements

> **Status: agreed scope (v1).** Changes are recorded in the decisions log (section 9).

## 1. Purpose

A bilingual (English / Arabic) Power BI report on renewable power in the 22 Arab League countries. Each page exists in English and in a mirrored right-to-left Arabic version.

The report is a portfolio piece. It is written as if a real team would use it, so every page must answer a business question, not just show the data.

## 2. Intended user (persona)

**A market-screening team at a renewable-energy developer or investor** deciding where to spend business-development effort in the region over the next 2–3 years.

The same questions apply to a development bank or an energy ministry analyst. We write for one persona to keep the report focused.

## 3. Decisions the report supports

| # | Decision | What the user needs to know |
|---|---|---|
| D1 | **Which countries to prioritise** | How big each market is today, how fast it is growing, and how much room is left |
| D2 | **Which technology to lead with in each country** | The solar / wind / hydro mix, operating and planned |
| D3 | **How far to trust the announced pipeline** | How much planned capacity is actually being built vs only announced, shelved or cancelled |
| D4 | **Who is already active** | The largest projects and their owners: potential competitors or partners |

## 4. Key questions

**Q1 – Size.** How much renewable capacity is operating in the region, and how much is in the pipeline?

**Q2 – Growth.** How fast has capacity been added year by year, and how has the renewable share of electricity changed?

**Q3 – Where.** Which countries hold the most operating capacity, and which hold the largest pipeline?

**Q4 – Momentum.** Where is new capacity actually being built (under construction), as opposed to only announced?

**Q5 – Mix.** What is the technology mix by country?

**Q6 – Delivery risk.** What share of the pipeline is under construction, versus pre-construction or announced only? How much has been shelved or cancelled?

**Q7 – Projects and owners.** Which projects drive the pipeline, and who owns them?

**Q8 – Opportunity gap.** Which countries still get little of their electricity from renewables, and is a meaningful pipeline coming?

First look at the data:
- About **50 GW** of renewable capacity is operating.
- About **447 GW** is under construction, in pre-construction or announced.
- So the pipeline is roughly 9× the operating fleet. That makes D3 (pipeline credibility) a central story, not a side note.

## 5. Pages

Each page has an English version and a mirrored Arabic version.

### 5.0 Storytelling rules (all pages)

1. **Headline, not title.** Every page opens with a one-sentence finding written as a DAX text measure. It recalculates when filters change.
   - Example: "Wind and solar still make only 3.8% of the region's electricity."
   - Headline templates live in the translations table with `{placeholders}`, so the Arabic headline is built the same way as the English one.
2. **One accent colour per page.** The thing that matters (the outlier, the leader, the risk) is drawn in the accent colour; everything else is neutral grey. Accent colour comes from conditional-formatting rules, not hand-picked bars.
3. **Outliers are called out, not hidden.** A short note under the visual explains them (e.g. "Mauritania: 113 GW announced, mainly for green-hydrogen export").
4. **Every page leads somewhere.**
   - Back / Next buttons sit in the header next to the language switch (arrows mirrored on Arabic pages). See `visual-guidelines.md`.
   - Bars and dots support drillthrough to the detail page, pre-filtered.
5. **Caveats sit next to the number they qualify**, not in a footnote page. Examples: Ember year labels, "utility-scale only".

> The page sketches below show content only. Layout, the header buttons, the footer and the menu panel (which holds the slicers) follow `visual-guidelines.md`.

### 5.1 Story arc

| Page | The story it tells | Hands over to |
|---|---|---|
| 1 Overview | Building is speeding up, but wind and solar are still a small share of the region's power | "Where is all the planned capacity?" → page 2 |
| 2 Breakdown | The pipeline is huge but concentrated, and most of it isn't being built yet | "Where are the real opportunities?" → page 3; drillthrough to page 4 for projects |
| 3 Opportunity | Markets sorted into "transition under way" vs "untapped" | "Which projects are behind this?" → page 4 (drillthrough by country) |
| 4 Detail | A handful of hydrogen-linked megaprojects dominate. Only a few owners run what's operating | Back to the page the user came from |

**Page order (decided):** Overview → Breakdown → Opportunity → Detail. Detail is last because every other page drills into it.

### 5.2 Page 1 – Overview: "Building is accelerating, but from a very small base"

```
┌───────────────────────────────────────────────────────────────┐
│ HEADLINE (dynamic)                              [عربي] switch │
├──────────┬──────────┬──────────┬──────────┬───────────────────┤
│Operating │Under     │Pre-constr│Wind+solar│ Emissions         │
│ 49.8 GW  │constr.   │+ announc.│ share    │ intensity         │
│          │ 51.6 GW  │ 396 GW   │ 3.8%     │ gCO2/kWh          │
├──────────┴──────────┴──────────┴──────────┴───────────────────┤
│ Column: operating GW added per year      │ Line: wind+solar   │
│ by start year, 2010–2025, stacked by     │ share of generation│
│ technology. 2025 bar in accent colour    │ 2015–2023 (region) │
├──────────────────────────────────────────┴────────────────────┤
│ Note: utility-scale plants only · Ember region total to 2023  │
│                           [Where is the planned capacity? →]  │
└───────────────────────────────────────────────────────────────┘
```

| Visual | What it highlights |
|---|---|
| KPI cards | The scale gap: about 50 GW operating vs about 450 GW planned. Under-construction capacity alone already exceeds the operating fleet (51.6 vs 49.8 GW) |
| Capacity added by year (column, by technology) | Acceleration: **10.9 GW came online in 2025 alone, more than 2010–2019 combined (about 9 GW)**. Accent on the latest year |
| Wind + solar share trend (line) | Context: the share rose from 0.5% (2015) to 3.8% (2023). Gas and other fossil fuels still supply about 90% of the region's electricity |
| Next button | → Page 2 |

Data check: 97% of operating capacity has a start year (48.2 of 49.8 GW), so the trend is reliable.

### 5.3 Page 2 – Breakdown: "The pipeline is concentrated, and most of it is still on paper"

Built only on the fully complete fields: country, type, status and capacity (all 100% filled).

```
┌───────────────────────────────────────────────────────────────┐
│ HEADLINE (dynamic)                              [عربي] switch │
├───────────────────────────────┬───────────────────────────────┤
│ Bar: GW by country, stacked   │ Bar: GW by technology,        │
│ by status (operating → constr │ operating vs pipeline         │
│ → pre-constr → announced),    │ (solar, wind, hydro, bio)     │
│ sorted by total. Outliers     │ Wind highlighted              │
│ (e.g. Mauritania) accented    │                               │
├───────────────────────────────┼───────────────────────────────┤
│ Delivery-risk funnel: GW by   │ Slicers: technology, status   │
│ status incl. shelved/cancelled│ Outlier note text             │
├───────────────────────────────┴───────────────────────────────┤
│ Right-click a country → Drill through to projects   [Next →]  │
└───────────────────────────────────────────────────────────────┘
```

| Visual | What it highlights |
|---|---|
| GW by country, stacked by status | **Mauritania: 113 GW planned against 0.23 GW operating and 2.1 TWh of annual generation.** The biggest pipeline sits in one of the smallest power systems. Egypt leads on actual construction (19.6 GW) |
| GW by technology | **Wind's pipeline (about 179 GW) is 28× its operating fleet (6.3 GW);** solar's is about 8×. The planned shift is towards wind. Hydro barely grows |
| Delivery-risk funnel | **Only 12% of the pipeline (52 GW) is under construction.** 61 GW is shelved and 20 GW cancelled: this shows how far announcements can be trusted |
| Drillthrough | Country or technology → page 4 (Detail), pre-filtered |

### 5.4 Page 3 – Opportunity: "Where is the transition gap?"

```
┌─────────────────────────────────┬──────────────────────────┐
│                                 │  Trend: wind + solar     │
│   SCATTER (about 60% width)     │  share over time         │
│   X = wind + solar share        │  (selected country,      │
│   Y = GW under construction     │   default = region)      │
│   size = total generation       ├──────────────────────────┤
│   + reference lines → quadrants │  KPI cards for selection:│
│                                 │  emissions intensity,    │
│                                 │  operating GW, announced │
├─────────────────────────────────┴──────────────────────────┤
│  Country scorecard table: country (year) · W+S share ·     │
│  operating GW · under construction GW · announced GW ·     │
│  emissions intensity  (data bars, sorted by construction)  │
└────────────────────────────────────────────────────────────┘
```

| Visual | Question it answers |
|---|---|
| Scatter | Where each country sits: today's mix vs what is being built |
| Trend line | Is the country moving or stuck? A dot is only a snapshot |
| KPI cards | Why it matters (emissions intensity), and what might come next (announced GW, kept off the Y axis) |
| Scorecard table | Exact values with the Ember year label; the readable view in screenshots and RTL |
| Reference lines | Quadrants, so "low" and "high" aren't judged by eye |

Interaction:
- Selecting a dot or a table row filters the trend and the cards.
- Right-click → drill through to page 4 (Detail) for that country's projects.

**Metric choice (decided):**

- **Y axis = GW under construction.**
  - *Rejected: pipeline ÷ operating.* The ratio explodes on small bases (Bahrain 621×, Kuwait 218×).
  - *Rejected: total pipeline GW.* It is dominated by announced green-hydrogen megaprojects (Mauritania 113 GW against 2.1 TWh of generation).
- **X axis = wind + solar share, not all renewables.** The all-renewables share counts legacy hydro (Sudan reads 79.7%, mostly dams), which would wrongly suggest a mature solar / wind market.
- **Bubble size = total generation**, so market size stays visible.

**Decided:**
- Trend default when nothing is selected: the region, computed as summed TWh, shown to 2023 (the last year with all 22 countries).
- Reference lines: the regional weighted share, rather than Power BI's unweighted average of the dots.

How to read the scatter:
- **Low share, high construction:** the transition is under way.
- **Low share, low construction:** an untapped or stalled market.
- **High share:** already advanced.

### 5.5 Page 4 – Detail: "A few megaprojects and a few owners"

```
┌───────────────────────────────────────────────────────────────┐
│ HEADLINE (dynamic)                              [عربي] switch │
├───────────────────────────────────────────────┬───────────────┤
│ Bar: top 10 pipeline projects by GW,          │ Bar: top      │
│ coloured by status; hydrogen-linked marked    │ owners by     │
│                                               │ operating GW  │
├───────────────────────────────────────────────┴───────────────┤
│ Project table: name (EN or AR) · country · technology ·       │
│ status (colour) · GW (data bar) · start year · owner ·        │
│ hydrogen flag. Sorted by GW                                   │
├───────────────────────────────────────────────────────────────┤
│ Filters from drillthrough shown · [← Back] │
└───────────────────────────────────────────────────────────────┘
```

| Visual | What it highlights |
|---|---|
| Top 10 projects | **The top 20 projects hold 50% of the 447 GW pipeline**, and the top 10 hold 35%. The two largest are 30 GW each in Mauritania, both still announced or pre-construction |
| Hydrogen flag | **253 GW (57%) of the pipeline is linked to green-hydrogen production** (units flagged by GEM). This is export-driven demand, not local grid demand |
| Top owners (operating) | Who owns what is running, weighted by ownership share: ACWA Power 5.7 GW, Badeel 3.8, DEWA 3.7, Egyptian Electricity Holding 2.8 |
| Project table | The full list with exact values; data bars on GW; status colour-coded |

Data caveats on the page:
- Owner is filled for 75% of units. Ultimate parent companies are almost never recorded, so owners are shown, not parents.
- Start year is mostly blank for pipeline projects.

## 6. Data

| Source | Grain | Used for | Licence |
|---|---|---|---|
| Global Energy Monitor, *Global Integrated Power Tracker*, Sept 2026 release | Plant unit / phase | Capacity, status, technology, start year, owners, Arabic plant names | CC BY 4.0 |
| Ember, *Yearly electricity data* | Country × year × source | Generation (TWh), renewable share, emissions intensity, demand | CC BY 4.0 |

**Filters applied:**
- Countries: the 22 Arab League members.
- Types: utility-scale solar, wind, hydropower, bioenergy, geothermal.
- Rows excluded: those tagged with a TransitionZero ID, which are CC BY-NC (non-commercial only). This removes 421 small solar units and keeps the whole dataset CC BY.

**Result:** 957 units / 758 plants. Of these, 270 plants (49.8 GW) are operating.

**Data facts that shape the design:**
- **Ember coverage drops after 2023.** All 22 countries have data for 2023, 21 for 2024, and only 7 for 2025.
  - **Decision:** use each country's latest available year.
  - Show that year as a label wherever an Ember figure appears, e.g. "Saudi Arabia (2025)", "Jordan (2024)", "Comoros (2023)".
- **Status scope (decided):**
  - Capacity totals = operating + pipeline (construction, pre-construction, announced).
  - Shelved, cancelled, mothballed and retired units are excluded from totals.
  - Shelved and cancelled units are used only in the delivery-risk measure.
- **Start year** is filled for 492 of 957 units. The gaps are almost all pipeline projects: 97% of operating capacity has a start year, so the growth trend is reliable.
- **Owners** are filled for 722 of 957 units. Ultimate parent companies are almost never filled (19 of 957), so we show owners, not parents.
- **Coverage.** GEM tracks utility-scale plants only; rooftop solar is not included. Ember generation covers everything. So capacity (GEM) and generation (Ember) must not be divided into a "capacity factor".
- **A few very large projects dominate the pipeline.** The largest single entry is 29.4 GW. Many large entries are linked to green hydrogen (101 units have a hydrogen flag). The detail page should make this visible.
- **Arabic plant names** are published by GEM for 368 of 758 plants. The rest keep their English name on Arabic pages.

## 7. Bilingual and RTL requirements

- The language switch is driven by a translations table and DAX label measures.
- Arabic pages are mirrored by Python scripts: positions, alignment, axes, data bars.
- Translation provenance is tracked per string:
  - `source` (published by GEM),
  - `machine` (machine-drafted),
  - `reviewed` (checked by a native speaker).
- The README states the counts for each.

## 8. Out of scope

- Forecasts, financial metrics (cost, tariffs), grid or transmission data.
- Rooftop / distributed solar.
- Plant-level generation or capacity factors (not in the data).
- Real-time refresh: this is a periodic snapshot.

## 9. Decisions log

| # | Question | Decision |
|---|---|---|
| 1 | Page 2 focus | Use the most complete fields: country, type, status, capacity (all 100%) |
| 2 | Status scope | Totals include the pipeline. Shelved / cancelled count only toward delivery risk |
| 3 | Ember year | Each country's latest year, labelled |
| 4 | Opportunity scatter axes | X = wind + solar share, Y = GW under construction, size = total generation |
| 5 | Page order | Overview → Breakdown → Opportunity → Detail |
| 6 | Opportunity page support | Region trend to 2023 as default; reference lines at the regional weighted share |
| 7 | Navigation buttons | Moved from the bottom corner to the header (Back / Next); see `visual-guidelines.md` |
| 8 | Hydrogen-linked capacity | Unit level, as GEM flags it: 253 GW, 57% of the pipeline |
| 9 | Owner capacity | Weighted by ownership share; owners without a stated share split the remainder equally |
| 10 | World benchmark | Added: Ember world wind+solar share, used as the comparison line in the share KPI (region 3.8% vs world 13.4% in 2023) |
