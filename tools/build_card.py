"""Build the neofetch-style hero card: assets/card_dark.svg / assets/card_light.svg.

Layout, left to right inside a terminal window:
    procedural ASCII orb (tools/ascii_art.py) | info panel + live GitHub stats

The panel is assembled from Row objects: fixed text segments plus elastic
dotted `fill` runs that stretch so every row lands on exactly PANEL_COLS
characters. render() asserts the width, so an arithmetic slip fails the build
instead of shipping a row that drifts out of alignment.

Animation is SMIL only (GitHub serves README SVGs through <img>, which runs
SMIL but no script) and limited to the blinking prompt cursor. A one-shot
"rows print in" reveal was tried and dropped: any renderer that snapshots
frame 0 (link previews, paused background tabs) showed an empty panel.

Usage:
    python tools/build_card.py
"""

from __future__ import annotations

import datetime as dt
import html
import json
from pathlib import Path

from ascii_art import CELL_ASPECT as ART_CELL_ASPECT, art
from profile import (ADVANCE, CONTACT, FONT_FACE, FONT_STACK, GITHUB_SINCE, INFO,
                     LINE_MID, LINE_PAD, RADIUS, THEMES, TITLE, CANVAS_W)

ROOT = Path(__file__).resolve().parent.parent
STATS_SRC = ROOT / "cache" / "stats.json"
CALENDAR_SRC = ROOT / "cache" / "calendar.json"
OUT = ROOT / "assets"

# --- Geometry ---------------------------------------------------------------
MARGIN = 22
BAR_H = 38                 # window title bar
ART_COL_WIDTH = 392.0      # the art is fitted to this pixel width
GUTTER = 20
PANEL_FONT = 15.5
PANEL_LINE = 20.0
PANEL_COLS = 59

def esc(text: str) -> str:
    return html.escape(text, quote=False)


# --- Row builder ------------------------------------------------------------
class Row:
    """A panel row assembled from fixed segments and elastic fills."""

    def __init__(self) -> None:
        self._segs: list[dict] = []

    def text(self, value: str, cls: str | None = None) -> "Row":
        self._segs.append({"kind": "text", "v": str(value), "cls": cls})
        return self

    def key(self, value: str) -> "Row":
        for i, part in enumerate(str(value).split(".")):
            if i:
                self.text(".", cls="cc")
            self.text(part, cls="key")
        return self

    def value(self, v: str) -> "Row":
        return self.text(v, cls="value")

    def fill(self, char: str = ".", cls: str = "cc") -> "Row":
        self._segs.append({"kind": "fill", "char": char, "cls": cls})
        return self

    def _widths(self, width: int) -> dict[int, int]:
        fills = [i for i, s in enumerate(self._segs) if s["kind"] == "fill"]
        fixed = sum(len(s["v"]) for s in self._segs if s["kind"] == "text")
        if not fills:
            return {}
        slack = width - fixed
        if slack < len(fills):
            raise SystemExit(f"row does not fit in {width} cols: "
                             f"{''.join(s.get('v', '~') for s in self._segs)!r}")
        base, extra = divmod(slack, len(fills))
        return {idx: base + (1 if n < extra else 0) for n, idx in enumerate(fills)}

    def render(self, width: int) -> str:
        widths = self._widths(width)
        out, total = [], 0
        for i, s in enumerate(self._segs):
            body = s["v"] if s["kind"] == "text" else s["char"] * widths[i]
            total += len(body)
            out.append(f'<tspan class="{s["cls"]}">{esc(body)}</tspan>' if s["cls"] else esc(body))
        if self._segs and total != width and widths:
            raise AssertionError(f"row rendered {total} cols, expected {width}")
        return "".join(out)


def info_row(key: str, value: str) -> Row:
    return (Row().text(". ", cls="cc").key(key).text(":")
            .text(" ").fill().text(" ").value(value))


def rule_row(label: str, cls: str = "rule") -> Row:
    return Row().text(label, cls=cls).text(" ").fill("─", cls="rulefill")


# --- Data -------------------------------------------------------------------
def uptime(today: dt.date | None = None) -> str:
    today = today or dt.date.today()
    years = today.year - GITHUB_SINCE.year
    months = today.month - GITHUB_SINCE.month
    days = today.day - GITHUB_SINCE.day
    if days < 0:
        months -= 1
        days += ((today.replace(day=1) - dt.timedelta(days=1)).day)
    if months < 0:
        years -= 1
        months += 12

    def plural(n: int, word: str) -> str:
        return f"{n} {word}" + ("" if n == 1 else "s")

    return f"{plural(years, 'year')}, {plural(months, 'month')}, {plural(days, 'day')}"


STAT_KEYS = ("repos", "contrib", "stars", "commits", "followers", "loc", "added", "deleted")


def load_stats() -> tuple[dict, str | None]:
    """Formatted figures, plus the date they were fetched. '--' marks unknowns."""
    st = {k: "--" for k in STAT_KEYS}
    st["year"] = "--"
    updated = None
    if STATS_SRC.exists():
        raw = json.loads(STATS_SRC.read_text(encoding="utf-8"))
        for k in STAT_KEYS:
            if isinstance(raw.get(k), int):
                st[k] = f"{raw[k]:,}"
        updated = (raw.get("updated") or "")[:10] or None
    if CALENDAR_SRC.exists():
        cal = json.loads(CALENDAR_SRC.read_text(encoding="utf-8"))
        st["year"] = f"{cal['total']:,}"
    return st, updated


# --- Panel ------------------------------------------------------------------
def panel_rows() -> list[Row | None]:
    st, _ = load_stats()
    rows: list[Row | None] = [rule_row(TITLE, cls="title")]
    for item in INFO:
        if item is None:
            rows.append(None)
            continue
        k, v = item
        rows.append(info_row(k, uptime() if k == "Uptime" else v))

    rows += [None, rule_row("Contact")]
    rows += [info_row(label, shown) for label, shown, _ in CONTACT]

    rows += [None, rule_row("GitHub Stats")]
    rows.append(
        Row().text(". ", cls="cc").key("Repos").text(":").text(" ").fill().text(" ")
        .value(st["repos"]).text(" {").text("Contributed", cls="key").text(": ")
        .value(st["contrib"]).text("}")
        .text(" | ").key("Stars").text(":").text(" ").fill().text(" ").value(st["stars"])
    )
    rows.append(
        Row().text(". ", cls="cc").key("Commits").text(":").text(" ").fill().text(" ")
        .value(st["commits"])
        .text(" | ").key("Followers").text(":").text(" ").fill().text(" ").value(st["followers"])
    )
    rows.append(
        Row().text(". ", cls="cc").key("Contributions").text(" (last year):").text(" ")
        .fill().text(" ").value(st["year"])
    )
    rows.append(
        Row().text(". ", cls="cc").key("Lines of Code").text(":").text(" ").fill().text(" ")
        .value(st["loc"])
        .text(" ( ").text(st["added"], cls="add").text("++", cls="add").text(", ")
        .text(st["deleted"], cls="del").text("--", cls="del").text(" )")
    )
    return rows


def build(theme: str) -> str:
    c = THEMES[theme]
    lines = art(invert=(theme == "light"))
    art_cols = max(len(l) for l in lines)
    art_font = ART_COL_WIDTH / (art_cols * ADVANCE)
    art_line = art_font * ADVANCE / ART_CELL_ASPECT

    rows = panel_rows()
    n_panel = len(rows) + 2                       # + blank + prompt
    panel_x = MARGIN + ART_COL_WIDTH + GUTTER
    panel_w = PANEL_COLS * PANEL_FONT * ADVANCE
    width = CANVAS_W
    # centre the panel in what is left after the art column
    panel_x += (width - MARGIN - panel_x - panel_w) / 2

    panel_span = (n_panel - 1) * PANEL_LINE
    art_span = (len(lines) - 1) * art_line
    half = max(panel_span / 2 + LINE_PAD * PANEL_FONT, art_span / 2 + LINE_PAD * art_font)
    axis = BAR_H + MARGIN + half
    height = round(axis + half + MARGIN)

    py0 = axis - panel_span / 2 + LINE_MID * PANEL_FONT
    ay0 = axis - art_span / 2 + LINE_MID * art_font

    panel = []
    for i, row in enumerate(rows):
        y = py0 + i * PANEL_LINE
        body = '<tspan class="cc">.</tspan>' if row is None else row.render(PANEL_COLS)
        panel.append(f'<text x="{panel_x:.2f}" y="{y:.2f}">{body}</text>')
    y = py0 + (len(rows) + 1) * PANEL_LINE
    panel.append(
        f'<text x="{panel_x:.2f}" y="{y:.2f}">'
        f'<tspan class="key">{esc(TITLE)}</tspan><tspan class="cc"> ~ </tspan>'
        f'<tspan class="value">$ </tspan>'
        f'<tspan class="value">█<animate attributeName="opacity" values="1;0" dur="1.06s" '
        f'calcMode="discrete" repeatCount="indefinite"/></tspan></text>'
    )

    art_tspans = "\n".join(
        f'<tspan x="{MARGIN}" y="{ay0 + i * art_line:.2f}">{esc(l)}</tspan>'
        for i, l in enumerate(lines)
    )

    _, updated = load_stats()
    stamp = f"updated {updated}" if updated else ""
    dots = "".join(
        f'<circle cx="{MARGIN + 6 + i * 20}" cy="{BAR_H / 2 + 1:g}" r="6" fill="{col}"/>'
        for i, col in enumerate(("#ff5f57", "#febc2e", "#28c840"))
    )
    bar_mid = BAR_H / 2 + 1 + LINE_MID * 13

    return f"""<?xml version='1.0' encoding='UTF-8'?>
<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}"
     font-family="{FONT_STACK}" role="img" aria-label="Sankalp Tellur, AI engineer and full-stack developer">
<title>Sankalp Tellur, AI engineer and full-stack developer</title>
<style>
{FONT_FACE}
text, tspan {{white-space: pre;}}
.key {{fill: {c['key']};}}
.value {{fill: {c['value']};}}
.title {{fill: {c['key']}; font-weight: bold;}}
.rule {{fill: {c['fg']}; font-weight: bold;}}
.rulefill {{fill: {c['dots']};}}
.add {{fill: {c['add']};}}
.del {{fill: {c['del']};}}
.cc {{fill: {c['dots']};}}
</style>
<defs>
  <linearGradient id="art" gradientUnits="userSpaceOnUse" x1="{MARGIN}" y1="{ay0 - art_font:.1f}"
                  x2="{MARGIN + ART_COL_WIDTH:.1f}" y2="{ay0 + art_span:.1f}">
    <stop offset="0" stop-color="{c['art_a']}"/>
    <stop offset="1" stop-color="{c['art_b']}"/>
  </linearGradient>
  <clipPath id="win"><rect width="{width}" height="{height}" rx="{RADIUS}"/></clipPath>
</defs>
<g clip-path="url(#win)">
<rect width="{width}" height="{height}" fill="{c['bg']}"/>
<rect width="{width}" height="{BAR_H}" fill="{c['chip']}"/>
<rect y="{BAR_H}" width="{width}" height="1" fill="{c['border']}"/>
</g>
<rect x="0.5" y="0.5" width="{width - 1}" height="{height - 1}" rx="{RADIUS - 0.5}" fill="none" stroke="{c['border']}"/>
{dots}
<text x="{width / 2:g}" y="{bar_mid:.2f}" font-size="13px" fill="{c['muted']}" text-anchor="middle">{esc(TITLE)}: ~/profile</text>
<text x="{width - MARGIN:g}" y="{bar_mid:.2f}" font-size="12px" fill="{c['muted']}" text-anchor="end">{esc(stamp)}</text>
<text fill="url(#art)" font-size="{art_font:.2f}px">
{art_tspans}
</text>
<g fill="{c['fg']}" font-size="{PANEL_FONT:g}px">
{chr(10).join(panel)}
</g>
</svg>
"""


def main() -> None:
    OUT.mkdir(exist_ok=True)
    st, updated = load_stats()
    print(f"uptime   : {uptime()}")
    print(f"stats    : {updated or 'not fetched yet (placeholders)'}")
    for name in THEMES:
        out = OUT / f"card_{name}.svg"
        out.write_text(build(name), encoding="utf-8")
        print(f"wrote {out.relative_to(ROOT)} ({out.stat().st_size:,} bytes)")


if __name__ == "__main__":
    main()
