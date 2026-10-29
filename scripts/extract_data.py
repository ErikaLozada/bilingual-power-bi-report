"""Build the model's CSV tables from the GEM tracker and Ember yearly data.

Usage:
    python scripts/extract_data.py "Global Integrated Power September 2026 V2.xlsx" [ember.csv]

The Ember yearly CSV is downloaded unless a local copy is given.

Writes one CSV per model table into data/, plus data/sources.json.
Arabic names for countries, technologies and statuses come from
translations/translations.csv; Arabic plant names come from GEM. Where GEM gives
separate plants the same Arabic name, the technology (or, within one technology,
a machine-drafted site name from translations.csv) is appended so each is unique.
"""
import csv
import datetime
import hashlib
import io
import json
import re
import sys
import urllib.request
from collections import Counter, defaultdict
from pathlib import Path

import openpyxl

ROOT = Path(__file__).resolve().parent.parent
DATA = ROOT / "data"
TRANSLATIONS = ROOT / "translations" / "translations.csv"

GEM_RELEASE = "Global Integrated Power Tracker, September 2026"
EMBER_URL = "https://files.ember-energy.org/public-downloads/generation/outputs/release_generation_yearly_global.csv"
FIRST_EMBER_YEAR = 2010

# Arab League members: GEM name -> ISO 3 code (Ember uses ISO 3 too)
COUNTRIES = {
    "Algeria": "DZA", "Bahrain": "BHR", "Comoros": "COM", "Djibouti": "DJI",
    "Egypt": "EGY", "Iraq": "IRQ", "Jordan": "JOR", "Kuwait": "KWT",
    "Lebanon": "LBN", "Libya": "LBY", "Mauritania": "MRT", "Morocco": "MAR",
    "Oman": "OMN", "Palestine": "PSE", "Qatar": "QAT", "Saudi Arabia": "SAU",
    "Somalia": "SOM", "Sudan": "SDN", "Syria": "SYR", "Tunisia": "TUN",
    "United Arab Emirates": "ARE", "Yemen": "YEM",
}

# GEM type -> (technology id, colour group id, sort order)
TECHNOLOGIES = {
    "utility-scale solar": ("solar", "solar", 1),
    "wind": ("wind", "wind", 2),
    "hydropower": ("hydro", "hydro", 3),
    "bioenergy": ("bioenergy", "other", 4),
    "geothermal": ("geothermal", "other", 5),
}
GROUP_ORDER = {"solar": 1, "wind": 2, "hydro": 3, "other": 4}

# status id -> (sort order, in totals, in pipeline, delivery risk)
STATUSES = {
    "operating": (1, True, False, False),
    "construction": (2, True, True, False),
    "pre-construction": (3, True, True, False),
    "announced": (4, True, True, False),
    "shelved": (5, False, False, True),
    "cancelled": (6, False, False, True),
    "mothballed": (7, False, False, False),
    "retired": (8, False, False, False),
}

# TransitionZero IDs mark rows licensed CC BY-NC; excluding them keeps the data CC BY
NON_COMMERCIAL_ID = re.compile(r"\bTZ:")
ARABIC_SCRIPT = re.compile(r"[؀-ۿ]")
OWNER_SHARE = re.compile(r"\s*(.*?)\s*\[([\d.]+)%\]\s*$")


def status_id(gem_status):
    # GEM adds suffixes such as "shelved - inferred 2 y"
    return gem_status.split(" - ")[0].strip()


def load_translations():
    with open(TRANSLATIONS, encoding="utf-8", newline="") as f:
        return {row["key"]: row for row in csv.DictReader(f)}


def write_csv(name, header, rows):
    with open(DATA / name, "w", encoding="utf-8", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(header)
        writer.writerows(rows)
    print(f"{name}: {len(rows)} rows")


def sha256(data):
    return hashlib.sha256(data).hexdigest()


def read_gem(path):
    wb = openpyxl.load_workbook(path, read_only=True)
    sheet = wb["Power facilities"]
    rows = sheet.iter_rows(values_only=True)
    header = next(rows)
    col = {name: i for i, name in enumerate(header)}
    units, excluded = [], 0
    for r in rows:
        if r[col["Country/area"]] not in COUNTRIES or r[col["Type"]] not in TECHNOLOGIES:
            continue
        if NON_COMMERCIAL_ID.search(r[col["Other IDs (unit/phase)"]] or ""):
            excluded += 1
            continue
        units.append({name: r[i] for name, i in col.items()})
    print(f"GEM: {len(units)} units kept, {excluded} CC BY-NC units excluded")
    return units


def owner_shares(owners):
    """Split "A [50%]; B; C [25%]" into (owner, share) pairs.

    Owners without a percentage split whatever the stated percentages leave.
    """
    parsed = []
    for part in owners.split(";"):
        m = OWNER_SHARE.match(part)
        parsed.append((m.group(1), float(m.group(2)) / 100) if m else (part.strip(), None))
    stated = sum(s for _, s in parsed if s is not None)
    unstated = [o for o, s in parsed if s is None]
    rest = max(0.0, 1 - stated) / len(unstated) if unstated else 0.0
    return [(o, s if s is not None else rest) for o, s in parsed]


def plant_arabic_name(local_names):
    # Units list comma-separated local names; the plant name is the one most units share
    # Ties go to the name listed first, so reruns give the same result
    counts = Counter()
    for names in local_names:
        counts.update(list(dict.fromkeys(n.strip() for n in names.split(",") if ARABIC_SCRIPT.search(n))))
    return max(counts, key=counts.get) if counts else None


def unique_arabic_names(plant_rows, plant_techs, tr):
    # Visuals group by name, so plants sharing an Arabic name would merge. Append the technology
    # when the group mixes technologies, else the site name; the suffix is a draft, so mark it machine
    groups = defaultdict(list)
    for row in plant_rows:
        if row[3] == "source":
            groups[row[2]].append(row)
    for name, rows in groups.items():
        if len(rows) < 2:
            continue
        techs = [sorted(plant_techs[r[0]]) for r in rows]
        mixed = len({tuple(t) for t in techs}) == len(rows)
        for row, t in zip(rows, techs):
            suffix = tr[f"tech.{t[0]}"]["ar"] if mixed else tr[f"plant.{row[0]}"]["ar"]
            row[2], row[3] = f"{name} – {suffix}", "machine"


def build_gem_tables(units, tr):
    unit_rows, ownership_rows, plants, local_names = [], [], {}, defaultdict(list)
    plant_techs = defaultdict(set)
    for u in units:
        plant_id = u["GEM location ID"]
        unit_id = u["GEM unit/phase ID"]
        tech_id = TECHNOLOGIES[u["Type"]][0]
        unit_name = u["Unit / Phase name"] or ""
        unit_rows.append([
            unit_id, plant_id, COUNTRIES[u["Country/area"]], tech_id,
            status_id(u["Status"]), "" if unit_name == "--" else unit_name, u["Capacity (MW)"],
            u["Start year"] or "", u["Owner(s)"] or "", u["Hydrogen production"] == "yes",
        ])
        if u["Owner(s)"]:
            ownership_rows += [[unit_id, o, round(s, 4)] for o, s in owner_shares(u["Owner(s)"])]
        plants.setdefault(plant_id, [plant_id, u["Plant / Project name"], COUNTRIES[u["Country/area"]]])
        local_names[plant_id].append(u["Plant / Project name (local)"] or "")
        plant_techs[plant_id].add(tech_id)

    plant_rows = []
    for plant_id, name, country in plants.values():
        ar = plant_arabic_name(local_names[plant_id])
        plant_rows.append([plant_id, name, ar or name, "source" if ar else "none", country])
    unique_arabic_names(plant_rows, plant_techs, tr)
    write_csv("unit.csv", ["Unit ID", "Plant ID", "Country ID", "Technology ID", "Status ID",
                           "Unit", "Capacity MW", "Start Year", "Owner", "Hydrogen"], unit_rows)
    write_csv("ownership.csv", ["Unit ID", "Owner", "Share"], ownership_rows)
    write_csv("plant.csv", ["Plant ID", "Plant", "Plant AR", "Plant AR Provenance", "Country ID"],
              plant_rows)

    tech_rows = []
    for tech_id, group, order in TECHNOLOGIES.values():
        t, g = tr[f"tech.{tech_id}"], tr[f"techgroup.{group}"]
        tech_rows.append([tech_id, t["en"], t["ar"], t["provenance"],
                          g["en"], g["ar"], g["provenance"], order, GROUP_ORDER[group]])
    write_csv("technology.csv", ["Technology ID", "Technology", "Technology AR",
                                 "Technology AR Provenance", "Technology Group",
                                 "Technology Group AR", "Technology Group AR Provenance",
                                 "Sort Order", "Group Sort Order"], tech_rows)

    status_rows = []
    for sid, (order, in_totals, in_pipeline, risk) in STATUSES.items():
        s = tr[f"status.{sid}"]
        status_rows.append([sid, s["en"], s["ar"], s["provenance"], order,
                            in_totals, in_pipeline, risk])
    write_csv("status.csv", ["Status ID", "Status", "Status AR", "Status AR Provenance",
                             "Sort Order", "In Totals", "In Pipeline", "Delivery Risk"],
              status_rows)

    unknown = {r[4] for r in unit_rows} - STATUSES.keys()
    if unknown:
        sys.exit(f"Unknown GEM statuses: {unknown}")


def build_ember_tables(raw, tr):
    # One row per country and year: wind + solar and total generation, emissions.
    # The world total is kept separately as a benchmark.
    years, world = {}, {}
    for r in csv.DictReader(io.StringIO(raw.decode("utf-8"))):
        iso = r["ISO 3 code"]
        if int(r["Year"]) < FIRST_EMBER_YEAR:
            continue
        if r["Area"] == "World":
            row = world.setdefault(int(r["Year"]), {})
        elif iso in COUNTRIES.values():
            row = years.setdefault((iso, int(r["Year"])), {})
        else:
            continue
        if r["Electricity source"] == "Wind and solar":
            row["ws"] = r["Generation (TWh)"]
        elif r["Electricity source"] == "Total generation":
            row["total"] = r["Generation (TWh)"]
            row["emissions"] = r["Emissions (MtCO2e)"]
    gen_rows = [[iso, year, v.get("ws", ""), v.get("total", ""), v.get("emissions", "")]
                for (iso, year), v in sorted(years.items()) if v.get("total")]
    write_csv("generation.csv", ["Country ID", "Year", "Wind Solar TWh", "Total Generation TWh",
                                 "Emissions MtCO2e"], gen_rows)
    write_csv("world_generation.csv", ["Year", "Wind Solar TWh", "Total Generation TWh"],
              [[year, v.get("ws", ""), v["total"]] for year, v in sorted(world.items()) if v.get("total")])

    latest = {}
    for iso, year, *_ in gen_rows:
        latest[iso] = max(latest.get(iso, 0), year)
    country_rows = []
    for name, iso in COUNTRIES.items():
        t = tr[f"country.{iso}"]
        country_rows.append([iso, name, t["ar"], t["provenance"], latest.get(iso, "")])
    write_csv("country.csv", ["Country ID", "Country", "Country AR", "Country AR Provenance",
                              "Ember Latest Year"], country_rows)
    missing = [iso for iso in COUNTRIES.values() if iso not in latest]
    if missing:
        print(f"Warning: no Ember data for {missing}")


def main():
    if len(sys.argv) not in (2, 3):
        sys.exit(__doc__)
    gem_path = Path(sys.argv[1])
    DATA.mkdir(exist_ok=True)
    tr = load_translations()

    build_gem_tables(read_gem(gem_path), tr)

    if len(sys.argv) == 3:
        ember_raw = Path(sys.argv[2]).read_bytes()
    else:
        with urllib.request.urlopen(EMBER_URL) as resp:
            ember_raw = resp.read()
    build_ember_tables(ember_raw, tr)

    sources = {
        "gem": {"release": GEM_RELEASE, "file": gem_path.name,
                "sha256": sha256(gem_path.read_bytes()), "licence": "CC BY 4.0"},
        "ember": {"dataset": "Yearly electricity data", "url": EMBER_URL,
                  "downloaded": datetime.date.today().isoformat(),
                  "sha256": sha256(ember_raw), "licence": "CC BY 4.0"},
    }
    (DATA / "sources.json").write_text(json.dumps(sources, indent=2) + "\n", encoding="utf-8")
    print("sources.json written")


if __name__ == "__main__":
    main()
