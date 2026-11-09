"""Everything personal about the profile, in one place.

Every generator in tools/ imports from here, so changing a line of text, a
link or a colour means editing this file and re-running tools/build_all.py
(or just pushing: the workflow rebuilds on any change under tools/).

Only facts belong here. Each value below is either stated by Sankalp or
published on his own GitHub profile or portfolio -- nothing is inferred.
"""

from __future__ import annotations

import datetime as dt

LOGIN = "sankalpmtellur"
REPO = f"{LOGIN}/{LOGIN}"

# Raw URL prefix the README uses for every generated image.
RAW = f"https://raw.githubusercontent.com/{REPO}/main"

NAME = "Sankalp Tellur"
TITLE = "sankalp@tellur"            # the prompt-style header of the card

# The day the GitHub account was created (public: api.github.com/users/...).
# Drives the card's "Uptime" row, which reads as time spent shipping on GitHub.
GITHUB_SINCE = dt.date(2024, 11, 6)

# --- The card's info panel ---------------------------------------------------
# (key, value). None draws an empty dotted spacer row. Dotted keys colour both
# halves, so "Stack.AI" renders as two keys joined by a dot.
INFO = [
    ("Host", "Vijayapura, Karnataka, India"),
    ("Uptime", None),  # filled from GITHUB_SINCE
    ("Kernel", "AI Engineer, Full-Stack Developer"),
    ("Shell", "Builder, aspiring founder"),
    None,
    ("Languages", "Python, TypeScript, JavaScript"),
    ("Stack.Web", "React, Next.js, Node.js"),
    ("Stack.Data", "PostgreSQL, Supabase, Redis"),
    ("Stack.AI", "AI Agents, LLMs, Automation"),
    None,
    ("Focus", "AI products, automation, SaaS"),
    ("Building", "Knili AI, DoPilot, Recall AI, WhoOwes"),
]

# Shown on the card and turned into the clickable buttons under it.
# Taken from the links published on sankalpmtellur.online.
CONTACT = [
    ("Portfolio", "sankalpmtellur.online", "https://sankalpmtellur.online"),
    ("LinkedIn", "in/sankalpmt", "https://www.linkedin.com/in/sankalpmt/"),
    ("Email", "sankalp.tellur2024@nst.rishihood.edu.in",
     "mailto:sankalp.tellur2024@nst.rishihood.edu.in"),
]

# --- Projects ----------------------------------------------------------------
# One card each. `tagline` and `about` are optional: a project without them
# renders as a compact card with just its name and tags, rather than with
# copy that was guessed. `url` makes the card a link in the README.
PROJECTS = [
    {
        "name": "DoPilot",
        "tagline": "An AI agent that drives your real browser.",
        "about": "Plain-English commands become browser actions, each step "
                 "shown live, with approval asked before anything sensitive.",
        "tags": ["TypeScript", "AI Agent", "Chrome Extension"],
        "status": "live",
        "url": "https://dopilot-extension.vercel.app",
        "link_label": "dopilot-extension.vercel.app",
    },
    {
        "name": "Knili AI",
        "tagline": None,
        "about": None,
        "tags": ["AI"],
        "status": "building",
        "url": None,
        "link_label": None,
    },
    {
        "name": "Recall AI",
        "tagline": None,
        "about": None,
        "tags": ["AI"],
        "status": "building",
        "url": None,
        "link_label": None,
    },
    {
        "name": "WhoOwes",
        "tagline": None,
        "about": None,
        "tags": [],
        "status": "building",
        "url": None,
        "link_label": None,
    },
]

# --- Palette -----------------------------------------------------------------
# One palette for every SVG. Dark sits on GitHub's #0d1117 page as a raised
# #161b22 panel; light is white with a hairline border so it still reads as a
# card on GitHub's white page. Accent pairs were checked for >= 4.5:1 text
# contrast on their own background.
THEMES = {
    "dark": {
        "bg": "#161b22", "border": "#30363d", "fg": "#c9d1d9", "muted": "#7d8590",
        "key": "#b392f0",      # violet: keys, accents
        "value": "#79c0ff",    # sky: values
        "art_a": "#d2a8ff", "art_b": "#56d4dd",   # ASCII art gradient
        "add": "#3fb950", "del": "#f85149", "dots": "#484f58",
        "pac": "#f2cc60", "coral": "#D97757",
        "chip": "#21262d",
    },
    "light": {
        "bg": "#ffffff", "border": "#d0d7de", "fg": "#1f2328", "muted": "#59636e",
        "key": "#6639ba",
        "value": "#0550ae",
        "art_a": "#8250df", "art_b": "#0a7f8c",
        "add": "#1a7f37", "del": "#cf222e", "dots": "#afb8c1",
        "pac": "#b07d00", "coral": "#C15F3C",
        "chip": "#f6f8fa",
    },
}

# --- Shared type metrics -----------------------------------------------------
# Consolas advances 0.55em; generic monospace 0.60em. Re-declaring Consolas at
# size-adjust:109% lands it on 0.5995em, so the layout holds with or without
# Consolas installed (this is the reference project's measured trick).
ADVANCE = 0.5995
LINE_MID = 0.35   # a line's visual middle sits this many em above its baseline
LINE_PAD = 0.65   # and a block of lines reaches this far past its outer baselines

CANVAS_W = 1018   # every full-width image is this wide, so they stack as one
RADIUS = 14

FONT_FACE = """@font-face {
  src: local('Consolas'), local('Consolas Bold');
  font-family: 'ConsolasFallback';
  font-display: swap;
  size-adjust: 109%;
}"""
FONT_STACK = "ConsolasFallback,Consolas,Menlo,'DejaVu Sans Mono',monospace"


def mix(a: str, b: str, t: float) -> str:
    """Blend two #rrggbb colours: t=0 is a, t=1 is b."""
    ca = [int(a[i:i + 2], 16) for i in (1, 3, 5)]
    cb = [int(b[i:i + 2], 16) for i in (1, 3, 5)]
    return "#" + "".join(f"{round(x + (y - x) * t):02x}" for x, y in zip(ca, cb))
