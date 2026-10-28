"""Create the mirrored Arabic pages of Renewables.Report from the English pages.

Usage:
    python scripts/mirror_pages.py

For every page named en_<page> it writes ar_<page>, applying the RTL rules in
docs/visual-guidelines.md section 9:
- positions mirrored (x' = width - x - w), text and titles right-aligned;
- static text translated from the "i18n" annotation keys (translations.csv);
- fields swapped to their Arabic columns, series literals translated;
- bar charts grow right to left, time axes run right to left, scatter X reversed;
- table columns reversed (text right, values left), data bars from the right;
- sizes of 16 pt and below grow by 1 pt;
- language filter, page navigation and menu bookmarks point at the Arabic pages.
"""
import copy
import csv
import json
import re
import shutil
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DEFINITION = ROOT / "Renewables.Report" / "definition"
PAGE_WIDTH = 1920

# English column -> Arabic twin
AR_COLUMNS = {
    ("Country", "Country"): "Country AR",
    ("Plant", "Plant"): "Plant AR",
    ("Status", "Status"): "Status AR",
    ("Technology", "Technology"): "Technology AR",
    ("Technology", "Technology Group"): "Technology Group AR",
    ("Overview Focus", "Focus"): "Focus AR",
}
# Translation key prefixes that hold the values of those columns
VALUE_KEYS = {("Status", "Status"): "status.", ("Technology", "Technology Group"): "techgroup.",
              ("Technology", "Technology"): "tech.", ("Country", "Country"): "country."}

with open(ROOT / "translations" / "translations.csv", encoding="utf-8", newline="") as f:
    ROWS = list(csv.DictReader(f))
AR = {r["key"]: r["ar"] for r in ROWS}
AR_VALUES = {column: {r["en"]: r["ar"] for r in ROWS if r["key"].startswith(prefix)}
             for column, prefix in VALUE_KEYS.items()}


RLE, PDF = "\u202b", "\u202c"


def rtl(text):
    """Right-to-left embedding: Power BI text boxes are LTR, so Arabic mixed with Latin or digits needs it."""
    return RLE + text + PDF


def literal(node):
    return node["expr"]["Literal"]["Value"]


def set_literal(node, value):
    node["expr"]["Literal"]["Value"] = value


def quoted(text):
    return "'" + text.replace("'", "''") + "'"


def walk(node, fn):
    fn(node)
    if isinstance(node, dict):
        for value in node.values():
            walk(value, fn)
    elif isinstance(node, list):
        for value in node:
            walk(value, fn)


# --- text ---------------------------------------------------------------------

def translate_text(visual, i18n):
    body = visual["visual"]
    vco = body.get("visualContainerObjects", {})
    if "title" in i18n:
        set_literal(vco["title"][0]["properties"]["text"], quoted(rtl(AR[i18n["title"]])))
    if "runs" in i18n:
        paragraphs = body["objects"]["general"][0]["properties"]["paragraphs"]
        runs = [run for p in paragraphs for run in p["textRuns"]]
        for run, key in zip(runs, i18n["runs"]):
            run["value"] = rtl(AR[key])
        # Runs lay out left to right, so reverse them to read right to left (e.g. legend swatch before its label)
        for p in paragraphs:
            p["textRuns"].reverse()
    if "button" in i18n:
        entry = next(e for e in body["objects"]["text"] if "text" in e["properties"])
        set_literal(entry["properties"]["text"], quoted(AR[i18n["button"]]))
    for projections in body.get("query", {}).get("queryState", {}).values():
        for p in projections["projections"]:
            key = i18n.get("display", {}).get(p["queryRef"])
            if key:
                p["displayName"] = AR[key]


def bump_font_sizes(visual):
    """Arabic text is 1 pt larger at 16 pt and below (visual-guidelines.md section 7)."""
    def fn(node):
        if not isinstance(node, dict):
            return
        for key in ("fontSize", "textSize", "titleFontSize"):
            value = node.get(key)
            if isinstance(value, dict) and "expr" in value:
                size = float(literal(value)[:-1])
                if size <= 16:
                    set_literal(value, f"{size + 1:g}D")
            elif isinstance(value, str) and value.endswith("pt") and float(value[:-2]) <= 16:
                node[key] = f"{float(value[:-2]) + 1:g}pt"
    walk(visual, fn)


def align_right(visual):
    def fn(node):
        if not isinstance(node, dict):
            return
        if "paragraphs" in node:
            for p in node["paragraphs"]:
                p["horizontalTextAlignment"] = "left" if p.get("horizontalTextAlignment") == "right" else "right"
        alignment = node.get("alignment")
        if isinstance(alignment, dict) and "expr" in alignment:
            # Mirror left <-> right (anything else goes right); keep the case, table columns need 'Left' / 'Right'
            value = literal(alignment)
            target = "left" if value.lower() == "'right'" else "right"
            set_literal(alignment, f"'{target.capitalize() if value[1:2].isupper() else target}'")
    walk(visual["visual"].get("objects", {}), fn)
    walk(visual["visual"].get("visualContainerObjects", {}), fn)


# --- fields -------------------------------------------------------------------

def swap_fields(visual):
    renamed = {}

    def fn(node):
        if not isinstance(node, dict):
            return
        column = node.get("Column")
        if isinstance(column, dict) and "Entity" in column["Expression"]["SourceRef"]:
            key = (column["Expression"]["SourceRef"]["Entity"], column["Property"])
            if key in AR_COLUMNS:
                column["Property"] = AR_COLUMNS[key]
                renamed[f"{key[0]}.{key[1]}"] = f"{key[0]}.{AR_COLUMNS[key]}"
        comparison = node.get("Comparison")
        if isinstance(comparison, dict) and "Column" in comparison.get("Left", {}):
            left = comparison["Left"]["Column"]
            key = (left["Expression"]["SourceRef"].get("Entity"), left["Property"])
            value = comparison["Right"].get("Literal", {}).get("Value", "")
            if key in AR_VALUES and value.startswith("'"):
                comparison["Right"]["Literal"]["Value"] = quoted(AR_VALUES[key].get(value[1:-1], value[1:-1]))

    walk(visual, fn)

    def refs(node):
        if isinstance(node, dict):
            if node.get("queryRef") in renamed:
                node["queryRef"] = renamed[node["queryRef"]]
                node["nativeQueryRef"] = node["queryRef"].split(".", 1)[1]
            if node.get("metadata") in renamed:
                node["metadata"] = renamed[node["metadata"]]
    walk(visual, refs)


# --- geometry and axes --------------------------------------------------------

def mirror_axes(visual):
    body = visual["visual"]
    kind = body["visualType"]
    objects = body.setdefault("objects", {})
    lit = lambda v: {"expr": {"Literal": {"Value": v}}}
    if kind in ("barChart", "clusteredBarChart"):
        objects.setdefault("valueAxis", [{"properties": {}}])[0]["properties"]["invertAxis"] = lit("true")
        objects.setdefault("categoryAxis", [{"properties": {}}])[0]["properties"]["switchAxisPosition"] = lit("true")
    if kind in ("lineChart", "columnChart", "clusteredColumnChart", "lineStackedColumnComboChart"):
        # Time runs right to left: earliest year on the right
        category = body["query"]["queryState"]["Category"]["projections"][0]["field"]
        body["query"]["sortDefinition"] = {"sort": [{"field": category, "direction": "Descending"}], "isDefaultSort": True}
        objects.setdefault("valueAxis", [{"properties": {}}])[0]["properties"]["position"] = lit("'Right'")
    if kind == "scatterChart":
        objects.setdefault("categoryAxis", [{"properties": {}}])[0]["properties"]["invertAxis"] = lit("true")
        objects.setdefault("valueAxis", [{"properties": {}}])[0]["properties"]["position"] = lit("'Right'")
        objects["valueAxis"][0]["properties"]["switchAxisPosition"] = lit("true")
    if "legend" in objects:
        props = objects["legend"][0]["properties"]
        if "position" in props:
            props["position"] = lit("'TopRight'")
    if kind == "tableEx":
        values = body["query"]["queryState"]["Values"]["projections"]
        values.reverse()
        formatting = objects.setdefault("columnFormatting", [])
        for entry in formatting:
            if "dataBars" in entry["properties"]:
                entry["properties"]["dataBars"]["reverseDirection"] = lit("true")


def mirror_position(visual):
    pos = visual["position"]
    pos["x"] = round(PAGE_WIDTH - pos["x"] - pos["width"], 2)


def retarget(node, en_page, ar_page, role):
    """Page navigation goes to Arabic pages; the language button goes back to English."""
    def fn(n):
        if not isinstance(n, dict):
            return
        for key in ("navigationSection", "bookmark"):
            value = n.get(key)
            if isinstance(value, dict) and "expr" in value:
                target = literal(value)
                if role == "language":
                    set_literal(value, f"'{en_page}'")
                else:
                    set_literal(value, target.replace("en_", "ar_"))
    walk(node, fn)


# --- pages --------------------------------------------------------------------

def mirror_page(en_dir):
    en_page = en_dir.name
    ar_page = "ar_" + en_page[3:]
    ar_dir = en_dir.parent / ar_page
    shutil.rmtree(ar_dir, ignore_errors=True)
    shutil.copytree(en_dir, ar_dir)

    page_file = ar_dir / "page.json"
    page = json.loads(page_file.read_text(encoding="utf-8"))
    i18n = json.loads(page["annotations"][0]["value"])
    page["name"] = ar_page
    page["displayName"] = AR[i18n["name"]]
    for flt in page["filterConfig"]["filters"]:
        flt["name"] = flt["name"].replace(en_page, ar_page)
        walk(flt, lambda n: isinstance(n, dict) and n.get("Value") == "'en'" and n.update(Value="'ar'"))
    page_file.write_text(json.dumps(page, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")

    for visual_file in sorted(ar_dir.glob("visuals/*/visual.json")):
        visual = json.loads(visual_file.read_text(encoding="utf-8"))
        i18n = json.loads(next((a["value"] for a in visual.get("annotations", []) if a["name"] == "i18n"), "{}"))
        translate_text(visual, i18n)
        swap_fields(visual)
        mirror_position(visual)
        align_right(visual)
        mirror_axes(visual)
        bump_font_sizes(visual)
        retarget(visual, en_page, ar_page, i18n.get("role"))
        visual_file.write_text(json.dumps(visual, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    return en_page, ar_page


def mirror_bookmarks(pairs):
    folder = DEFINITION / "bookmarks"
    meta = json.loads((folder / "bookmarks.json").read_text(encoding="utf-8"))
    names = [item["name"] for item in meta["items"]]
    for en_page, ar_page in pairs:
        for file in sorted(folder.glob(f"bm_{en_page}_*.bookmark.json")):
            text = file.read_text(encoding="utf-8").replace(en_page, ar_page)
            obj = json.loads(text)
            (folder / f"{obj['name']}.bookmark.json").write_text(text, encoding="utf-8")
            if obj["name"] not in names:
                names.append(obj["name"])
    meta["items"] = [{"name": nm} for nm in names]
    (folder / "bookmarks.json").write_text(json.dumps(meta, indent=2) + "\n", encoding="utf-8")


def main():
    pages_dir = DEFINITION / "pages"
    for old in pages_dir.glob("ar_*"):
        shutil.rmtree(old)
    pairs = [mirror_page(d) for d in sorted(pages_dir.glob("en_*")) if d.is_dir()]
    mirror_bookmarks(pairs)
    meta_file = pages_dir / "pages.json"
    meta = json.loads(meta_file.read_text(encoding="utf-8"))
    english = [p for p in meta["pageOrder"] if p.startswith("en_")]
    meta["pageOrder"] = english + ["ar_" + p[3:] for p in english]
    meta_file.write_text(json.dumps(meta, indent=2) + "\n", encoding="utf-8")
    print(f"mirrored {len(pairs)} pages into Arabic")


if __name__ == "__main__":
    main()
