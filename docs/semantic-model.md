# Semantic model

> **Status: agreed (v1).** The measure list is a draft; insight titles are tested during development. Changes are recorded in the decisions log (section 9).

## 1. Shape

```
Country ──────┐                ┌── Technology
(EN/AR names, │                │   (EN/AR, colour group: Solar/Wind/Hydro/Other)
 latest Ember │                │
 year + values)│     Unit      │
              ├── (957 rows, ──┤
Status ───────┘   unit grain)  └── Plant (EN/AR name)
                      │
                  Ownership (unit, owner, share)
(EN/AR, stage order,
 in-totals / risk-only)

Generation (country × year: wind+solar TWh, total TWh, emissions) ── Country
Translations (key, en, ar, provenance)  ┐ disconnected
Language (en / ar)                      │ helper tables
Refresh info (one row, refresh time)    ┘
Measures table (every measure lives in the model, so Publish to web works)
```

Table names follow section 6.

## 2. Data loading

- The extract script writes filtered CSV files into the repo.
- Power Query reads each CSV from its raw GitHub URL. Refreshing in Fabric needs no gateway, and the footer's "Refreshed" time reflects a real refresh.
- The repo must be public, and the CSV paths are part of the model's contract: moving a file breaks the refresh.
- **Credentials (once per tenant user):** Fabric stores the credential per data source, so setting it on one model covers every model using the same URL. Model settings → Data source credentials → Anonymous, privacy Public, **Skip test connection**. The test fetches the repo root, which raw GitHub answers with 404, so it can't pass and can't be set by API.

## 3. Grain

The fact table is at **unit (phase) level**: 957 rows, as GEM publishes it. Status and capacity belong to units, and one plant can have units at different statuses.

## 3a. Ownership

- `Ownership` has one row per unit and owner, with the owner's share (0–1). It is filtered by `Unit`.
- GEM writes owners as `A [50%]; B; C [25%]`. Owners without a percentage split whatever the stated percentages leave.
- Owner GW = capacity × share, so owner totals add up to the real capacity. A few units (24) have stated shares under 100% and keep the remainder unallocated.
- `Unit` keeps GEM's original owner text for the project table.

## 4. Arabic data values

- Each dimension has an English and an Arabic column (for example, country name EN / AR). Arabic pages use the Arabic column in axes, slicers and tables.
- Each Arabic column has a matching provenance value: `source` (GEM), `machine` or `reviewed`.
- The translations table holds UI text only: titles, headlines, labels, notes and menu text.
- **Plant names:** the Arabic name comes from GEM's local-name field. GEM stores it per unit as a comma-separated list; the plant takes the name most of its units share. 368 of 758 plants have one (`source`); the rest show the English name (`none`).
- **Owner names** stay as published (Latin script) on both pages.

## 5. Language selection

- A disconnected `Language` table holds `en` and `ar`.
- Every page has a page-level filter on it: `en` on English pages, `ar` on Arabic pages.
- Dynamic text measures (section 7) read the filtered value to return the right text. There is no language slicer; the language button switches pages.

## 6. Naming conventions

- **Tables:** plain business names: `Country`, `Technology`, `Status`, `Plant`, `Unit`, `Ownership`, `Generation`, `Translations`, `Language`, `Refresh Info`, `_Measures` (the underscore keeps it at the top of the field list). No `Dim` / `Fact` prefixes.
- **Columns:** Title Case with spaces (`Start Year`, `Capacity MW`). Arabic twins take an `AR` suffix (`Country AR`); provenance columns add `Provenance` (`Country AR Provenance`).
- **Hidden:** keys and helper columns (`Unit ID`, sort-order columns).
- **Measures:** say what they return, unit included (`Operating GW`, `Wind Solar Share %`), grouped in display folders.

## 7. Translating text

| Kind of text | How it is translated |
|---|---|
| **Static:** axis titles, column headers, tooltip field names, legend titles, KPI labels, button, menu and footer labels | At build time. The build/mirror script writes the Arabic text from the translations CSV straight into the Arabic page's visual JSON (literal titles, field display names). No DAX |
| **Dynamic:** text with numbers or that reacts to filters (headlines, insight titles, refresh time, Ember year labels) | At run time. A DAX measure fills a translated template (`{placeholders}`) and picks EN or AR from the page's Language filter |

- The translations CSV holds every string with its provenance, so the README counts cover both kinds.
- Rejected: model translations (TMDL cultures), which switch by browser language, not by page, and aren't supported by Publish to web; and per-language report-page tooltips, which double the tooltip pages.

## 8. Measures (draft)

| Folder | Measures | Notes |
|---|---|---|
| Capacity | `Operating GW`, `Construction GW`, `Pre-construction GW`, `Announced GW`, `Pipeline GW` (construction + pre-construction + announced), `Total GW` (operating + pipeline), `GW Added` (operating, by start year) | Totals exclude shelved and cancelled |
| Risk | `Shelved GW`, `Cancelled GW`, `Construction % of Pipeline`, `Pipeline to Operating Ratio` | |
| Hydrogen | `Hydrogen Pipeline GW`, `Hydrogen % of Pipeline` | |
| Generation | `Wind Solar Share %`, `Emissions Intensity g/kWh`, `Total Generation TWh`, `Ember Year` | Latest year per country; region = weighted (summed TWh); trend to 2023 |
| Headlines | One per page, from a translated template | |
| Formatting | `Accent Colour`, `Status Colour`, `Technology Colour` | Return hex codes for conditional formatting |
| Footer | `Refreshed At`, `Data To` | `dd mmm yy, HH:mm` |

**Insight titles:** visual titles start static. During development we test which visuals benefit from a dynamic takeaway; each one adopted becomes a dynamic measure (section 7).

## 9. Decisions log

| # | Question | Decision |
|---|---|---|
| 1 | Data loading | CSVs in the public repo, read by Power Query from raw GitHub URLs |
| 2 | Fact grain | Unit (phase) level, 957 rows |
| 3 | Arabic data values | EN/AR columns in each dimension, each with provenance; translations table is UI text only |
| 4 | Language selection | Disconnected Language table, fixed by a page-level filter on each page |
| 5 | Table names | Plain business names, `_Measures` for measures |
| 6 | Column names | Title Case; `AR` suffix for Arabic twins; keys and helpers hidden |
| 7 | Measure names | Name what they return, unit included; display folders |
| 8 | Translating text | Static text at build time into the page JSON; dynamic text by DAX template measures |
| 9 | Measure list | Draft in section 8; insight titles tested during development |
| 10 | Ownership | `Ownership` bridge table, share-weighted owner GW |
| 11 | Arabic plant names | Most-shared Arabic local name across a plant's units; English fallback flagged `none` |
| 12 | Unit names | GEM's "--" placeholder stored as blank |
| 13 | Hydrogen | Unit-level flag as published |
| 14 | Generation shape | One row per country and year with wind+solar TWh, total TWh and emissions, so regional shares and intensity are sums of TWh and emissions |
