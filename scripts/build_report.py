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
HEADER_Y, HEADER_H = 20, 100
BODY_Y, BODY_BOTTOM = 140, 1000
FOOTER_Y, FOOTER_H = 1020, 40
# Text renders below its box top (title ~13 px) and above its box bottom (footer 11-17 px); measured on
# exported PNGs. The nudges put the ink, not the boxes, 20 px from the canvas edges.
HEADER_NUDGE, FOOTER_SOURCE_NUDGE, FOOTER_STATUS_NUDGE = 13, 11, 17
TOOLTIP_W = 320
KPI_H = 260
BAR_GAP = 50  # gap between bars, % of the category width
MAIN_Y = BODY_Y + KPI_H + G

# Colours and fonts (sections 6-7)
CANVAS, CARD, RULE, INK, INK2 = "#f4f4f2", "#ffffff", "#e4e3df", "#1d1d1b", "#5c5b57"
ACCENT, GREY_LINE, NEUTRAL = "#eb6834", "#b3b2ac", "#d3d2cc"
# Operating is delivered, so recessive (purple-grey); the pipeline stages carry the focus
STATUS = {"Operating": "#c9c6d6", "Under construction": "#4a3fb0", "Pre-construction": "#7368d9",
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


def value_card(measure, size=36):
    # A shape title holds the number, so it aligns and mirrors like the other text
    return measure_text(f"{measure} Text", size, INK, FONT_SEMI, pad=(0, 0, 16, 16))


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


def trend(category, series, last_point, status_measure, status_color, label_precision="1L", axis_max=None):
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
                         # axis_max: headroom so a label on the highest point is not clipped
                         "valueAxis": axis(show=False, **({"end": {"expr": mea(axis_max)}} if axis_max else {}))}
    v.measure_title(status_measure, 13, status_color)
    return v


def series_colours(entity, prop, colours):
    """Fixed colour per series value (legend), e.g. status or technology."""
    return [{"properties": {"fill": colour(c)},
             "selector": {"data": [{"scopeId": {"Comparison": {"ComparisonKind": 0, "Left": col(entity, prop),
                                                               "Right": {"Literal": {"Value": f"'{value}'"}}}}}]}}
            for value, c in colours.items()]


def bars(category, values, title_key=None, visual_type="barChart", legend=None, fill_measure=None,
         detail_measure=None, sort_by_category=False, sort_measure=None, legend_show=False, size=12, axis_max=None,
         axis_min=None):
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
        "categoryAxis": axis(size=size, maxMarginFactor=n(40), innerPadding=lit(f"{BAR_GAP}L")),
        # axis_max: a measure giving headroom so labels stay outside the longest bar
        "valueAxis": axis(show=False, **({"end": {"expr": mea(axis_max)}} if axis_max else {}),
                          **({"start": {"expr": mea(axis_min)}} if axis_min else {})),
        "legend": [{"properties": {"show": b(legend_show), "position": s("Top"), "fontSize": n(11),
                                   "fontFamily": s(FONT), "labelColor": colour(INK2), "showTitle": b(False)}}],
    }
    return v


def online_by_year():
    """Came online (by start year) and under construction (by expected year), stacked; status colours.
    An invisible line on the same axis labels only the latest full year and the expected years."""
    v = Visual("lineStackedColumnComboChart", pad=(4, 8, 16, 16))
    built, building = mea("Operating GW"), mea("Construction GW")
    v.body["query"] = {"queryState": {
        "Category": {"projections": [projection(v, col("Unit", "Start Year"))]},
        "Y": {"projections": [projection(v, built, "field.added"), projection(v, building, "field.construction")]},
        "Y2": {"projections": [projection(v, mea("Online Label GW"), "field.gw")]}},
        "sortDefinition": {"sort": [{"field": col("Unit", "Start Year"), "direction": "Ascending"}], "isDefaultSort": True}}
    v.body["objects"] = {
        "dataPoint": [{"properties": {"fill": colour(STATUS["Operating"])}, "selector": {"metadata": ref(built)}},
                      {"properties": {"fill": colour(STATUS["Under construction"])}, "selector": {"metadata": ref(building)}}],
        "lineStyles": [{"properties": {"strokeWidth": n(0), "showMarker": b(False)}}],
        "labels": [{"properties": {"show": b(True), "color": colour(INK), "fontSize": n(12), "fontFamily": s(FONT_SEMI),
                                   "labelPrecision": lit("1L"), "labelPosition": s("Above")}},
                   {"properties": {"showSeries": b(False)}, "selector": {"metadata": ref(built)}},
                   {"properties": {"showSeries": b(False)}, "selector": {"metadata": ref(building)}}],
        "categoryAxis": axis(size=12, color=INK2, axisType=s("Categorical"), innerPadding=lit(f"{BAR_GAP}L")),
        # One value axis (the line shares it); recessive solid hairlines carry the unlabelled years
        "valueAxis": axis(size=11, color=INK2, gridlineShow=b(True), gridlineColor=colour(RULE),
                          gridlineStyle=s("solid"), secShow=b(False)),
        "legend": [{"properties": {"show": b(False)}}],
    }
    v.filters.append(range_filter("Unit", "Start Year", 2015, 2029))
    return report_tooltip(v, "tt_tech")


def online_panel(x, y, w, h):
    """Title, legend + coverage note row, then the chart, stacked on one white card."""
    title_h, row_h = 40, 32
    legend = textbox([("legend.swatch", 12, STATUS["Operating"], FONT), ("legend.came-online", 12, INK2, FONT),
                      ("legend.swatch", 12, STATUS["Under construction"], FONT), ("legend.expected", 12, INK2, FONT)],
                     pad=(4, 0, 16, 16))
    note = measure_text("Note Expected Coverage", 12, INK2, FONT, pad=(4, 0, 16, 16))
    note.body["visualContainerObjects"]["title"][0]["properties"]["alignment"] = s("right")
    return [("online_title", x, y, w, title_h, textbox([("chart.online-by-year", 16, INK, FONT_SEMI)], pad=(8, 0, 16, 16))),
            ("online_legend", x, y + title_h, w * 0.4, row_h, legend),
            ("online_note", x + w * 0.4, y + title_h, w * 0.6, row_h, note),
            ("online_chart", x, y + title_h + row_h, w, h - title_h - row_h, online_by_year())]


TEXT_MEASURES = {"Ember Year", "Hydrogen Marker", "Status Dot"}


def table(columns, bar_measure=None, title_key=None, filters=None, dot_measure=None):
    """columns: (field, display key, width px). Widths fill the visual, so the mirrored grid leaves no gap.
    Text and descriptive numbers (years) align left, values right."""
    v = Visual("tableEx", title_key=title_key)
    v.body["query"] = {"queryState": {"Values": {"projections": [projection(v, f, key) for f, key, _ in columns]}},
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
        # styleHeader: the header aligns with its column
        "columnFormatting": [{"properties": {"alignment": s("Right" if is_value(f) else "Left"), "styleHeader": b(True)},
                              "selector": {"metadata": ref(f)}} for f, _, _ in columns],
        "columnWidth": [{"properties": {"value": n(w)}, "selector": {"metadata": ref(f)}} for f, _, w in columns],
    }
    if bar_measure:
        v.body["objects"]["columnFormatting"].append({
            "properties": {"dataBars": {"positiveColor": colour(NEUTRAL), "negativeColor": colour(ACCENT),
                                        "axisColor": colour(RULE), "reverseDirection": b(False), "hideText": b(False)}},
            "selector": {"metadata": f"_Measures.{bar_measure}"}})
    if dot_measure:
        # The status dot takes the status colour, linking the table to the status charts
        v.body["objects"]["values"].append({
            "properties": {"fontColor": {"solid": {"color": {"expr": mea("Status Colour")}}}},
            "selector": {"data": [{"dataViewWildcard": {"matchingOption": 1}}], "metadata": f"_Measures.{dot_measure}"}})
    v.filters += filters or []
    return v


def report_tooltip(v, page):
    """Hover shows a tooltip page (value first, label after) instead of the default list."""
    v.body["visualContainerObjects"]["visualTooltip"] = [{"properties": {
        "show": b(True), "type": s("ReportPage"), "section": s(f"en_{page}")}}]
    return v


def is_value(field):
    return "Measure" in field and field["Measure"]["Property"] not in TEXT_MEASURES


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
        "fill": [{"properties": {"show": b(False)}}],
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
    top = HEADER_Y - HEADER_NUDGE
    title_w = 300
    items.append(("page_title", M, top, title_w, 40,
                  textbox([(f"page.{page}", 20, INK, FONT_SEMI)], pad=(4, 0, 0, 0), background=False)))
    # Active slicer filters, on the title row (blank when nothing is filtered)
    items.append(("filter_state", M + title_w, top + 6, head_w - title_w, 34,
                  measure_text("Filter State Text", 13, INK2, FONT, pad=(4, 0, 0, 0), background=False)))
    items.append(("headline", M, top + 40, head_w, HEADER_H - 30,
                  measure_text(headline_measure, 18, INK2, FONT, pad=(4, 0, 0, 0), background=False)))
    if i > 0:
        items.append(("nav_back", x_back, top + 22, btn, btn,
                      button("nav.back", ("page", f"en_{PAGES[i - 1]}"), "nav")))
    if i < len(PAGES) - 1:
        items.append(("nav_next", x_next, top + 22, btn, btn,
                      button("nav.next", ("page", f"en_{PAGES[i + 1]}"), "nav")))
    items.append(("nav_language", x_lang, top + 22, 100, btn,
                  button("nav.language", ("page", f"ar_{page}"), "language", size=16)))
    items.append(("menu_open", x_menu, top + 22, btn, btn,
                  button("nav.menu-open", ("bookmark", f"bm_{name}_menu_open"), "bookmark")))

    items.append(("footer_source", M, FOOTER_Y + FOOTER_SOURCE_NUDGE, 1100, FOOTER_H,
                  textbox([("footer.source", 11, INK2, FONT)], pad=(10, 0, 0, 0), background=False)))
    items.append(("footer_status", M + 1100 + G, FOOTER_Y + FOOTER_STATUS_NUDGE, W - 2 * M - 1100 - G, FOOTER_H,
                  measure_text("Footer Status", 11, INK2, FONT, pad=(4, 0, 0, 0), background=False)))
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


def kpi_panel(x, w, title_key, value_measure, status_measure, body=None, status_color=INK2, key_runs=None, key=False):
    """Title, value, then status line + optional trend or bars (visual-guidelines.md section 10.2).
    key: the page's lead number, larger than the others (one per page)."""
    title_h, value_h = 40, 66
    rest = KPI_H - title_h - value_h
    items = [("title", x, BODY_Y, w, title_h, textbox([(title_key, 16, INK, FONT_SEMI)], pad=(8, 0, 16, 16))),
             ("value", x, BODY_Y + title_h, w, value_h, value_card(value_measure, 44 if key else 30))]
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
             detail_measure=detail, sort_by_category=True, axis_max=f"{measure} Bar Max")
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
    # Cumulative, so the line shows the same thing as the number above it
    added = trend(col("Unit", "Start Year"), [("Operating GW Cumulative", "field.operating", INK, 3)],
                  "Operating Cumulative Last Point", "KPI Operating Status", INK2,
                  axis_max="Operating GW Cumulative Axis Max")
    added.filters.append(range_filter("Unit", "Start Year", 2015, 2025))
    kpis = (kpi_panel(xs[0], pw, "kpi.share.title", "Wind Solar Share % Full Coverage", None, share,
                      key_runs=[("legend.region", 11, INK, FONT), ("legend.world", 11, GREY_LINE, FONT)], key=True)
            + kpi_panel(xs[1], pw, "kpi.operating.title", "Operating GW", None, added)
            + kpi_panel(xs[2], pw, "kpi.pipeline.title", "Pipeline GW", None, stage_bars("In Pipeline")))
    main = online_panel(M, MAIN_Y, W - 2 * M, BODY_BOTTOM - MAIN_Y)
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
    kpis = (kpi_panel(xs[0], pw, "kpi.pipeline.title", "Pipeline GW", None, stage_bars("In Pipeline"), key=True)
            + kpi_panel(xs[1], pw, "kpi.hydrogen.title", "Hydrogen Pipeline GW", None, hydrogen)
            + kpi_panel(xs[2], pw, "kpi.risk.title", "Dropped GW", None, risk))
    left_w = (W - 2 * M - G) * 0.58
    by_country = bars(col("Country", "Country"), [("Total GW", "field.gw")], "chart.country-status",
                      legend=("Status", "Status", {k: v for k, v in STATUS.items() if k not in ("Shelved", "Cancelled")}),
                      sort_measure="Total GW", legend_show=True)
    by_country.filters.append(in_filter("Status", "In Totals", "true"))
    report_tooltip(by_country, "tt_tech")
    # How dependent each country's pipeline is on green hydrogen: tied (dark grey) and the rest (neutral)
    tied, rest = mea("Hydrogen Pipeline GW"), mea("Non-hydrogen Pipeline GW")
    by_hydrogen = bars(col("Country", "Country"), [("Hydrogen Pipeline GW", "field.hydrogen-gw"),
                                                   ("Non-hydrogen Pipeline GW", "field.other-pipeline")],
                       "chart.hydrogen-by-country", detail_measure="Hydrogen % of Pipeline Label",
                       sort_measure="Hydrogen Pipeline GW", legend_show=True)
    by_hydrogen.body["objects"]["dataPoint"] = [
        {"properties": {"fill": colour(INK2)}, "selector": {"metadata": ref(tied)}},
        {"properties": {"fill": colour(NEUTRAL)}, "selector": {"metadata": ref(rest)}},
    ]
    # Label the tied segment only, in white inside the dark fill; the rest of the pipeline stays in the tooltip
    by_hydrogen.body["objects"]["labels"] += [
        {"properties": {"color": colour(CARD), "detailColor": colour(CARD)}, "selector": {"metadata": ref(tied)}},
        {"properties": {"showSeries": b(False)}, "selector": {"metadata": ref(rest)}},
    ]
    main = [("by_country", M, MAIN_Y, left_w, BODY_BOTTOM - MAIN_Y, by_country),
            ("by_hydrogen", M + left_w + G, MAIN_Y, W - 2 * M - left_w - G, BODY_BOTTOM - MAIN_Y, by_hydrogen)]
    menu = [(slicer(col("Technology", "Technology Group"), "field.technology"), 170),
            (slicer(col("Country", "Country"), "field.country", mode="Dropdown"), 80)]
    return "Headline Breakdown", kpis, main, menu, "note.breakdown"


def opportunity():
    pw, xs = thirds()
    intensity = trend(col("Generation", "Year"), [("Emissions Intensity g/kWh", "field.intensity", INK, 3)],
                      "Emissions Intensity Last Point", "KPI Intensity Status", INK2, label_precision="0L")
    intensity.filters.append(range_filter("Generation", "Year", 2015, 2023))
    builders = bars(col("Country", "Country"), [("Top 3 Construction GW", "field.gw")], fill_measure="Top Builder Colour",
                    detail_measure="Construction % of Total Label", axis_max="Top 3 Construction GW Bar Max")
    builders.measure_title("KPI Construction Status", 13, INK2)
    announced = stage_bars("In Pipeline", status_measure="KPI Announced Status")
    kpis = (kpi_panel(xs[0], pw, "kpi.intensity.title", "Emissions Intensity Full Coverage", None, intensity)
            + kpi_panel(xs[1], pw, "kpi.construction.title", "Construction GW", None, builders, key=True)
            + kpi_panel(xs[2], pw, "kpi.announced.title", "Announced GW", None, announced))
    left_w = (W - 2 * M - G) * 0.5
    # Widths sum to the inner width (930 - 2 x 16 padding) less 18 px for the scroll bar
    card = table([(col("Country", "Country"), "field.country", 150), (mea("Ember Year"), "field.year", 90),
                  (mea("Scorecard Share %"), "field.share", 120),
                  (mea("Emissions Intensity g/kWh"), "field.intensity", 90),
                  (mea("Operating GW"), "field.operating", 120), (mea("Construction GW"), "field.construction", 180),
                  (mea("Scorecard Pipeline GW"), "field.pipeline", 130)],
                 bar_measure="Construction GW", title_key="chart.scorecard")
    # Gap to the world share: bars either side of zero (= the world); the top builder in the accent
    gap = bars(col("Country", "Country"), [("Share Gap to World pts", "field.gap")], "chart.gap-to-world",
               fill_measure="Top Builder Colour", axis_max="Share Gap Axis Max", axis_min="Share Gap Axis Min")
    report_tooltip(gap, "tt_gap")
    main = [("gap_to_world", M, MAIN_Y, left_w, BODY_BOTTOM - MAIN_Y, gap),
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
    # Widths sum to the inner width (1880 - 2 x 16 padding) less 18 px for the scroll bar
    projects = table([(col("Plant", "Plant"), "field.plant", 440), (col("Country", "Country"), "field.country", 150),
                      (col("Technology", "Technology Group"), "field.technology", 130),
                      (mea("Status Dot"), "field.status-dot", 24), (col("Status", "Status"), "field.status", 170), (mea("Capacity MW"), "field.capacity-mw", 140),
                      (col("Unit", "Start Year"), "field.start-year", 110), (col("Unit", "Owner"), "field.owner", 566),
                      (mea("Hydrogen Marker"), "field.hydrogen", 100)],
                     bar_measure="Capacity MW", title_key="chart.projects", dot_measure="Status Dot",
                     filters=[in_filter("Status", "In Totals", "true")])
    main = [("top_projects", M, BODY_Y, left_w, top_h, top),
            ("top_owners", M + left_w + G, BODY_Y, W - 2 * M - left_w - G, top_h, owners),
            ("projects", M, BODY_Y + top_h + G, W - 2 * M, BODY_BOTTOM - BODY_Y - top_h - G, projects)]
    menu = [(slicer(col("Status", "Status"), "field.status"), 170),
            (slicer(col("Technology", "Technology Group"), "field.technology"), 170),
            (slicer(col("Country", "Country"), "field.country", mode="Dropdown"), 80)]
    return "Headline Detail", [], main, menu, "note.detail"


# --- tooltip pages ------------------------------------------------------------

def tooltip_tech():
    """Value first (GW), then what was hovered, then the technology split."""
    chart = bars(col("Technology", "Technology Group"), [("Tooltip GW", "field.gw")], fill_measure="Technology Colour",
                 sort_by_category=True, axis_max="Tooltip GW Bar Max")
    chart.title("tooltip.by-technology", 12, INK2, FONT)
    chart.body["visualContainerObjects"]["padding"] = [{"properties": {"top": n(0), "bottom": n(4), "left": n(12),
                                                                         "right": n(12)}}]
    return 200, [("value", 0, 0, TOOLTIP_W, 46, measure_text("Tooltip GW Text", 24, INK, FONT_SEMI, pad=(8, 0, 12, 12))),
                 ("context", 0, 46, TOOLTIP_W, 28, measure_text("Tooltip Context Text", 12, INK2, FONT, pad=(0, 0, 12, 12))),
                 ("by_technology", 0, 74, TOOLTIP_W, 126, chart)]


def tooltip_gap():
    """Value first (the country's share), then country and year, then the world and the gap."""
    return 110, [("value", 0, 0, TOOLTIP_W, 46, measure_text("Tooltip Share Text", 24, INK, FONT_SEMI, pad=(8, 0, 12, 12))),
                 ("context", 0, 46, TOOLTIP_W, 28, measure_text("Tooltip Gap Context Text", 12, INK2, FONT, pad=(0, 0, 12, 12))),
                 ("world", 0, 74, TOOLTIP_W, 32, measure_text("Tooltip Gap Text", 12, INK, FONT, pad=(0, 0, 12, 12)))]


TOOLTIPS = {"tt_tech": tooltip_tech, "tt_gap": tooltip_gap}


def build_tooltip(page, spec):
    height, items = spec()
    name = f"en_{page}"
    folder = DEFINITION / "pages" / name
    write(folder / "page.json", {
        "$schema": f"{SCHEMA}/page/2.1.0/schema.json", "name": name, "displayName": TEXT[f"page.{page.replace('_', '-')}"],
        "displayOption": "ActualSize", "width": TOOLTIP_W, "height": height, "type": "Tooltip",
        "visibility": "HiddenInViewMode",
        "objects": {"background": [{"properties": {"color": colour(CARD), "transparency": n(0)}}]},
        "filterConfig": {"filters": [dict(in_filter("Language", "Code", "'en'", name=f"lang_{name}"),
                                          isHiddenInViewMode=True, isLockedInViewMode=True)]},
        "annotations": [{"name": "i18n", "value": json.dumps({"name": f"page.{page.replace('_', '-')}"})}],
    })
    for z, (nm, x, y, w, h, v) in enumerate(items):
        v.body["visualContainerObjects"]["background"] = [{"properties": {"show": b(False)}}]
        write(folder / "visuals" / nm / "visual.json", visual_json(nm, x, y, w, h, z, v))


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
    for page, spec in TOOLTIPS.items():
        build_tooltip(page, spec)
    for name, obj in marks:
        write(DEFINITION / "bookmarks" / f"{name}.bookmark.json", obj)
    write(DEFINITION / "bookmarks" / "bookmarks.json",
          {"$schema": f"{SCHEMA}/bookmarksMetadata/1.0.0/schema.json", "items": [{"name": nm} for nm, _ in marks]})
    write(DEFINITION / "pages" / "pages.json", {"$schema": f"{SCHEMA}/pagesMetadata/1.1.0/schema.json",
                                                "pageOrder": [f"en_{p}" for p in PAGES + list(TOOLTIPS)],
                                                "activePageName": "en_overview"})
    print(f"built {len(PAGES)} English pages and {len(marks)} bookmarks in {REPORT.name}")


if __name__ == "__main__":
    main()
