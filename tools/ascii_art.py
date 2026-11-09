"""Procedural ASCII art for the card: a lit sphere wrapped in a tilted ring.

The reference card used a photo pushed through an image-to-ASCII converter.
This one is computed instead -- a ray-traced orb (an "AI core") with a
wireframe of latitude/longitude lines and an orbital ring that passes in front
of and behind it. Being code, it is deterministic, needs no source image, and
regenerates identically in CI.

Density ramps run dark-to-bright. On the dark card the densest glyph is the
brightest pixel; on the light card ink is dark, so the ramp is inverted.

Usage (preview in a terminal):
    python tools/ascii_art.py
"""

from __future__ import annotations

import math

COLS, ROWS = 72, 34
# Monospace cells are ~0.5 as wide as tall at the card's line height, so x is
# scaled to keep the sphere round.
CELL_ASPECT = 0.46

RAMP = " .:-=+*#%@"

LIGHT = (-0.55, -0.62, 0.56)        # from upper left, toward the viewer
TILT = math.radians(-16)            # ring tilt about the view axis
RING_INCL = math.radians(72)        # ring inclination (90 = edge-on)


def _norm(v):
    n = math.sqrt(sum(c * c for c in v))
    return tuple(c / n for c in v)


def _rot_z(x, y, a):
    return x * math.cos(a) - y * math.sin(a), x * math.sin(a) + y * math.cos(a)


def render(invert: bool = False) -> list[str]:
    lx, ly, lz = _norm(LIGHT)
    ramp = RAMP[::-1] if invert else RAMP
    R = 0.62                      # sphere radius in normalised units
    ring_r0, ring_r1 = 0.80, 0.98  # ring inner/outer radius
    out = []
    for j in range(ROWS):
        row = []
        for i in range(COLS):
            # normalised screen coords, y down
            x = (i + 0.5 - COLS / 2) * CELL_ASPECT / (ROWS / 2)
            y = (j + 0.5 - ROWS / 2) / (ROWS / 2)
            val = None
            depth = -9.0

            # --- sphere
            d2 = x * x + y * y
            if d2 <= R * R:
                z = math.sqrt(R * R - d2)
                nx, ny, nz = x / R, y / R, z / R
                diff = max(0.0, nx * lx + ny * ly + nz * lz)
                hx, hy, hz = _norm((lx, ly, lz + 1))
                spec = max(0.0, nx * hx + ny * hy + nz * hz) ** 24
                shade = 0.10 + 0.78 * diff + 0.6 * spec
                # wireframe: rotate the normal a little so the grid is not
                # perfectly face-on, then carve latitude/longitude lines
                gx, gy = _rot_z(nx, ny, math.radians(14))
                lat = math.asin(max(-1, min(1, gy)))
                lon = math.atan2(gx, nz)
                on_lat = abs(lat / math.radians(30) - round(lat / math.radians(30))) < 0.07
                on_lon = abs(lon / math.radians(36) - round(lon / math.radians(36))) < 0.05 / max(0.35, nz)
                if on_lat or on_lon:
                    shade *= 0.55
                val, depth = shade, z

            # --- ring: plane through the origin, inclined and tilted.
            # Un-tilt the screen point, then solve for where the view ray
            # meets the inclined plane.
            ux, uy = _rot_z(x, y, -TILT)
            cos_i, sin_i = math.cos(RING_INCL), math.sin(RING_INCL)
            # plane: y' = uy, satisfies uy = py*cos_i, z = py*sin_i
            py = uy / cos_i
            pz = py * sin_i
            rr = math.sqrt(ux * ux + py * py)
            if ring_r0 <= rr <= ring_r1 and pz > depth - 1e-9:
                # the half of the ring nearer the viewer wins over the sphere
                band = (rr - ring_r0) / (ring_r1 - ring_r0)
                shade = 0.35 + 0.45 * (1 - abs(band - 0.5) * 2) + (0.15 if pz > 0 else -0.12)
                if abs(band - 0.5) < 0.12:
                    shade *= 0.55   # Cassini-style gap
                val, depth = shade, pz

            if val is None:
                row.append(" ")
            else:
                k = min(len(ramp) - 1, max(1, int(round(val * (len(ramp) - 1)))))
                row.append(ramp[k])
        out.append("".join(row).rstrip())
    return out


# A sparse field of "stars", fixed positions so every build is identical.
STARS = [(4, 2, "."), (63, 1, "+"), (68, 10, "."), (2, 21, "+"), (7, 31, "."),
         (60, 31, "."), (69, 25, "+"), (16, 5, "."), (55, 29, "."), (36, 0, ".")]


def art(invert: bool = False) -> list[str]:
    lines = [l.ljust(COLS) for l in render(invert)]
    for x, y, ch in STARS:
        if lines[y][x] == " ":
            lines[y] = lines[y][:x] + ch + lines[y][x + 1:]
    return [l.rstrip() for l in lines]


if __name__ == "__main__":
    print("\n".join(art()))
