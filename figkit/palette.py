"""Semantic color palettes.

The golden rule of this template: **a color means a role, not a series index.**
If "ours" is deep blue in Figure 3, it must be deep blue in Figure 11 too.
Reviewers learn the mapping once and then read every later figure faster.
"""

from __future__ import annotations

from typing import Final

import matplotlib.colors as mcolors

# --------------------------------------------------------------------------
# Primary semantic palette (the "RICE" scheme used across our papers).
# Pick colors by ROLE, never by "the next color in the list".
# --------------------------------------------------------------------------
RICE: Final[dict[str, str]] = {
    "ours":           "#0A509E",  # deep blue    - the proposed system / full method
    "best_baseline":  "#E0A494",  # warm salmon  - strongest competing baseline
    "other_baseline": "#7C7E7F",  # neutral gray - weaker / origin / "w/o X"
    "ablation":       "#C04829",  # brick red    - ablation variant, 2nd model, deltas
    "highlight":      "#E9A139",  # amber gold   - callouts (speedups, annotations)
}

# Convenience aliases so scripts read like prose: C.ours, C.ablation, ...
class _Roles:
    ours = RICE["ours"]
    best_baseline = RICE["best_baseline"]
    other_baseline = RICE["other_baseline"]
    ablation = RICE["ablation"]
    highlight = RICE["highlight"]
    # extra roles for figures that genuinely need > 5 series
    teal = "#42949E"
    violet = "#9A4D8E"
    ink = "#333333"
    white = "#FFFFFF"

C: Final[_Roles] = _Roles()

# --------------------------------------------------------------------------
# Extended palette, kept for figures that need more hues (composition
# breakdowns, many-method comparisons). Still grouped by intent.
# --------------------------------------------------------------------------
PALETTE: Final[dict[str, str]] = {
    "blue_main":      "#0F4D92",
    "blue_secondary": "#3775BA",
    "green_1":        "#DDF3DE",
    "green_2":        "#AADCA9",
    "green_3":        "#8BCF8B",
    "red_1":          "#F6CFCB",
    "red_2":          "#E9A6A1",
    "red_strong":     "#B64342",
    "neutral":        "#CFCECE",
    "gray_mid":       "#767676",
    "gray_dark":      "#4D4D4D",
    "highlight":      "#FFD700",
    "teal":           "#42949E",
    "violet":         "#9A4D8E",
}

#: Default cycle when you have unnamed series. Ordered so the first color is
#: always "ours" — if that is wrong for your figure, pass colors explicitly.
DEFAULT_COLORS: Final[list[str]] = [
    RICE["ours"], RICE["best_baseline"], RICE["other_baseline"],
    RICE["ablation"], RICE["highlight"], PALETTE["teal"], PALETTE["violet"],
]

#: Ordered ramp for "more of the same thing" (e.g. 1/2/4/8 GPUs).
#: Same hue, increasing saturation — reads as a magnitude, not as categories.
ORDINAL_BLUE: Final[list[str]] = ["#CBDCEF", "#8FB4DA", "#4E82BE", "#0A509E", "#06356A"]


def sequential_cmap(color: str, start: str = "#FFFFFF", name: str = "seq"):
    """White -> `color` colormap. Use for heatmaps of a single quantity.

    Keeping the low end white means "small value" is visually empty, which is
    what readers expect, and it keeps in-cell black text legible.
    """
    return mcolors.LinearSegmentedColormap.from_list(name, [start, color])


def diverging_cmap(low: str = RICE["ours"], mid: str = "#FFFFFF",
                   high: str = RICE["ablation"], name: str = "div"):
    """low -> white -> high. Use only when the data has a meaningful zero."""
    return mcolors.LinearSegmentedColormap.from_list(name, [low, mid, high])


def shades(color: str, n: int, low: float = 0.25, high: float = 1.0) -> list[str]:
    """`n` tints of one color, light to dark.

    The house convention for ablations: keep the hue (it still means "ours"),
    vary the lightness to signal how complete the variant is. Unlike `alpha`,
    these are solid colors, so they stay correct when bars overlap gridlines.
    """
    r, g, b = mcolors.to_rgb(color)
    out: list[str] = []
    for i in range(n):
        t = low + (high - low) * (i / max(n - 1, 1))
        out.append(mcolors.to_hex(((1 - t) + t * r,
                                   (1 - t) + t * g,
                                   (1 - t) + t * b)))
    return out


def text_on(color: str, threshold: float = 0.55) -> str:
    """Return 'white' or a dark ink color, whichever is readable on `color`.

    Used for in-bar / in-cell value labels so you never hand-pick text colors.
    """
    r, g, b = mcolors.to_rgb(color)
    luminance = 0.2126 * r + 0.7152 * g + 0.0722 * b
    return "#333333" if luminance > threshold else "white"
