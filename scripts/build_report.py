"""Build the English pages of Renewables.Report (PBIR) from the page specs below.

Usage:
    python scripts/build_report.py

Every piece of static text is written in English and its translation key is
stored in the visual's "i18n" annotation, so scripts/mirror_pages.py can turn
each English page into its mirrored Arabic twin. Layout and styling follow
docs/visual-guidelines.md.
"""
import csv
import json
import shutil
import uuid
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
REPORT = ROOT / "Renewables.Report"
DEFINITION = REPORT / "definition"
SCHEMA = "https://developer.microsoft.com/json-schemas/fabric/item/report/definition"

# Canvas and spacing (visual-guidelines.md sections 1-2)
W, H, M, G = 1920, 1080, 20, 20
HEADER_Y, HEADER_H = 20, 80
BODY_Y, BODY_BOTTOM = 120, 1000
FOOTER_Y, FOOTER_H = 1020, 40
KPI_H = 260
MAIN_Y = BODY_Y + KPI_H + G

# Colours and fonts (sections 6-7)
CANVAS, CARD, RULE, INK, INK2 = "#f4f4f2", "#ffffff", "#e4e3df", "#1d1d1b", "#5c5b57"
ACCENT, GREY_LINE = "#eb6834", "#b3b2ac"
TECH = {"Solar": "#eda100", "Wind": "#1baf7a", "Hydro": "#2a78d6", "Other": "#b3b2ac"}
STATUS = {"Operating": "#2b2570", "Under construction": "#4a3fb0", "Pre-construction": "#7368d9",
          "Announced": "#a49cea", "Shelved": "#9e9d97", "Cancelled": "#9e9d97"}
FONT = "'Segoe UI', wf_segoe-ui_normal, helvetica, arial, sans-serif"
FONT_SEMI = "'Segoe UI Semibold', wf_segoe-ui_semibold, helvetica, arial, sans-serif"

PAGES = ["overview", "breakdown", "opportunity", "detail"]

with open(ROOT / "translations" / "translations.csv", encoding="utf-8", newline="") as f:
    TEXT = {row["key"]: row["en"] for row in csv.DictReader(f)}


# --- expression helpers -------------------------------------------------------

def lit(value):
    return {"expr": {"Literal": {"Value": value}}}


def s(text):
    return lit("'" + text.replace("'", "''") + "'")


def n(number):
    return lit(f"{number}D")


def b(flag):
    return lit("true" if flag else "false")


def colour(hex_):
    return {"solid": {"color": s(hex_)}}


def col(entity, prop):
    return {"Column": {"Expression": {"SourceRef": {"Entity": entity}}, "Property": prop}}


def mea(prop):
    return {"Measure": {"Expression": {"SourceRef": {"Entity": "_Measures"}}, "Property": prop}}


def ref(field):
    kind = "Column" if "Column" in field else "Measure"
    return f'{field[kind]["Expression"]["SourceRef"]["Entity"]}.{field[kind]["Property"]}'


class Visual:
    """A visual plus the translation keys of its static text."""

    def __init__(self, visual_type, query=None, objects=None, title_key=None, pad=(12, 12, 16, 16)):
        self.i18n = {}
        self.body = {"visualType": visual_type}
        if query:
            self.body["query"] = query
        self.body["objects"] = objects or {}
        self.body["visualContainerObjects"] = container(pad)
        if title_key:
            self.title(title_key)
        self.filters = []
        self.hidden = False

    def title(self, key, size=16, color=INK, font=FONT_SEMI):
        self.i18n["title"] = key
        self.body["visualContainerObjects"]["title"] = [{"properties": {
            "show": b(True), "text": s(TEXT[key]), "fontFamily": s(font), "fontSize": n(size),
            "fontColor": colour(color), "alignment": s("left"), "titleWrap": b(True)}}]
        return self

    def measure_title(self, measure, size=13, color=INK2, font=FONT):
        self.body["visualContainerObjects"]["title"] = [{"properties": {
            "show": b(True), "text": {"expr": mea(measure)}, "fontFamily": s(font), "fontSize": n(size),
            "fontColor": colour(color), "alignment": s("left"), "titleWrap": b(True)}}]
        return self


def container(pad):
    return {
        "title": [{"properties": {"show": b(False)}}],
        "background": [{"properties": {"show": b(True), "color": colour(CARD), "transparency": n(0)}}],
        "border": [{"properties": {"show": b(False)}}],
        "dropShadow": [{"properties": {"show": b(False)}}],
        "padding": [{"properties": {"top": n(pad[0]), "bottom": n(pad[1]), "left": n(pad[2]), "right": n(pad[3])}}],
        "visualHeader": [{"properties": {"show": b(False)}}],
    }


def projection(v, field, display_key=None):
    p = {"field": field, "queryRef": ref(field), "nativeQueryRef": field.get("Column", field.get("Measure"))["Property"]}
    if display_key:
        p["displayName"] = TEXT[display_key]
        v.i18n.setdefault("display", {})[ref(field)] = display_key
    return p


# --- components ---------------------------------------------------------------

def textbox(runs, align=None, pad=(12, 12, 16, 16), background=True):
    """runs: (translation key, size pt, colour, font)."""
    v = Visual("textbox", pad=pad)
    v.i18n["runs"] = [key for key, *_ in runs]
    para = {"textRuns": [{"value": TEXT[key], "textStyle": {"fontFamily": font, "fontSize": f"{size}pt", "color": c}}
                         for key, size, c, font in runs]}
    if align:
        para["horizontalTextAlignment"] = align
    v.body["objects"] = {"general": [{"properties": {"paragraphs": [para]}}]}
    if not background:
        v.body["visualContainerObjects"]["background"] = [{"properties": {"show": b(False)}}]
    return v


def measure_text(measure, size, color=INK, font=FONT, pad=(0, 0, 16, 16), background=True):
    """A text measure shown as the title of an empty shape: wraps, aligns, and mirrors."""
    v = Visual("shape", objects={
        "shape": [{"properties": {"tileShape": s("rectangle")}}],
        "fill": [{"properties": {"show": b(False)}}],
        "outline": [{"properties": {"show": b(False)}}],
    }, pad=pad)
    v.measure_title(measure, size, color, font)
    if not background:
        v.body["visualContainerObjects"]["background"] = [{"properties": {"show": b(False)}}]
    return v


def value_card(measure):
    # A shape title holds the number, so it aligns and mirrors like the other text
    return measure_text(f"{measure} Text", 36, INK, FONT_SEMI, pad=(0, 0, 16, 16))


def value_card_multirow(measure):
    v = Visual("multiRowCard", pad=(0, 0, 16, 16))
    v.body["query"] = {"queryState": {"Values": {"projections": [projection(v, mea(measure))]}}}
    v.body["objects"] = {
        "dataLabels": [{"properties": {"color": colour(INK), "fontSize": n(36), "fontFamily": s(FONT_SEMI)}}],
        "categoryLabels": [{"properties": {"show": b(False)}}],
        "card": [{"properties": {"barShow": b(False), "outlineStyle": lit("0D")}}],
    }
    return v


def axis(show=True, size=12, color=INK, **extra):
    props = {"show": b(show), "fontFamily": s(FONT), "fontSize": n(size), "labelColor": colour(color),
             "showAxisTitle": b(False), "gridlineShow": b(False)}
    props.update(extra)
    return [{"properties": props}]


def range_filter(entity, prop, low, high):
    src = {"Column": {"Expression": {"SourceRef": {"Source": "t"}}, "Property": prop}}

    def cmp(kind, value):
        return {"Comparison": {"ComparisonKind": kind, "Left": src, "Right": {"Literal": {"Value": f"{value}L"}}}}

    return {"name": f"f_{entity}_{prop}".replace(" ", "_"), "field": col(entity, prop), "type": "Advanced",
            "filter": {"Version": 2, "From": [{"Name": "t", "Entity": entity, "Type": 0}],
                       "Where": [{"Condition": {"And": {"Left": cmp(2, low), "Right": cmp(4, high)}}}]}}


def in_filter(entity, prop, literal, name=None):
    src = {"Column": {"Expression": {"SourceRef": {"Source": "t"}}, "Property": prop}}
    return {"name": name or f"f_{entity}_{prop}".replace(" ", "_"), "field": col(entity, prop), "type": "Categorical",
            "filter": {"Version": 2, "From": [{"Name": "t", "Entity": entity, "Type": 0}],
                       "Where": [{"Condition": {"In": {"Expressions": [src], "Values": [[{"Literal": {"Value": literal}}]]}}}]}}


def trend(category, series, last_point, status_measure, status_color, label_precision="1L"):
    """KPI trend strip: dark line = measure, light line = comparison, dot + label on the latest point only."""
    v = Visual("lineChart", pad=(4, 4, 16, 16))
    projections = [projection(v, mea(m), key) for m, key, _, _ in series] + [projection(v, mea(last_point))]
    line_styles = [{"properties": {"showMarker": b(False), "strokeWidth": n(2), "lineChartType": s("straight")}}]
    points = []
    labels = [{"properties": {"show": b(True), "color": colour(INK), "fontSize": n(12), "fontFamily": s(FONT_SEMI),
                              "labelPrecision": lit(label_precision), "labelPosition": s("Above")}}]
    for m, _, c, width in series:
        line_styles.append({"properties": {"strokeWidth": n(width)}, "selector": {"metadata": f"_Measures.{m}"}})
        points.append({"properties": {"fill": colour(c)}, "selector": {"metadata": f"_Measures.{m}"}})
        labels.append({"properties": {"showSeries": b(False)}, "selector": {"metadata": f"_Measures.{m}"}})
    line_styles.append({"properties": {"strokeWidth": n(0), "showMarker": b(True), "markerShape": s("circle"),
                                       "markerSize": n(6)}, "selector": {"metadata": f"_Measures.{last_point}"}})
    points.append({"properties": {"fill": colour(INK)}, "selector": {"metadata": f"_Measures.{last_point}"}})
    v.body["query"] = {"queryState": {"Category": {"projections": [projection(v, category)]},
                                      "Y": {"projections": projections}}}
    v.body["objects"] = {"lineStyles": line_styles, "dataPoint": points, "labels": labels,
                         "legend": [{"properties": {"show": b(False)}}],
                         "categoryAxis": axis(size=11, color=INK2, axisType=s("Categorical")),
                         "valueAxis": axis(show=False)}
    v.measure_title(status_measure, 13, status_color)
    return v


def series_colours(entity, prop, colours):
    """Fixed colour per series value (legend), e.g. status or technology."""
    return [{"properties": {"fill": colour(c)},
             "selector": {"data": [{"scopeId": {"Comparison": {"ComparisonKind": 0, "Left": col(entity, prop),
                                                               "Right": {"Literal": {"Value": f"'{value}'"}}}}}]}}
            for value, c in colours.items()]


def bars(category, values, title_key=None, visual_type="barChart", legend=None, fill_measure=None,
         detail_measure=None, sort_by_category=False, sort_measure=None, legend_show=False, size=12):
    """values: (measure, display key). legend: (entity, prop, colours) for stacked series."""
    v = Visual(visual_type, title_key=title_key)
    state = {"Category": {"projections": [projection(v, category)]},
             "Y": {"projections": [projection(v, mea(m), key) for m, key in values]}}
    if legend:
        state["Series"] = {"projections": [projection(v, col(legend[0], legend[1]))]}
    sort_field = category if sort_by_category else mea(sort_measure or values[0][0])
    v.body["query"] = {"queryState": state, "sortDefinition": {
        "sort": [{"field": sort_field, "direction": "Ascending" if sort_by_category else "Descending"}],
        "isDefaultSort": True}}
    data_point = []
    if fill_measure:
        data_point.append({"properties": {"fill": {"solid": {"color": {"expr": mea(fill_measure)}}}},
                           "selector": {"data": [{"dataViewWildcard": {"matchingOption": 1}}]}})
    if legend:
        data_point += series_colours(*legend)
    labels = [{"properties": {"show": b(True), "color": colour(INK), "fontSize": n(size), "fontFamily": s(FONT),
                              "labelDisplayUnits": n(1), "labelPrecision": lit("1L")}}]
    if detail_measure:
        labels[0]["properties"].update({"enableDetailDataLabel": b(True), "labelContentLayout": s("SingleLine"),
                                        "detailColor": colour(INK2)})
        labels.append({"properties": {"dynamicLabelDetail": {"expr": mea(detail_measure)}},
                       "selector": {"data": [{"dataViewWildcard": {"matchingOption": 1}}]}})
    v.body["objects"] = {
        "dataPoint": data_point, "labels": labels,
        "categoryAxis": axis(size=size, maxMarginFactor=n(40)),
        "valueAxis": axis(show=False),
        "legend": [{"properties": {"show": b(legend_show), "position": s("Top"), "fontSize": n(11),
                                   "fontFamily": s(FONT), "labelColor": colour(INK2), "showTitle": b(False)}}],
    }
    return v


def columns_by_technology():
    v = Visual("columnChart", title_key="chart.added-by-tech")
    v.body["query"] = {"queryState": {
        "Category": {"projections": [projection(v, col("Unit", "Start Year"))]},
        "Y": {"projections": [projection(v, mea("Operating GW"), "field.added")]},
        "Series": {"projections": [projection(v, col("Technology", "Technology Group"), "field.technology")]}},
        "sortDefinition": {"sort": [{"field": col("Unit", "Start Year"), "direction": "Ascending"}], "isDefaultSort": True}}
    v.body["objects"] = {
        "dataPoint": series_colours("Technology", "Technology Group", TECH),
        "categoryAxis": axis(size=12, color=INK2, axisType=s("Categorical")),
        "valueAxis": axis(show=False),
        "labels": [{"properties": {"show": b(False)}}],
        "totals": [{"properties": {"show": b(True), "fontSize": n(12), "fontFamily": s(FONT_SEMI),
                                   "color": colour(INK), "labelPrecision": lit("1L")}}],
        "legend": [{"properties": {"show": b(True), "position": s("Top"), "fontSize": n(12),
                                   "fontFamily": s(FONT), "labelColor": colour(INK2), "showTitle": b(False)}}],
    }
    v.filters.append(range_filter("Unit", "Start Year", 2010, 2025))
    return v


def scatter():
    v = Visual("scatterChart", title_key="chart.scatter")
    v.body["query"] = {"queryState": {
        "Category": {"projections": [projection(v, col("Country", "Country"), "field.country")]},
        "X": {"projections": [projection(v, mea("Wind Solar Share %"), "field.share")]},
        "Y": {"projections": [projection(v, mea("Construction GW"), "field.construction")]},
        "Size": {"projections": [projection(v, mea("Total Generation TWh"), "field.generation")]}}}
    v.body["objects"] = {
        "dataPoint": [{"properties": {"fill": {"solid": {"color": {"expr": mea("Top Builder Colour")}}}},
                       "selector": {"data": [{"dataViewWildcard": {"matchingOption": 1}}]}}],
        "categoryLabels": [{"properties": {"show": b(True), "color": colour(INK), "fontSize": n(11),
                                           "fontFamily": s(FONT)}}],
        "categoryAxis": axis(size=11, color=INK2, showAxisTitle=b(True), titleFontSize=n(11),
                             titleColor=colour(INK2), gridlineShow=b(True), gridlineColor=colour(RULE)),
        "valueAxis": axis(size=11, color=INK2, showAxisTitle=b(True), titleFontSize=n(11),
                          titleColor=colour(INK2), gridlineShow=b(True), gridlineColor=colour(RULE)),
        "legend": [{"properties": {"show": b(False)}}],
        "bubbles": [{"properties": {"bubbleSize": lit("-10L")}}],
    }
    return v


def table(columns, bar_measure=None, title_key=None, widths=None, filters=None):
    """columns: (field, display key)."""
    v = Visual("tableEx", title_key=title_key)
    v.body["query"] = {"queryState": {"Values": {"projections": [projection(v, f, key) for f, key in columns]}},
                       "sortDefinition": {"sort": [{"field": mea(bar_measure), "direction": "Descending"}],
                                          "isDefaultSort": True} if bar_measure else None}
    if not bar_measure:
        del v.body["query"]["sortDefinition"]
    v.body["objects"] = {
        "columnHeaders": [{"properties": {"fontFamily": s(FONT_SEMI), "fontSize": n(12), "fontColor": colour(INK2),
                                          "backColor": colour(CARD), "wordWrap": b(True)}}],
        "values": [{"properties": {"fontFamily": s(FONT), "fontSize": n(12), "fontColorPrimary": colour(INK),
                                   "backColorPrimary": colour(CARD), "fontColorSecondary": colour(INK),
                                   "backColorSecondary": colour(CARD)}}],
        "grid": [{"properties": {"gridHorizontal": b(True), "gridHorizontalColor": colour(RULE), "gridVertical": b(False),
                                 "outlineColor": colour(RULE), "rowPadding": n(4)}}],
        "total": [{"properties": {"totals": b(False)}}],
        "columnFormatting": [],
    }
    if bar_measure:
        v.body["objects"]["columnFormatting"].append({
            "properties": {"dataBars": {"positiveColor": colour("#aaa8c6"), "negativeColor": colour(ACCENT),
                                        "axisColor": colour(RULE), "reverseDirection": b(False), "hideText": b(False)}},
            "selector": {"metadata": f"_Measures.{bar_measure}"}})
    if widths:
        v.body["objects"]["columnWidth"] = [{"properties": {"value": n(w)}, "selector": {"metadata": ref(f)}}
                                            for f, w in widths]
    v.filters += filters or []
    return v


def slicer(field, display_key, single=False, mode="Basic"):
    v = Visual("slicer", pad=(8, 8, 16, 16))
    v.body["query"] = {"queryState": {"Values": {"projections": [projection(v, field, display_key)]}}}
    v.body["objects"] = {
        "data": [{"properties": {"mode": s(mode)}}],
        "selection": [{"properties": {"singleSelect": b(single), "selectAllCheckboxEnabled": b(not single)}}],
        "header": [{"properties": {"show": b(True), "fontColor": colour(INK), "fontFamily": s(FONT_SEMI),
                                   "textSize": n(12)}}],
        "items": [{"properties": {"fontColor": colour(INK), "fontFamily": s(FONT), "textSize": n(12)}}],
    }
    return v


def button(text_key, action, role, size=20, width_text=None):
    """action: ("page", page name) or ("bookmark", bookmark name)."""
    v = Visual("actionButton", pad=(0, 0, 0, 0))
    v.i18n.update({"button": text_key, "role": role})
    v.body["objects"] = {
        "icon": [{"properties": {"show": b(False)}}],
        "text": [{"properties": {"show": b(True)}},
                 {"properties": {"text": s(TEXT[text_key]), "fontColor": colour(INK), "fontSize": n(size),
                                 "fontFamily": s(FONT_SEMI), "horizontalAlignment": s("center"),
                                 "verticalAlignment": s("middle")}, "selector": {"id": "default"}}],
        "fill": [{"properties": {"show": b(True)}},
                 {"properties": {"fillColor": colour(CARD), "transparency": n(0)}, "selector": {"id": "default"}}],
        "outline": [{"properties": {"show": b(True)}},
                    {"properties": {"lineColor": colour(RULE), "weight": n(1), "roundEdge": n(6)},
                     "selector": {"id": "default"}}],
    }
    link = {"show": b(True)}
    if action[0] == "page":
        link.update({"type": s("PageNavigation"), "navigationSection": s(action[1])})
    else:
        link.update({"type": s("Bookmark"), "bookmark": s(action[1])})
    v.body["visualContainerObjects"]["visualLink"] = [{"properties": link}]
    v.body["visualContainerObjects"]["background"] = [{"properties": {"show": b(False)}}]
    return v


# --- page frame ---------------------------------------------------------------

def page_frame(page, headline_measure, menu_items, note_key):
    """Header (headline, Back/Next, language, menu), footer, and the hidden menu panel."""
    i = PAGES.index(page)
    name = f"en_{page}"
    items = []
    btn, gap = 56, 10
    x_menu = W - M - btn
    x_lang = x_menu - G - 100
    x_next = x_lang - G - btn
    x_back = x_next - gap - btn
    head_w = x_back - G - M
    items.append(("headline", M, HEADER_Y, head_w, HEADER_H,
                  measure_text(headline_measure, 20, INK, FONT_SEMI, pad=(6, 4, 16, 16))))
    if i > 0:
        items.append(("nav_back", x_back, HEADER_Y + 12, btn, btn,
                      button("nav.back", ("page", f"en_{PAGES[i - 1]}"), "nav")))
    if i < len(PAGES) - 1:
        items.append(("nav_next", x_next, HEADER_Y + 12, btn, btn,
                      button("nav.next", ("page", f"en_{PAGES[i + 1]}"), "nav")))
    items.append(("nav_language", x_lang, HEADER_Y + 12, 100, btn,
                  button("nav.language", ("page", f"ar_{page}"), "language", size=16)))
    items.append(("menu_open", x_menu, HEADER_Y + 12, btn, btn,
                  button("nav.menu-open", ("bookmark", f"bm_{name}_menu_open"), "bookmark")))

    items.append(("footer_source", M, FOOTER_Y, 1100, FOOTER_H,
                  textbox([("footer.source", 11, INK2, FONT)], pad=(10, 0, 16, 16), background=False)))
    items.append(("footer_status", M + 1100 + G, FOOTER_Y, W - 2 * M - 1100 - G, FOOTER_H,
                  measure_text("Footer Status", 11, INK2, FONT, pad=(4, 0, 16, 16), background=False)))
    items[-1][5].body["visualContainerObjects"]["title"][0]["properties"]["alignment"] = s("right")

    # Menu panel: overlays the body from the menu button's side, hidden until opened
    pw, px = 420, W - M - 420
    panel = [("menu_panel", px, BODY_Y, pw, BODY_BOTTOM - BODY_Y, menu_background()),
             ("menu_title", px, BODY_Y, pw - 70, 56, textbox([("menu.title", 16, INK, FONT_SEMI)], pad=(16, 0, 20, 16))),
             ("menu_close", px + pw - 16 - 44, BODY_Y + 12, 44, 44,
              button("nav.menu-close", ("bookmark", f"bm_{name}_menu_closed"), "bookmark", size=16))]
    y = BODY_Y + 70
    for j, (vis, h) in enumerate(menu_items):
        panel.append((f"menu_item{j}", px + 4, y, pw - 8, h, vis))
        y += h + 10
    panel.append(("menu_note", px + 4, y, pw - 8, BODY_BOTTOM - y - 10,
                  textbox([(note_key, 12, INK2, FONT)], pad=(8, 8, 16, 16))))
    for item in panel:
        item[5].hidden = True
    return items, [item[0] for item in panel], panel


def menu_background():
    v = Visual("shape", objects={
        "shape": [{"properties": {"tileShape": s("rectangle")}}],
        "fill": [{"properties": {"show": b(True)}},
                 {"properties": {"fillColor": colour(CARD), "transparency": n(0)}, "selector": {"id": "default"}}],
        "outline": [{"properties": {"show": b(True)}},
                    {"properties": {"lineColor": colour(RULE), "weight": n(1)}, "selector": {"id": "default"}}],
    }, pad=(0, 0, 0, 0))
    v.body["visualContainerObjects"]["dropShadow"] = [{"properties": {"show": b(True), "position": s("Outer"),
                                                                        "preset": s("Custom"), "shadowBlur": n(12),
                                                                        "shadowDistance": n(2), "transparency": n(80)}}]
    return v


def kpi_panel(x, w, title_key, value_measure, status_measure, body=None, status_color=INK2, key_runs=None):
    """Title, value, then status line + optional trend or bars (visual-guidelines.md section 10.2)."""
    title_h, value_h = 40, 66
    rest = KPI_H - title_h - value_h
    items = [("title", x, BODY_Y, w, title_h, textbox([(title_key, 16, INK, FONT_SEMI)], pad=(8, 0, 16, 16))),
             ("value", x, BODY_Y + title_h, w, value_h, value_card(value_measure))]
    if body is None:
        body = measure_text(status_measure, 13, status_color, FONT, pad=(4, 0, 16, 16))
    items.append(("body", x, BODY_Y + title_h + value_h, w, rest, body))
    if key_runs:
        # Comparison legend sits on the title row, at the far end from the title
        items.append(("key", x + w * 0.62, BODY_Y + 2, w * 0.38 - 2, title_h - 4,
                      textbox(key_runs, "right", pad=(10, 0, 0, 16))))
    return items


def stage_bars(status_filter, measure="Total GW", detail="Share of Pipeline %", status_measure="KPI Pipeline Status",
               status_color=INK2):
    v = bars(col("Status", "Status"), [(measure, "field.gw")], fill_measure="Status Colour",
             detail_measure=detail, sort_by_category=True)
    v.body["visualContainerObjects"]["padding"] = [{"properties": {"top": n(4), "bottom": n(4), "left": n(16),
                                                                     "right": n(16)}}]
    v.measure_title(status_measure, 13, status_color)
    v.filters.append(in_filter("Status", status_filter, "true"))
    return v


def thirds():
    pw = (W - 2 * M - 2 * G) / 3
    return pw, [M, M + pw + G, M + 2 * (pw + G)]


# --- pages --------------------------------------------------------------------

def overview():
    pw, xs = thirds()
    share = trend(col("Generation", "Year"),
                  [("Wind Solar Share %", "label.region", INK, 3), ("World Wind Solar Share %", "label.world", GREY_LINE, 2)],
                  "Wind Solar Share Last Point", "KPI Share Status", ACCENT)
    share.filters.append(range_filter("Generation", "Year", 2015, 2023))
    added = trend(col("Unit", "Start Year"), [("Operating GW", "field.added", INK, 3)], "GW Added Last Point",
                  "KPI Operating Status", INK2)
    added.filters.append(range_filter("Unit", "Start Year", 2015, 2025))
    kpis = (kpi_panel(xs[0], pw, "kpi.share.title", "Wind Solar Share % Full Coverage", None, share,
                      key_runs=[("legend.region", 11, INK, FONT), ("legend.world", 11, GREY_LINE, FONT)])
            + kpi_panel(xs[1], pw, "kpi.operating.title", "Operating GW", None, added)
            + kpi_panel(xs[2], pw, "kpi.pipeline.title", "Pipeline GW", None, stage_bars("In Pipeline")))
    main = [("added_by_tech", M, MAIN_Y, W - 2 * M, BODY_BOTTOM - MAIN_Y, columns_by_technology())]
    menu = [(slicer(col("Overview Focus", "Focus"), "field.focus", single=True), 110),
            (slicer(col("Technology", "Technology Group"), "field.technology"), 170),
            (slicer(col("Country", "Country"), "field.country", mode="Dropdown"), 80)]
    return "Headline Overview", kpis, main, menu, "note.overview"


def breakdown():
    pw, xs = thirds()
    hydrogen = bars(col("Technology", "Technology Group"), [("Hydrogen Pipeline GW", "field.gw")],
                    fill_measure="Technology Colour", sort_measure="Hydrogen Pipeline GW")
    hydrogen.measure_title("KPI Hydrogen Status", 13, INK2)
    risk = stage_bars("Delivery Risk", measure="Dropped GW", detail=None, status_measure="KPI Risk Status")
    kpis = (kpi_panel(xs[0], pw, "kpi.pipeline.title", "Pipeline GW", None, stage_bars("In Pipeline"))
            + kpi_panel(xs[1], pw, "kpi.hydrogen.title", "Hydrogen Pipeline GW", None, hydrogen)
            + kpi_panel(xs[2], pw, "kpi.risk.title", "Dropped GW", None, risk))
    left_w = (W - 2 * M - G) * 0.58
    by_country = bars(col("Country", "Country"), [("Total GW", "field.gw")], "chart.country-status",
                      legend=("Status", "Status", {k: v for k, v in STATUS.items() if k not in ("Shelved", "Cancelled")}),
                      sort_measure="Total GW", legend_show=True)
    by_country.filters.append(in_filter("Status", "In Totals", "true"))
    by_tech = bars(col("Technology", "Technology Group"), [("Operating GW", "field.operating"), ("Pipeline GW", "field.pipeline")],
                   "chart.tech-operating-pipeline", visual_type="clusteredBarChart", legend_show=True,
                   sort_by_category=True)
    by_tech.body["objects"]["dataPoint"] = [
        {"properties": {"fill": colour(STATUS["Operating"])}, "selector": {"metadata": "_Measures.Operating GW"}},
        {"properties": {"fill": colour(STATUS["Announced"])}, "selector": {"metadata": "_Measures.Pipeline GW"}}]
    main = [("by_country", M, MAIN_Y, left_w, BODY_BOTTOM - MAIN_Y, by_country),
            ("by_technology", M + left_w + G, MAIN_Y, W - 2 * M - left_w - G, BODY_BOTTOM - MAIN_Y, by_tech)]
    menu = [(slicer(col("Technology", "Technology Group"), "field.technology"), 170),
            (slicer(col("Country", "Country"), "field.country", mode="Dropdown"), 80)]
    return "Headline Breakdown", kpis, main, menu, "note.breakdown"


def opportunity():
    pw, xs = thirds()
    intensity = trend(col("Generation", "Year"), [("Emissions Intensity g/kWh", "field.intensity", INK, 3)],
                      "Emissions Intensity Last Point", "KPI Intensity Status", INK2, label_precision="0L")
    intensity.filters.append(range_filter("Generation", "Year", 2015, 2023))
    builders = bars(col("Country", "Country"), [("Top 3 Construction GW", "field.gw")], fill_measure="Top Builder Colour",
                    detail_measure="Construction % of Total Label")
    builders.measure_title("KPI Construction Status", 13, INK2)
    announced = stage_bars("In Pipeline", status_measure="KPI Announced Status")
    kpis = (kpi_panel(xs[0], pw, "kpi.intensity.title", "Emissions Intensity Full Coverage", None, intensity)
            + kpi_panel(xs[1], pw, "kpi.construction.title", "Construction GW", None, builders)
            + kpi_panel(xs[2], pw, "kpi.announced.title", "Announced GW", None, announced))
    left_w = (W - 2 * M - G) * 0.5
    card = table([(col("Country", "Country"), "field.country"), (mea("Ember Year"), "field.year"),
                  (mea("Wind Solar Share %"), "field.share"), (mea("Emissions Intensity g/kWh"), "field.intensity"),
                  (mea("Operating GW"), "field.operating"), (mea("Construction GW"), "field.construction"),
                  (mea("Pipeline GW"), "field.pipeline")],
                 bar_measure="Construction GW", title_key="chart.scorecard")
    main = [("scatter", M, MAIN_Y, left_w, BODY_BOTTOM - MAIN_Y, scatter()),
            ("scorecard", M + left_w + G, MAIN_Y, W - 2 * M - left_w - G, BODY_BOTTOM - MAIN_Y, card)]
    menu = [(slicer(col("Technology", "Technology Group"), "field.technology"), 170),
            (slicer(col("Country", "Country"), "field.country", mode="Dropdown"), 80)]
    return "Headline Opportunity", kpis, main, menu, "note.opportunity"


def detail():
    top_h = 380
    left_w = (W - 2 * M - G) * 0.58
    top = bars(col("Plant", "Plant"), [("Top 10 Pipeline GW", "field.gw")], "chart.top-projects",
               legend=("Status", "Status", {k: STATUS[k] for k in ("Under construction", "Pre-construction", "Announced")}),
               detail_measure="Hydrogen Marker", sort_measure="Top 10 Pipeline GW", legend_show=True)
    owners = bars(col("Ownership", "Owner"), [("Top 10 Owner Operating GW", "field.gw")], "chart.top-owners",
                  fill_measure="Neutral Colour")
    owners.body["objects"]["dataPoint"] = [{"properties": {"fill": colour(STATUS["Operating"])}}]
    projects = table([(col("Plant", "Plant"), "field.plant"), (col("Unit", "Unit"), "field.unit"),
                      (col("Country", "Country"), "field.country"), (col("Technology", "Technology Group"), "field.technology"),
                      (col("Status", "Status"), "field.status"), (mea("Capacity MW"), "field.capacity-mw"),
                      (col("Unit", "Start Year"), "field.start-year"), (col("Unit", "Owner"), "field.owner"),
                      (mea("Hydrogen Marker"), "field.hydrogen")],
                     bar_measure="Capacity MW", title_key="chart.projects",
                     widths=[(mea("Capacity MW"), 110), (col("Unit", "Owner"), 330)],
                     filters=[in_filter("Status", "In Totals", "true")])
    main = [("top_projects", M, BODY_Y, left_w, top_h, top),
            ("top_owners", M + left_w + G, BODY_Y, W - 2 * M - left_w - G, top_h, owners),
            ("projects", M, BODY_Y + top_h + G, W - 2 * M, BODY_BOTTOM - BODY_Y - top_h - G, projects)]
    menu = [(slicer(col("Status", "Status"), "field.status"), 170),
            (slicer(col("Technology", "Technology Group"), "field.technology"), 170),
            (slicer(col("Country", "Country"), "field.country", mode="Dropdown"), 80)]
    return "Headline Detail", [], main, menu, "note.detail"


# --- writing ------------------------------------------------------------------

def write(path, obj):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(obj, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def visual_json(name, x, y, w, h, z, v):
    out = {"$schema": f"{SCHEMA}/visualContainer/2.13.0/schema.json", "name": name,
           "position": {"x": round(x, 2), "y": y, "z": z, "width": round(w, 2), "height": h, "tabOrder": z},
           "visual": v.body}
    if v.filters:
        out["filterConfig"] = {"filters": v.filters}
    if v.hidden:
        out["isHidden"] = True
    if v.i18n:
        out["annotations"] = [{"name": "i18n", "value": json.dumps(v.i18n, ensure_ascii=False)}]
    return out


def bookmark(page_name, state, visuals):
    name = f"bm_{page_name}_menu_{state}"
    return name, {
        "$schema": f"{SCHEMA}/bookmark/2.1.0/schema.json",
        "displayName": f"{page_name} menu {state}",
        "name": name,
        "options": {"targetVisualNames": visuals, "applyOnlyToTargetVisuals": True, "suppressData": True},
        "explorationState": {
            "version": "1.3",
            "activeSection": page_name,
            "sections": {page_name: {"visualContainers": {
                # Visible = no display override; hidden = display mode "hidden"
                v: {"singleVisual": {} if state == "open" else {"display": {"mode": "hidden"}}} for v in visuals}}},
        },
    }


def build_page(page, spec):
    headline, kpis, main, menu, note = spec
    name = f"en_{page}"
    frame, panel_names, panel = page_frame(page, headline, menu, note)
    folder = DEFINITION / "pages" / name
    write(folder / "page.json", {
        "$schema": f"{SCHEMA}/page/2.1.0/schema.json", "name": name, "displayName": TEXT[f"page.{page}"],
        "displayOption": "FitToPage", "width": W, "height": H,
        "objects": {"background": [{"properties": {"color": colour(CANVAS), "transparency": n(0)}}],
                    "outspace": [{"properties": {"color": colour(CANVAS)}}]},
        "filterConfig": {"filters": [dict(in_filter("Language", "Code", "'en'", name=f"lang_{name}"),
                                          isHiddenInViewMode=True, isLockedInViewMode=True)]},
        "annotations": [{"name": "i18n", "value": json.dumps({"name": f"page.{page}"})}],
    })
    # KPI items get stable names per panel: kpi<panel>_<part>
    named, panel_index = [], -1
    for part, x, y, w, h, v in kpis:
        if part == "title":
            panel_index += 1
        named.append((f"kpi{panel_index}_{part}", x, y, w, h, v))
    # The menu panel always sits on top of everything else (visual-guidelines.md section 3)
    for z, (nm, x, y, w, h, v) in enumerate(frame + named + main + panel):
        write(folder / "visuals" / nm / "visual.json",
              visual_json(nm, x, y, w, h, z + (10000 if nm.startswith("menu_") else 0), v))
    return [bookmark(name, "open", panel_names), bookmark(name, "closed", panel_names)]


def main():
    shutil.rmtree(DEFINITION / "pages", ignore_errors=True)
    shutil.rmtree(DEFINITION / "bookmarks", ignore_errors=True)
    write(REPORT / ".platform", {
        "$schema": "https://developer.microsoft.com/json-schemas/fabric/gitIntegration/platformProperties/2.0.0/schema.json",
        "metadata": {"type": "Report", "displayName": "Renewables"},
        "config": {"version": "2.0", "logicalId": str(uuid.uuid5(uuid.NAMESPACE_URL, "bilingual-power-bi-report/Renewables.Report"))},
    })
    write(REPORT / "definition.pbir", {
        "$schema": "https://developer.microsoft.com/json-schemas/fabric/item/report/definitionProperties/2.0.0/schema.json",
        "version": "4.0", "datasetReference": {"byPath": {"path": "../Renewables.SemanticModel"}}})
    write(DEFINITION / "version.json", {"$schema": f"{SCHEMA}/versionMetadata/1.0.0/schema.json", "version": "2.0.0"})
    write(DEFINITION / "report.json", {"$schema": f"{SCHEMA}/report/3.3.0/schema.json", "themeCollection": {}})
    specs = {"overview": overview(), "breakdown": breakdown(), "opportunity": opportunity(), "detail": detail()}
    marks = []
    for page in PAGES:
        marks += build_page(page, specs[page])
    for name, obj in marks:
        write(DEFINITION / "bookmarks" / f"{name}.bookmark.json", obj)
    write(DEFINITION / "bookmarks" / "bookmarks.json",
          {"$schema": f"{SCHEMA}/bookmarksMetadata/1.0.0/schema.json", "items": [{"name": nm} for nm, _ in marks]})
    write(DEFINITION / "pages" / "pages.json", {"$schema": f"{SCHEMA}/pagesMetadata/1.1.0/schema.json",
                                                "pageOrder": [f"en_{p}" for p in PAGES], "activePageName": "en_overview"})
    print(f"built {len(PAGES)} English pages and {len(marks)} bookmarks in {REPORT.name}")


if __name__ == "__main__":
    main()
