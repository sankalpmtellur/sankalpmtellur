"""Rebuild every generated SVG from tools/profile.py and the cache/ files.

Does not touch the network: run tools/fetch_stats.py first for fresh numbers.

Usage:
    python tools/build_all.py
"""

import build_card
import build_links
import build_pacman
import build_projects

for step in (build_card, build_links, build_projects, build_pacman):
    print(f"--- {step.__name__}")
    step.main()
