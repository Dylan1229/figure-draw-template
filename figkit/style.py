"""Global matplotlib style: one call, applied before you draw anything.

House style, in one paragraph: sans-serif, bold labels, no top/right spines,
frameless legends, dashed low-alpha grid *behind* the data, black bar edges,
and vector PDF output with Type-42 fonts. Everything else is per-figure.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Final

import matplotlib.pyplot as plt


@dataclass(frozen=True)
class FigureStyle:
    """Knobs you actually change per figure.

    Attributes:
        font_size: Base font size *in the rendered canvas*, not on the printed
            page. See `figkit.sizing` — what the reviewer sees is
            ``font_size * (page_width / fig_width)``.
        axes_linewidth: Spine width. 1.4-1.8 for compact paper figures,
            2.5-3 for large slide/poster panels.
        bold_text: House default. Bold survives the down-scaling that a
            12-inch canvas goes through to fit a 3.3-inch column.
        use_tex: Only turn on if you need real math typography *and* have a
            working LaTeX install. It roughly triples render time.
        font_family: First available wins. Add "Times New Roman"/"Nimbus Roman"
            first if your venue is serif-heavy and you want figures to match.
        grid_alpha: Gridlines should be visible but never compete with data.
    """

    font_size: int = 16
    axes_linewidth: float = 1.6
    bold_text: bool = True
    use_tex: bool = False
    font_family: tuple[str, ...] = ("DejaVu Sans", "Helvetica", "Arial", "sans-serif")
    grid_alpha: float = 0.35


#: Ready-made starting points. Copy and tweak rather than inventing new ones.
PRESETS: Final[dict[str, FigureStyle]] = {
    # Wide-and-short panel that will be shrunk into a two-column paper.
    "paper": FigureStyle(font_size=17, axes_linewidth=1.6),
    # Denser figure (heatmaps, tables-in-figures) where 17pt would collide.
    "paper_dense": FigureStyle(font_size=13, axes_linewidth=1.3),
    # Big single panel for a talk; drawn at slide scale, no down-scaling.
    "slide": FigureStyle(font_size=24, axes_linewidth=3.0),
    # Serif to match a serif paper body.
    "serif": FigureStyle(font_size=17, axes_linewidth=1.6,
                         font_family=("Nimbus Roman", "Times New Roman",
                                      "DejaVu Serif", "serif")),
}


def apply_style(style: FigureStyle | str | None = None) -> FigureStyle:
    """Set global rcParams. Call once, at the top of every figure function.

    Args:
        style: A `FigureStyle`, a key of `PRESETS`, or None for the default.

    Returns:
        The `FigureStyle` that was applied (handy for logging / sizing checks).

    Note:
        rcParams are global and sticky. Because one script usually builds
        several figures with different densities, each figure function should
        call this itself instead of relying on a module-level call.
    """
    if isinstance(style, str):
        try:
            s = PRESETS[style]
        except KeyError:
            raise ValueError(
                f"Unknown preset {style!r}. Available: {sorted(PRESETS)}") from None
    else:
        s = style or FigureStyle()

    weight = "bold" if s.bold_text else "normal"
    plt.rcParams.update({
        "text.usetex": s.use_tex,
        "font.family": "serif" if "serif" in s.font_family[-1] else "sans-serif",
        "font.sans-serif": list(s.font_family),
        "font.serif": list(s.font_family),
        "font.size": s.font_size,
        "font.weight": weight,
        "axes.labelsize": s.font_size,
        "axes.labelweight": weight,
        "axes.titlesize": s.font_size + 1,
        "axes.titleweight": weight,
        "axes.linewidth": s.axes_linewidth,
        "axes.spines.right": False,
        "axes.spines.top": False,
        "axes.grid": False,          # opt in per axis; see figkit.charts
        "axes.axisbelow": True,      # grid never draws on top of bars
        "grid.linestyle": "--",
        "grid.alpha": s.grid_alpha,
        "grid.linewidth": 0.8,
        "legend.frameon": False,
        "legend.fontsize": s.font_size - 2,
        "legend.handlelength": 1.6,
        "legend.columnspacing": 1.2,
        "xtick.direction": "out",
        "ytick.direction": "out",
        "xtick.labelsize": s.font_size - 1,
        "ytick.labelsize": s.font_size - 1,
        "figure.dpi": 120,           # on-screen preview only
        "savefig.bbox": "tight",
        "savefig.transparent": False,
        "svg.fonttype": "none",      # keep text editable in Illustrator/Inkscape
        "pdf.fonttype": 42,          # TrueType, not Type-3: required by ACM/IEEE
        "ps.fonttype": 42,
    })
    return s


#: Backwards-compatible alias for scripts ported from `scientific_figure_pro`.
apply_publication_style = apply_style


def rel_fontsize(factor: float, floor: float = 5.0) -> float:
    """A font size relative to the current base size.

    Every secondary label in figkit (bar values, speedup callouts, heatmap
    cells) is sized as a *fraction of the base font* rather than an absolute
    number. Change `FigureStyle(font_size=...)` once and the whole figure
    rescales without any label silently becoming unreadable.
    """
    return max(plt.rcParams["font.size"] * factor, floor)


#: Named factors, so a figure's internal type hierarchy stays consistent.
REL: Final[dict[str, float]] = {
    "value": 0.78,     # numbers printed on/next to bars
    "callout": 0.86,   # speedup labels, deltas -- the point of the figure
    "tick": 0.95,
    "cell": 0.62,      # heatmap cells (many, small, dense)
    "table": 0.72,
}


def bold_ticks(*axes) -> None:
    """Force bold tick labels on the given axes.

    `font.weight` covers most text, but tick labels created before the rcParam
    took effect (or by helpers that set their own weight) can slip through.
    Cheap to call, idempotent.
    """
    for ax in axes:
        for label in list(ax.get_xticklabels()) + list(ax.get_yticklabels()):
            label.set_fontweight("bold")


def grid(ax, axis: str = "y", alpha: float | None = None, ls: str = "--") -> None:
    """Enable the house grid on one axis only.

    Bars get a horizontal grid (`axis='y'`), horizontal bars get `axis='x'`,
    line plots usually get both. Never a full grid under a bar chart -- the
    vertical lines fight the bars.
    """
    ax.grid(axis=axis, ls=ls, alpha=alpha if alpha is not None else plt.rcParams["grid.alpha"])
    ax.set_axisbelow(True)


def despine(ax, left: bool = False, bottom: bool = False) -> None:
    """Remove extra spines. Top/right are already off via rcParams.

    Drop the left spine on horizontal bar charts where the category labels
    already anchor the reader.
    """
    if left:
        ax.spines["left"].set_visible(False)
    if bottom:
        ax.spines["bottom"].set_visible(False)
