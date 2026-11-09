"""Render the project cards and the section heading above them.

Writes, per theme:
    assets/project_<slug>_<theme>.svg   one card per profile.PROJECTS entry
    assets/heading_projects_<theme>.svg  the "$ ls ~/projects" divider

Like the link buttons, each card has to be its own image inside its own link
(an <img> SVG is never clickable inside). Two cards share a row: every image is
exactly half the canvas wide, the gap is drawn inside the images, and the outer
edges line up with the card and the board above and below.

A project without a tagline renders a status line instead of invented copy;
fill `tagline`/`about` in tools/profile.py and the card grows its text.

Usage:
    python tools/build_projects.py
"""

from __future__ import annotations

import html
import re
import textwrap
from pathlib import Path

from build_pacman import validate_smil
from profile import (ADVANCE, CANVAS_W, FONT_FACE, FONT_STACK, LINE_MID, PROJECTS,
                     RADIUS, THEMES, mix)

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "assets"

GAP = 14                 # between cards; also drawn under each row
SLOT_W = CANVAS_W / 2
CARD_W = (CANVAS_W - GAP) / 2
CARD_H = 206
PAD = 22
TILE = 52

NAME_FONT = 21
BODY_FONT = 13.5
BODY_LINE = 20
TAG_FONT = 12
TAG_H = 24

ACCENTS = ("key", "value", "pac", "coral")   # one per card, in order

# (file name, command, path, comment) for each section divider in the README.
HEADINGS = (
    ("projects", "ls", "projects", "# what I'm building"),
    ("activity", "git log", "activity", "# the last year, one square a day"),
)


def esc(t: str) -> str:
    return html.escape(t, quote=True)


def slug(name: str) -> str:
    return re.sub(r"[^a-z0-9]+", "-", name.lower()).strip("-")


def text_w(s: str, size: float) -> float:
    return len(s) * size * ADVANCE


def initials(name: str) -> str:
    parts = re.findall(r"[A-Z][a-z]*|[a-z]+|\d+", name)
    if len(parts) >= 2:
        return (parts[0][0] + parts[1][0]).upper()
    return name[:2].upper()


def pulse(dur: float = 2.2) -> str:
    return (f'<animate attributeName="opacity" values="1;0.25;1" keyTimes="0;0.5;1" '
            f'dur="{dur}s" repeatCount="indefinite"/>')


def card(theme: str, index: int, p: dict) -> str:
    c = THEMES[theme]
    accent = c[ACCENTS[index % len(ACCENTS)]]
    # Left card hugs the left edge of its slot, right card the right edge.
    x0 = 0 if index % 2 == 0 else SLOT_W - CARD_W
    tx = x0 + PAD + TILE + 16             # text column
    text_right = x0 + CARD_W - PAD
    cols = int((text_right - tx) / (BODY_FONT * ADVANCE))

    parts: list[str] = []
    # Frame, with a thin accent bar along the top.
    parts.append(f'<rect x="{x0 + 0.5:g}" y="0.5" width="{CARD_W - 1:g}" height="{CARD_H - 1}" '
                 f'rx="{RADIUS - 0.5}" fill="{c["bg"]}" stroke="{c["border"]}"/>')
    parts.append(f'<rect x="{x0 + PAD:g}" y="0" width="{CARD_W - 2 * PAD:g}" height="2" fill="{accent}" rx="1"/>')

    # Monogram tile.
    ty = PAD + 2
    parts.append(f'<rect x="{x0 + PAD:g}" y="{ty}" width="{TILE}" height="{TILE}" rx="10" '
                 f'fill="{mix(c["bg"], accent, 0.14)}" stroke="{mix(c["bg"], accent, 0.45)}"/>')
    ini = initials(p["name"])
    parts.append(f'<text x="{x0 + PAD + TILE / 2:g}" y="{ty + TILE / 2 + LINE_MID * 20:.2f}" '
                 f'font-size="20px" font-weight="bold" fill="{accent}" text-anchor="middle">{esc(ini)}</text>')

    # Name + status.
    name_y = ty + 20
    parts.append(f'<text x="{tx:g}" y="{name_y}" font-size="{NAME_FONT}px" font-weight="bold" '
                 f'fill="{c["fg"]}">{esc(p["name"])}</text>')
    live = p.get("status") == "live"
    status = "live" if live else "in development"
    dot = c["add"] if live else c["pac"]
    sy = name_y + 22
    parts.append(f'<circle cx="{tx + 4:g}" cy="{sy - 4:g}" r="4" fill="{dot}">{pulse()}</circle>')
    parts.append(f'<text x="{tx + 14:g}" y="{sy:g}" font-size="12.5px" fill="{c["muted"]}">{status}</text>')
    if p.get("link_label"):
        label = f"{p['link_label']} ↗"
        if tx + 14 + text_w(status + "  ", 12.5) + text_w(label, 12.5) > text_right:
            raise SystemExit(f"{p['name']}: link label too long for the status line")
        parts.append(f'<text x="{text_right:g}" y="{sy:g}" font-size="12.5px" fill="{accent}" '
                     f'text-anchor="end">{esc(label)}</text>')

    # Body.
    y = sy + 30
    if p.get("tagline"):
        parts.append(f'<text x="{tx:g}" y="{y:g}" font-size="{BODY_FONT}px" fill="{c["fg"]}">'
                     f'{esc(p["tagline"])}</text>')
        y += BODY_LINE
        for line in textwrap.wrap(p.get("about") or "", cols)[:2]:
            parts.append(f'<text x="{tx:g}" y="{y:g}" font-size="{BODY_FONT}px" '
                         f'fill="{c["muted"]}">{esc(line)}</text>')
            y += BODY_LINE
    else:
        parts.append(f'<text x="{tx:g}" y="{y:g}" font-size="{BODY_FONT}px" fill="{c["muted"]}">'
                     f'<tspan fill="{c["value"]}">$</tspan> cat {esc(slug(p["name"]))}/README.md</text>')
        y += BODY_LINE
        parts.append(f'<text x="{tx:g}" y="{y:g}" font-size="{BODY_FONT}px" fill="{c["dots"]}">'
                     f'# being built, details soon</text>')
        y += BODY_LINE

    # Footer: tags on the left, link on the right.
    fy = CARD_H - PAD - TAG_H
    x = tx
    for tag in p.get("tags", []):
        w = text_w(tag, TAG_FONT) + 18
        parts.append(f'<rect x="{x:g}" y="{fy}" width="{w:.1f}" height="{TAG_H}" rx="{TAG_H / 2:g}" '
                     f'fill="{c["chip"]}" stroke="{c["border"]}"/>')
        parts.append(f'<text x="{x + 9:g}" y="{fy + TAG_H / 2 + LINE_MID * TAG_FONT:.2f}" '
                     f'font-size="{TAG_FONT}px" fill="{c["fg"]}">{esc(tag)}</text>')
        x += w + 8
    if x - 8 > text_right:
        raise SystemExit(f"{p['name']}: tags overflow the card")

    title = p["name"] + (f": {p['tagline']}" if p.get("tagline") else " (in development)")
    return f"""<?xml version='1.0' encoding='UTF-8'?>
<svg xmlns="http://www.w3.org/2000/svg" width="{SLOT_W:g}" height="{CARD_H + GAP}" viewBox="0 0 {SLOT_W:g} {CARD_H + GAP}"
     font-family="{FONT_STACK}" role="img" aria-label="{esc(title)}">
<title>{esc(title)}</title>
<style>
{FONT_FACE}
text, tspan {{white-space: pre;}}
</style>
{chr(10).join(parts)}
</svg>
"""


def heading(theme: str, cmd: str, path: str, comment: str) -> str:
    """A shell-prompt divider: `$ <cmd> ~/<path>  # comment ─────────`."""
    c = THEMES[theme]
    h, size = 46, 15
    y = h / 2 + LINE_MID * size
    prompt = f"$ {cmd} ~/{path}"
    x2 = 4 + text_w(prompt + "  ", size)
    rule_x = x2 + text_w(comment, size) + 14
    return f"""<?xml version='1.0' encoding='UTF-8'?>
<svg xmlns="http://www.w3.org/2000/svg" width="{CANVAS_W}" height="{h}" viewBox="0 0 {CANVAS_W} {h}"
     font-family="{FONT_STACK}" role="img" aria-label="{esc(path.title())}">
<title>{esc(path.title())}</title>
<style>
{FONT_FACE}
text, tspan {{white-space: pre;}}
</style>
<text x="4" y="{y:.2f}" font-size="{size}px"><tspan fill="{c['value']}">$</tspan><tspan fill="{c['fg']}"> {esc(cmd)} </tspan><tspan fill="{c['key']}" font-weight="bold">~/{esc(path)}</tspan></text>
<text x="{x2:.2f}" y="{y:.2f}" font-size="{size}px" fill="{c['muted']}">{esc(comment)}</text>
<rect x="{rule_x:.2f}" y="{h / 2:g}" width="{CANVAS_W - 4 - rule_x:.2f}" height="1" fill="{c['border']}"/>
</svg>
"""


def main() -> None:
    OUT.mkdir(exist_ok=True)
    for theme in THEMES:
        for i, p in enumerate(PROJECTS):
            svg = card(theme, i, p)
            validate_smil(svg)
            out = OUT / f"project_{slug(p['name'])}_{theme}.svg"
            out.write_text(svg, encoding="utf-8")
            print(f"wrote {out.relative_to(ROOT)} ({out.stat().st_size:,} bytes)")
        for name, cmd, path, comment in HEADINGS:
            out = OUT / f"heading_{name}_{theme}.svg"
            out.write_text(heading(theme, cmd, path, comment), encoding="utf-8")
            print(f"wrote {out.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
