"""Build the English pages of Renewables.Report (PBIR) from the page specs below.

Usage:
    python scripts/build_report.py

Every piece of static text is written in English and its translation key is
stored in the visual's "i18n" annotation, so scripts/mirror_pages.py can turn
each English page into its mirrored Arabic twin. Layout and styling follow
docs/visual-guidelines.md.
"""
import csv
import hashlib
import json
import shutil
import uuid
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
REPORT = ROOT / "Renewables.Report"
DEFINITION = REPORT / "definition"
SCHEMA = "https://developer.microsoft.com/json-schemas/fabric/item/report/definition"

# Canvas and spacing: fabric-kit Report layout A (visual-guidelines.md sections 1-2)
W, H, G = 1280, 720, 8
TOP_H, RAIL_W, PANE_W, FOOTER_H = 40, 40, 232, 24
BODY_X, BODY_Y = RAIL_W + G, TOP_H + G
BODY_W = W - BODY_X - G
FOOTER_Y = H - FOOTER_H
BODY_BOTTOM = FOOTER_Y - G
HEADLINE_H = 34
STRIP_Y = BODY_Y + HEADLINE_H + 4
KPI_H = 92
MAIN_Y = STRIP_Y + KPI_H + G
TOOLTIP_W = 320
BAR_GAP = 50  # gap between bars, % of the category width

# Colours and fonts (sections 6-7): Fern & Stone Tidepool (light), registered as the report theme
CANVAS, PANEL, CHROME, BORDER, RULE = "#f8faf8", "#fcfdfc", "#ffffff", "#d6ded8", "#e4eae5"
INK, INK2 = "#111a15", "#46534b"
# One highlight per visual in fern green; the rest light grey, so the highlight also differs in lightness
ACCENT, NEUTRAL, BAD = "#1d6a44", "#c2ccc5", "#9c5520"
# Axis line: 1 px, lighter than the axis text (INK2); the theme's grey-green
AXIS_LINE = "#7a877f"
# Kit series colours in stage order; status and technology share hues, so their charts always carry a legend
STATUS = {"Operating": "#28a19c", "Under construction": "#b6801f", "Pre-construction": "#5a71cd",
          "Announced": "#b25e6a", "Shelved": "#7a877f", "Cancelled": "#7a877f"}
THEME = "FernStoneTidepoolLight"
FONT = "'Segoe UI', wf_segoe-ui_normal, helvetica, arial, sans-serif"
FONT_SEMI = "'Segoe UI Semibold', wf_segoe-ui_semibold, helvetica, arial, sans-serif"

PAGES = ["overview", "breakdown", "opportunity", "detail"]
# Right-click a country on any page to see its projects
DRILLTHROUGH = {"detail": ("Country", "Country")}

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

    def __init__(self, visual_type, query=None, objects=None, title_key=None, pad=(8, 8, 8, 8)):
        self.i18n = {}
        self.body = {"visualType": visual_type}
        if query:
            self.body["query"] = query
        self.body["objects"] = objects or {}
        self.body["visualContainerObjects"] = container(pad)
        if title_key:
            self.title(title_key)
            self.alt(title_key)
        self.filters = []
        self.hidden = False

    def title(self, key, size=12, color=INK, font=FONT_SEMI):
        self.i18n["title"] = key
        self.body["visualContainerObjects"]["title"] = [{"properties": {
            "show": b(True), "text": s(TEXT[key]), "fontFamily": s(font), "fontSize": n(size),
            "fontColor": colour(color), "alignment": s("left"), "titleWrap": b(True)}}]
        return self

    def alt(self, key):
        """Alt text for screen readers (report-design.md: every visual)."""
        self.i18n["alt"] = key
        self.body["visualContainerObjects"]["general"] = [{"properties": {"altText": s(TEXT[key])}}]
        return self

    def plain(self):
        """No panel: the visual sits on the canvas or on a panel drawn behind it."""
        self.body["visualContainerObjects"]["background"] = [{"properties": {"show": b(False)}}]
        self.body["visualContainerObjects"]["border"] = [{"properties": {"show": b(False)}}]
        return self

    def measure_title(self, measure, size=13, color=INK2, font=FONT):
        self.body["visualContainerObjects"]["title"] = [{"properties": {
            "show": b(True), "text": {"expr": mea(measure)}, "fontFamily": s(font), "fontSize": n(size),
            "fontColor": colour(color), "alignment": s("left"), "titleWrap": b(True)}}]
        return self


def container(pad):
    """A thin panel: a lighter tint of the page with a hairline border (fabric-kit compact app mode)."""
    return {
        "title": [{"properties": {"show": b(False)}}],
        "background": [{"properties": {"show": b(True), "color": colour(PANEL), "transparency": n(0)}}],
        "border": [{"properties": {"show": b(True), "color": colour(BORDER), "radius": n(6), "width": n(1)}}],
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

def textbox(runs, align=None, pad=(8, 8, 8, 8), background=True):
    """runs: (translation key, size pt, colour, font)."""
    v = Visual("textbox", pad=pad)
    v.i18n["runs"] = [key for key, *_ in runs]
    para = {"textRuns": [{"value": TEXT[key], "textStyle": {"fontFamily": font, "fontSize": f"{size}pt", "color": c}}
                         for key, size, c, font in runs]}
    if align:
        para["horizontalTextAlignment"] = align
    v.body["objects"] = {"general": [{"properties": {"paragraphs": [para]}}]}
    if not background:
        v.plain()
    return v


def measure_text(measure, size, color=INK, font=FONT, pad=(0, 0, 8, 8), background=True):
    """A text measure shown as the title of an empty shape: wraps, aligns, and mirrors."""
    v = Visual("shape", objects={
        "shape": [{"properties": {"tileShape": s("rectangle")}}],
        "fill": [{"properties": {"show": b(False)}}],
        "outline": [{"properties": {"show": b(False)}}],
    }, pad=pad)
    v.measure_title(measure, size, color, font)
    if not background:
        v.plain()
    return v


def value_card(measure, size=36):
    # A shape title holds the number, so it aligns and mirrors like the other text
    return measure_text(f"{measure} Text", size, INK, FONT_SEMI, pad=(0, 0, 8, 8), background=False)


def block(fill=None):
    """An empty rectangle: a panel behind grouped visuals (no fill given), or a solid fill for the
    top bar, rail and footer (white) and their hairlines."""
    v = Visual("shape", objects={
        "shape": [{"properties": {"tileShape": s("rectangle")}}],
        "fill": [{"properties": {"show": b(False)}}],
        "outline": [{"properties": {"show": b(False)}}],
    }, pad=(0, 0, 0, 0))
    if fill:
        v.plain()
        v.body["objects"]["fill"] = [{"properties": {"show": b(True)}},
                                     {"properties": {"fillColor": colour(fill), "transparency": n(0)},
                                      "selector": {"id": "default"}}]
    return v


def value_card_multirow(measure):
    v = Visual("multiRowCard", pad=(0, 0, 16, 16))
    v.body["query"] = {"queryState": {"Values": {"projections": [projection(v, mea(measure))]}}}
    v.body["objects"] = {
        "dataLabels": [{"properties": {"color": colour(INK), "fontSize": n(36), "fontFamily": s(FONT_SEMI)}}],
        "categoryLabels": [{"properties": {"show": b(False)}}],
        "card": [{"properties": {"barShow": b(False), "outlineStyle": lit("0D")}}],
    }
    return v


def axis(show=True, size=9, color=INK2, **extra):
    props = {"show": b(show), "fontFamily": s(FONT), "fontSize": n(size), "labelColor": colour(color),
             "showAxisTitle": b(False), "gridlineShow": b(False)}
    props.update(extra)
    return [{"properties": props}]


def baseline():
    """The axis line: Power BI charts have no axis-line setting, so a 1 px constant line at 0 on the value axis
    draws the baseline the bars grow from (and the zero line of diverging bars)."""
    return [{"properties": {"show": b(True), "value": n(0), "lineColor": colour(AXIS_LINE), "width": n(1),
                            "transparency": n(0), "style": s("solid"), "position": s("front"),
                            "dataLabelShow": b(False)}, "selector": {"id": "1"}}]


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


def series_colours(entity, prop, colours):
    """Fixed colour per series value (legend), e.g. status or technology."""
    return [{"properties": {"fill": colour(c)},
             "selector": {"data": [{"scopeId": {"Comparison": {"ComparisonKind": 0, "Left": col(entity, prop),
                                                               "Right": {"Literal": {"Value": f"'{value}'"}}}}}]}}
            for value, c in colours.items()]


def bars(category, values, title_key=None, visual_type="barChart", legend=None, fill_measure=None,
         detail_measure=None, sort_by_category=False, sort_measure=None, legend_show=False, size=9, axis_max=None,
         axis_min=None, value_axis=False, show_labels=True):
    """values: (measure, display key). legend: (entity, prop, colours) for stacked series.
    Every bar carries a label; where stacked segments are too small for labels, value_axis shows a labelled
    axis instead (show_labels=False)."""
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
    labels = [{"properties": {"show": b(show_labels), "color": colour(INK), "fontSize": n(size), "fontFamily": s(FONT),
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
        "valueAxis": axis(show=value_axis, size=size, labelDisplayUnits=n(1), labelPrecision=lit("0L"),
                          **({"end": {"expr": mea(axis_max)}} if axis_max else {}),
                          **({"start": {"expr": mea(axis_min)}} if axis_min else {})),
        "y1AxisReferenceLine": baseline(),
        "legend": [{"properties": {"show": b(legend_show), "position": s("Top"), "fontSize": n(9),
                                   "fontFamily": s(FONT), "labelColor": colour(INK2), "showTitle": b(False)}}],
    }
    return v


def online_by_year():
    """Came online (by start year) and under construction (by expected year), stacked; status colours.
    An invisible line on the same axis labels only the latest full year and the expected years."""
    v = Visual("lineStackedColumnComboChart", pad=(0, 4, 8, 8))
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
        "labels": [{"properties": {"show": b(True), "color": colour(INK), "fontSize": n(9), "fontFamily": s(FONT_SEMI),
                                   "labelPrecision": lit("1L"), "labelPosition": s("Above")}},
                   {"properties": {"showSeries": b(False)}, "selector": {"metadata": ref(built)}},
                   {"properties": {"showSeries": b(False)}, "selector": {"metadata": ref(building)}}],
        "categoryAxis": axis(axisType=s("Categorical"), innerPadding=lit(f"{BAR_GAP}L")),
        # One value axis (the line shares it); recessive solid hairlines carry the unlabelled years
        "valueAxis": axis(gridlineShow=b(True), gridlineColor=colour(RULE),
                          gridlineStyle=s("solid"), secShow=b(False)),
        "y1AxisReferenceLine": baseline(),
        "legend": [{"properties": {"show": b(False)}}],
    }
    v.filters.append(range_filter("Unit", "Start Year", 2015, 2029))
    return report_tooltip(v, "tt_tech")


def online_panel(x, y, w, h):
    """Title, legend + coverage note row, then the chart, stacked on one panel."""
    title_h, row_h = 28, 22
    legend = textbox([("legend.swatch", 9, STATUS["Operating"], FONT), ("legend.came-online", 9, INK2, FONT),
                      ("legend.swatch", 9, STATUS["Under construction"], FONT), ("legend.expected", 9, INK2, FONT)],
                     pad=(2, 0, 8, 8), background=False)
    note = measure_text("Note Expected Coverage", 9, INK2, FONT, pad=(2, 0, 8, 8), background=False)
    note.body["visualContainerObjects"]["title"][0]["properties"]["alignment"] = s("right")
    chart = online_by_year().plain().alt("chart.online-by-year")
    return [("online_panel", x, y, w, h, block()),
            ("online_title", x, y, w, title_h,
             textbox([("chart.online-by-year", 12, INK, FONT_SEMI)], pad=(6, 0, 8, 8), background=False)),
            ("online_legend", x, y + title_h, w * 0.4, row_h, legend),
            ("online_note", x + w * 0.4, y + title_h, w * 0.6, row_h, note),
            ("online_chart", x, y + title_h + row_h, w, h - title_h - row_h, chart)]


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
        "columnHeaders": [{"properties": {"fontFamily": s(FONT_SEMI), "fontSize": n(9), "fontColor": colour(INK2),
                                          "backColor": colour(PANEL), "wordWrap": b(True)}}],
        "values": [{"properties": {"fontFamily": s(FONT), "fontSize": n(10), "fontColorPrimary": colour(INK),
                                   "backColorPrimary": colour(PANEL), "fontColorSecondary": colour(INK),
                                   "backColorSecondary": colour(PANEL)}}],
        "grid": [{"properties": {"gridHorizontal": b(True), "gridHorizontalColor": colour(RULE), "gridVertical": b(False),
                                 "outlineColor": colour(BORDER), "rowPadding": n(3)}}],
        "total": [{"properties": {"totals": b(False)}}],
        # styleHeader: the header aligns with its column
        "columnFormatting": [{"properties": {"alignment": s("Right" if is_value(f) else "Left"), "styleHeader": b(True)},
                              "selector": {"metadata": ref(f)}} for f, _, _ in columns],
        "columnWidth": [{"properties": {"value": n(w)}, "selector": {"metadata": ref(f)}} for f, _, w in columns],
    }
    if bar_measure:
        v.body["objects"]["columnFormatting"].append({
            "properties": {"dataBars": {"positiveColor": colour(NEUTRAL), "negativeColor": colour(BAD),
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


def slicer(field, display_key, single=False):
    """Dropdown slicer in the filter pane (fabric-kit Report layout A)."""
    v = Visual("slicer", pad=(4, 4, 8, 8))
    v.body["query"] = {"queryState": {"Values": {"projections": [projection(v, field, display_key)]}}}
    v.body["objects"] = {
        "data": [{"properties": {"mode": s("Dropdown")}}],
        "selection": [{"properties": {"singleSelect": b(single), "selectAllCheckboxEnabled": b(not single)}}],
        "header": [{"properties": {"show": b(True), "fontColor": colour(INK2), "fontFamily": s(FONT_SEMI),
                                   "textSize": n(10)}}],
        "items": [{"properties": {"fontColor": colour(INK), "fontFamily": s(FONT), "textSize": n(10)}}],
    }
    return v.plain().alt(display_key)


def button(text_key, action, role, alt_key, size=12):
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
                    {"properties": {"lineColor": colour(BORDER), "weight": n(1), "roundEdge": n(4)},
                     "selector": {"id": "default"}}],
    }
    link = {"show": b(True)}
    if action[0] == "page":
        link.update({"type": s("PageNavigation"), "navigationSection": s(action[1])})
    else:
        link.update({"type": s("Bookmark"), "bookmark": s(action[1])})
    v.body["visualContainerObjects"]["visualLink"] = [{"properties": link}]
    return v.plain().alt(alt_key)


# --- page frame ---------------------------------------------------------------

def page_frame(page, headline_measure, menu_items, note_key):
    """fabric-kit Report layout A: top bar (title, filter line, Back/Next, language), a rail with the
    filter toggle, the footer, the headline, and the hidden filter pane that opens over the body."""
    i = PAGES.index(page)
    name = f"en_{page}"
    btn, lang_w, title_w = 28, 64, 180
    by = (TOP_H - btn) / 2
    x_lang = W - G - lang_w
    x_next = x_lang - G - btn
    x_back = x_next - 4 - btn
    items = [("top_bar", 0, 0, W, TOP_H, block(CHROME)),
             ("top_rule", 0, TOP_H, W, 1, block(BORDER)),
             ("rail", 0, TOP_H + 1, RAIL_W, FOOTER_Y - TOP_H - 1, block(CHROME)),
             ("rail_rule", RAIL_W, TOP_H + 1, 1, FOOTER_Y - TOP_H - 1, block(BORDER)),
             ("footer_bar", 0, FOOTER_Y, W, FOOTER_H, block(CHROME)),
             ("footer_rule", 0, FOOTER_Y, W, 1, block(BORDER))]
    items.append(("page_title", 12, 0, title_w, TOP_H,
                  textbox([(f"page.{page}", 14, INK, FONT_SEMI)], pad=(8, 0, 0, 0), background=False)))
    # Active slicer filters, on the title row (blank when nothing is filtered)
    items.append(("filter_state", 12 + title_w, 0, x_back - G - 12 - title_w, TOP_H,
                  measure_text("Filter State Text", 10, INK2, FONT, pad=(12, 0, 0, 0), background=False)))
    if i > 0:
        items.append(("nav_back", x_back, by, btn, btn,
                      button("nav.back", ("page", f"en_{PAGES[i - 1]}"), "nav", "alt.back", size=14)))
    if i < len(PAGES) - 1:
        items.append(("nav_next", x_next, by, btn, btn,
                      button("nav.next", ("page", f"en_{PAGES[i + 1]}"), "nav", "alt.next", size=14)))
    items.append(("nav_language", x_lang, by, lang_w, btn,
                  button("nav.language", ("page", f"ar_{page}"), "language", "alt.language", size=10)))
    items.append(("menu_open", (RAIL_W - btn) / 2, TOP_H + G, btn, btn,
                  button("nav.menu-open", ("bookmark", f"bm_{name}_menu_open"), "bookmark", "alt.menu-open")))
    items.append(("headline", BODY_X, BODY_Y, BODY_W, HEADLINE_H,
                  measure_text(headline_measure, 12, INK2, FONT, pad=(0, 0, 0, 0), background=False)))

    items.append(("footer_source", 12, FOOTER_Y, 820, FOOTER_H,
                  textbox([("footer.source", 9, INK2, FONT)], pad=(4, 0, 0, 0), background=False)))
    items.append(("footer_status", 844, FOOTER_Y, W - 12 - 844, FOOTER_H,
                  measure_text("Footer Status", 9, INK2, FONT, pad=(4, 0, 0, 0), background=False)))
    items[-1][5].body["visualContainerObjects"]["title"][0]["properties"]["alignment"] = s("right")

    # Filter pane: opens over the rail and the body's reading-start edge, hidden until opened
    top, bottom = TOP_H + 1, FOOTER_Y
    panel = [("menu_panel", 0, top, PANE_W, bottom - top, menu_background()),
             # Room for two lines: the Arabic title wraps
             ("menu_title", 0, top, PANE_W - 40, 62, textbox([("menu.title", 12, INK, FONT_SEMI)], pad=(10, 0, 12, 8),
                                                              background=False)),
             ("menu_close", PANE_W - 6 - btn, top + 6, btn, btn,
              button("nav.menu-close", ("bookmark", f"bm_{name}_menu_closed"), "bookmark", "alt.menu-close"))]
    y = top + 64
    for j, vis in enumerate(menu_items):
        panel.append((f"menu_item{j}", 4, y, PANE_W - 8, 56, vis))
        y += 60
    panel.append(("menu_note", 4, y, PANE_W - 8, bottom - y - 4,
                  textbox([(note_key, 9, INK2, FONT)], pad=(4, 4, 8, 8), background=False)))
    for item in panel:
        item[5].hidden = True
    return items, [item[0] for item in panel], panel


def menu_background():
    v = block(CHROME)
    v.body["objects"]["outline"] = [{"properties": {"show": b(True)}},
                                    {"properties": {"lineColor": colour(BORDER), "weight": n(1)},
                                     "selector": {"id": "default"}}]
    v.body["visualContainerObjects"]["dropShadow"] = [{"properties": {"show": b(True), "position": s("Outer"),
                                                                        "preset": s("Custom"), "shadowBlur": n(12),
                                                                        "shadowDistance": n(2), "transparency": n(80)}}]
    return v


def kpi_strip(cells):
    """One panel across the body: label, value and status line per cell (fabric-kit KPI strip).
    cells: (title key, value measure, status measure, key, status filters). key: the page's lead number,
    larger than the others (one per page). The filters keep each status line's old visual filters."""
    cw = BODY_W / len(cells)
    items = [("kpi_strip", BODY_X, STRIP_Y, BODY_W, KPI_H, block())]
    for j, (title_key, value, status, key, filters) in enumerate(cells):
        x = BODY_X + j * cw
        if j:
            items.append((f"kpi{j}_rule", x, STRIP_Y + 12, 1, KPI_H - 24, block(BORDER)))
        line = measure_text(status, 9, INK if key else INK2, FONT, pad=(0, 0, 12, 12), background=False)
        line.filters += filters
        # Title boxes leave room for the taller Arabic line, or the text box shows a scroll bar
        items += [(f"kpi{j}_title", x, STRIP_Y + 2, cw, 28,
                   textbox([(title_key, 10, INK2, FONT)], pad=(6, 0, 12, 12), background=False)),
                  (f"kpi{j}_value", x, STRIP_Y + 28, cw, 34,
                   value_card(value, 22 if key else 18).alt(title_key)),
                  (f"kpi{j}_status", x, STRIP_Y + 62, cw, KPI_H - 64, line)]
    return items


# --- pages --------------------------------------------------------------------

def overview():
    kpis = kpi_strip([
        ("kpi.share.title", "Wind Solar Share % Full Coverage", "KPI Share Status", True,
         [range_filter("Generation", "Year", 2015, 2023)]),
        ("kpi.operating.title", "Operating GW", "KPI Operating Status", False,
         [range_filter("Unit", "Start Year", 2015, 2025)]),
        ("kpi.pipeline.title", "Pipeline GW", "KPI Pipeline Status", False, [in_filter("Status", "In Pipeline", "true")])])
    main = online_panel(BODY_X, MAIN_Y, BODY_W, BODY_BOTTOM - MAIN_Y)
    menu = [slicer(col("Overview Focus", "Focus"), "field.focus", single=True),
            slicer(col("Technology", "Technology Group"), "field.technology"),
            slicer(col("Country", "Country"), "field.country")]
    return "Headline Overview", kpis, main, menu, "note.overview"


def breakdown():
    kpis = kpi_strip([
        ("kpi.concentration.title", "Top 3 Pipeline Share %", "KPI Concentration Status", True, []),
        ("kpi.hydrogen.title", "Hydrogen Pipeline GW", "KPI Hydrogen Status", False, []),
        ("kpi.risk.title", "Dropped GW", "KPI Risk Status", False, [in_filter("Status", "Delivery Risk", "true")])])
    left_w = (BODY_W - G) * 0.58
    by_country = bars(col("Country", "Country"), [("Total GW", "field.gw")], "chart.country-status",
                      legend=("Status", "Status", {k: v for k, v in STATUS.items() if k not in ("Shelved", "Cancelled")}),
                      sort_measure="Total GW", legend_show=True, value_axis=True, show_labels=False)
    by_country.filters.append(in_filter("Status", "In Totals", "true"))
    report_tooltip(by_country, "tt_tech")
    # How dependent each country's pipeline is on green hydrogen: tied (dark grey) and the rest (neutral)
    tied, rest = mea("Hydrogen Pipeline GW"), mea("Non-hydrogen Pipeline GW")
    by_hydrogen = bars(col("Country", "Country"), [("Hydrogen Pipeline GW", "field.hydrogen-gw"),
                                                   ("Non-hydrogen Pipeline GW", "field.other-pipeline")],
                       "chart.hydrogen-by-country", detail_measure="Hydrogen % of Pipeline Label",
                       sort_measure="Hydrogen Pipeline GW", legend_show=True, value_axis=True)
    by_hydrogen.body["objects"]["dataPoint"] = [
        {"properties": {"fill": colour(INK2)}, "selector": {"metadata": ref(tied)}},
        {"properties": {"fill": colour(NEUTRAL)}, "selector": {"metadata": ref(rest)}},
    ]
    # Label the tied segment only, in white inside the dark fill; the rest of the pipeline stays in the tooltip
    by_hydrogen.body["objects"]["labels"] += [
        {"properties": {"color": colour(CHROME), "detailColor": colour(CHROME)}, "selector": {"metadata": ref(tied)}},
        {"properties": {"showSeries": b(False)}, "selector": {"metadata": ref(rest)}},
    ]
    main = [("by_country", BODY_X, MAIN_Y, left_w, BODY_BOTTOM - MAIN_Y, by_country),
            ("by_hydrogen", BODY_X + left_w + G, MAIN_Y, BODY_W - left_w - G, BODY_BOTTOM - MAIN_Y, by_hydrogen)]
    menu = [slicer(col("Technology", "Technology Group"), "field.technology"),
            slicer(col("Country", "Country"), "field.country")]
    return "Headline Breakdown", kpis, main, menu, "note.breakdown"


def opportunity():
    kpis = kpi_strip([
        ("kpi.intensity.title", "Emissions Intensity Full Coverage", "KPI Intensity Status", False,
         [range_filter("Generation", "Year", 2015, 2023)]),
        ("kpi.construction.title", "Construction GW", "KPI Construction Status", True, []),
        ("kpi.announced.title", "Announced GW", "KPI Announced Status", False, [in_filter("Status", "In Pipeline", "true")])])
    left_w = (BODY_W - G) * 0.5
    # Widths sum to the inner width (608 - 2 x 8 padding) less 18 px for the scroll bar
    card = table([(col("Country", "Country"), "field.country", 110), (mea("Ember Year"), "field.year", 59),
                  (mea("Scorecard Share %"), "field.share", 78),
                  (mea("Emissions Intensity g/kWh"), "field.intensity", 59),
                  (mea("Operating GW"), "field.operating", 78), (mea("Construction GW"), "field.construction", 105),
                  (mea("Scorecard Pipeline GW"), "field.pipeline", 85)],
                 bar_measure="Construction GW", title_key="chart.scorecard")
    # Gap to the world share: bars either side of zero (= the world); the top builder in the accent
    gap = bars(col("Country", "Country"), [("Share Gap to World pts", "field.gap")], "chart.gap-to-world",
               fill_measure="Top Builder Colour", axis_max="Share Gap Axis Max", axis_min="Share Gap Axis Min")
    report_tooltip(gap, "tt_gap")
    main = [("gap_to_world", BODY_X, MAIN_Y, left_w, BODY_BOTTOM - MAIN_Y, gap),
            ("scorecard", BODY_X + left_w + G, MAIN_Y, BODY_W - left_w - G, BODY_BOTTOM - MAIN_Y, card)]
    menu = [slicer(col("Technology", "Technology Group"), "field.technology"),
            slicer(col("Country", "Country"), "field.country")]
    return "Headline Opportunity", kpis, main, menu, "note.opportunity"


def detail():
    top_h = 320
    left_w = (BODY_W - G) * 0.58
    top = bars(col("Plant", "Plant"), [("Top 10 Pipeline GW", "field.gw")], "chart.top-projects",
               legend=("Status", "Status", {k: STATUS[k] for k in ("Under construction", "Pre-construction", "Announced")}),
               detail_measure="Hydrogen Marker", sort_measure="Top 10 Pipeline GW", legend_show=True, value_axis=True,
               show_labels=False)
    owners = bars(col("Ownership", "Owner"), [("Top 10 Owner Operating GW", "field.gw")], "chart.top-owners",
                  fill_measure="Neutral Colour")
    # Widths sum to the inner width (1224 - 2 x 8 padding) less 18 px for the scroll bar
    projects = table([(col("Plant", "Plant"), "field.plant", 286), (col("Country", "Country"), "field.country", 98),
                      (col("Technology", "Technology Group"), "field.technology", 85),
                      (mea("Status Dot"), "field.status-dot", 20), (col("Status", "Status"), "field.status", 125), (mea("Capacity MW"), "field.capacity-mw", 91),
                      (col("Unit", "Start Year"), "field.start-year", 72), (col("Unit", "Owner"), "field.owner", 333),
                      (mea("Hydrogen Marker"), "field.hydrogen", 80)],
                     bar_measure="Capacity MW", title_key="chart.projects", dot_measure="Status Dot",
                     filters=[in_filter("Status", "In Totals", "true")])
    y = STRIP_Y
    main = [("top_projects", BODY_X, y, left_w, top_h, top),
            ("top_owners", BODY_X + left_w + G, y, BODY_W - left_w - G, top_h, owners),
            ("projects", BODY_X, y + top_h + G, BODY_W, BODY_BOTTOM - y - top_h - G, projects)]
    menu = [slicer(col("Status", "Status"), "field.status"),
            slicer(col("Technology", "Technology Group"), "field.technology"),
            slicer(col("Country", "Country"), "field.country")]
    return "Headline Detail", [], main, menu, "note.detail"


# --- tooltip pages ------------------------------------------------------------

def tooltip_tech():
    """Value first (GW), then what was hovered, then the technology split."""
    chart = bars(col("Technology", "Technology Group"), [("Tooltip GW", "field.gw")], fill_measure="Technology Colour",
                 sort_by_category=True, axis_max="Tooltip GW Bar Max", size=12)
    chart.title("tooltip.by-technology", 12, INK2, FONT)
    chart.body["visualContainerObjects"]["padding"] = [{"properties": {"top": n(0), "bottom": n(4), "left": n(12),
                                                                         "right": n(12)}}]
    return 240, [("value", 0, 0, TOOLTIP_W, 46, measure_text("Tooltip GW Text", 24, INK, FONT_SEMI, pad=(8, 0, 12, 12))),
                 ("context", 0, 46, TOOLTIP_W, 28, measure_text("Tooltip Context Text", 12, INK2, FONT, pad=(0, 0, 12, 12))),
                 ("by_technology", 0, 74, TOOLTIP_W, 166, chart)]


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
        "objects": {"background": [{"properties": {"color": colour(CHROME), "transparency": n(0)}}]},
        "filterConfig": {"filters": [dict(in_filter("Language", "Code", "'en'", name=f"lang_{name}"),
                                          isHiddenInViewMode=True, isLockedInViewMode=True)]},
        "annotations": [{"name": "i18n", "value": json.dumps({"name": f"page.{page.replace('_', '-')}"})}],
    })
    for z, (nm, x, y, w, h, v) in enumerate(items):
        write(folder / "visuals" / nm / "visual.json", visual_json(nm, x, y, w, h, z, v.plain()))


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


def write_theme():
    """Register theme/fernstone-tidepool-light.json (fabric-kit brand theme). The file name carries a content
    hash, so every edit gets a new suffix, and the theme's "name" matches the file name."""
    theme = json.loads((ROOT / "theme" / "fernstone-tidepool-light.json").read_text(encoding="utf-8"))
    digest = hashlib.sha256(json.dumps(theme, sort_keys=True).encode()).hexdigest()[:8]
    file_name = f"{THEME}-{digest}.json"
    theme["name"] = file_name
    resources = REPORT / "StaticResources" / "RegisteredResources"
    shutil.rmtree(resources, ignore_errors=True)
    write(resources / file_name, theme)
    write(DEFINITION / "report.json", {
        "$schema": f"{SCHEMA}/report/3.3.0/schema.json",
        "themeCollection": {"customTheme": {"name": file_name, "type": "RegisteredResources",
                                            "reportVersionAtImport": {"visual": "1.8.81", "report": "2.0.81",
                                                                      "page": "1.3.81"}}},
        "resourcePackages": [{"name": "RegisteredResources", "type": "RegisteredResources",
                              "items": [{"name": file_name, "path": file_name, "type": "CustomTheme"}]}]})


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
    if page in DRILLTHROUGH:
        entity, prop = DRILLTHROUGH[page]
        page_json = json.loads((folder / "page.json").read_text(encoding="utf-8"))
        page_json["pageBinding"] = {"name": f"drill_{name}", "type": "Drillthrough", "parameters": [
            {"name": f"drill_{name}_param", "boundFilter": f"drill_{name}_filter", "fieldExpr": col(entity, prop)}]}
        page_json["filterConfig"]["filters"].append({"name": f"drill_{name}_filter", "field": col(entity, prop),
                                                     "type": "Categorical", "howCreated": "Drillthrough"})
        write(folder / "page.json", page_json)
    # The menu panel always sits on top of everything else (visual-guidelines.md section 3)
    for z, (nm, x, y, w, h, v) in enumerate(frame + kpis + main + panel):
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
    write_theme()
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
