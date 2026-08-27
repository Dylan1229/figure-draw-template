"""Annotations that state the *claim*, not just the data.

A bar chart shows two numbers. `speedup()` shows the sentence "we are 2.4x
faster", which is the thing the reviewer is actually looking for. Every
annotator here draws a connector between two data points and labels the ratio
between them, so the figure argues instead of merely reporting.

All positions are in **data coordinates**. Set your axis limits (or call
`headroom()`) *before* annotating: the curved connectors size themselves from
the current limits.
"""

from __future__ import annotations

from typing import Iterable, Sequence

import matplotlib.patches as mpatches
import matplotlib.pyplot as plt
import numpy as np

from .palette import RICE, text_on
from .style import REL, rel_fontsize

_CALLOUT = RICE["ablation"]


# --------------------------------------------------------------------------
# axis prep
# --------------------------------------------------------------------------

def headroom(ax, frac: float = 0.30, axis: str = "y", floor_at_zero: bool = True) -> None:
    """Grow the axis so value labels and connectors have room.

    Bars that touch the top of the panel look cramped and leave nowhere for a
    speedup arc. 0.30-0.40 is right when you annotate above bars; 0.15 when you
    only label inside them.
    """
    if axis == "y":
        lo, hi = ax.get_ylim()
        ax.set_ylim(0 if floor_at_zero else lo, hi * (1 + frac))
    else:
        lo, hi = ax.get_xlim()
        ax.set_xlim(0 if floor_at_zero else lo, hi * (1 + frac))


def panel_titles(axes: Iterable, titles: Sequence[str], letters: bool = True,
                 start: str = "a", **kwargs) -> None:
    """Title each axis, optionally prefixed `(a) `, `(b) `, ...

    Panel letters are what captions cite ("Figure 4(b) shows ..."). Add them
    from the start; retrofitting them means editing the caption too.
    """
    o = ord(start)
    for i, (ax, title) in enumerate(zip(axes, titles)):
        text = f"({chr(o + i)}) {title}" if letters else title
        ax.set_title(text, fontweight="bold", **kwargs)


# --------------------------------------------------------------------------
# value labels
# --------------------------------------------------------------------------

def bar_labels(ax, bars, fmt: str = "{:g}", where: str = "outside",
               fontsize: int | None = None, color: str | None = None,
               pad: float = 3.0, horizontal: bool = False,
               shift: tuple[float, float] | None = None, ha: str | None = None,
               va: str | None = None, **kwargs) -> None:
    """Print each bar's value.

    Args:
        bars: A `BarContainer` (what `ax.bar`/`ax.barh` returns) or a list of them.
        where: `"outside"` above/right of the bar, `"inside"` within it (white
            text on the fill), or `"mid"` centered in the bar.
        horizontal: True for `barh`.
        shift: Extra `(dx, dy)` offset in points, on top of `pad`. Use it with
            `ha="left"` to slide a label out from under an arrowhead that lands
            on the same bar (see `examples/01_grouped_bar_speedup.py`).
        ha / va: Override the automatic alignment.

    `"inside"` is the trick that keeps wide-and-short figures compact: the
    label costs no vertical space and cannot collide with a connector.
    """
    fontsize = fontsize or rel_fontsize(REL["value"])
    for bar in bars:
        value = bar.get_width() if horizontal else bar.get_height()
        cx = bar.get_x() + bar.get_width() / 2
        cy = bar.get_y() + bar.get_height() / 2
        auto = text_on(bar.get_facecolor()) if where in ("inside", "mid") else "black"
        col = color or auto
        if horizontal:
            if where == "outside":
                xy, off, _ha, _va = (value, cy), (pad, 0), "left", "center"
            elif where == "inside":
                xy, off, _ha, _va = (value, cy), (-pad - 1, 0), "right", "center"
            else:
                xy, off, _ha, _va = (value / 2, cy), (0, 0), "center", "center"
        else:
            if where == "outside":
                xy, off, _ha, _va = (cx, value), (0, pad), "center", "bottom"
            elif where == "inside":
                xy, off, _ha, _va = (cx, value), (0, -pad - 1), "center", "top"
            else:
                xy, off, _ha, _va = (cx, value / 2), (0, 0), "center", "center"
        if shift is not None:
            off = (off[0] + shift[0], off[1] + shift[1])
        ax.annotate(fmt.format(value), xy, xytext=off, textcoords="offset points",
                    ha=ha or _ha, va=va or _va, fontsize=fontsize,
                    fontweight="bold", color=col, **kwargs)


# --------------------------------------------------------------------------
# speedup / ratio connectors
# --------------------------------------------------------------------------

def _bezier(p0, pc, p1, n: int = 64) -> np.ndarray:
    t = np.linspace(0.0, 1.0, n)[:, None]
    p0, pc, p1 = (np.asarray(p, dtype=float) for p in (p0, pc, p1))
    return (1 - t) ** 2 * p0 + 2 * (1 - t) * t * pc + t ** 2 * p1


def speedup(ax, src, dst, *, fmt: str = "{:.2f}x", label: str | None = None,
            style: str = "arc", bulge: str = "up", bulge_frac: float = 0.10,
            color: str = _CALLOUT, lw: float = 1.7, fontsize: int | None = None,
            label_offset: tuple[float, float] = (0, 3), invert: bool = False,
            boxed: bool = False) -> float:
    """Connect two data points and label how much better `dst` is than `src`.

    Args:
        src: `(x, y)` of the slower/worse point, e.g. the top of a baseline bar.
        dst: `(x, y)` of the faster/better point.
        fmt: Format for the ratio. Use `"{:.2f}x"`; write the multiplication
            sign as a literal U+00D7 if you prefer (`"{:.2f}×"`).
        style: `"arc"` (curved, the default -- it never runs through a bar),
            `"bracket"` (L-shaped: across then down, for adjacent paired bars),
            or `"straight"`.
        bulge: Which way an `"arc"` bows: `"up"` for vertical bars,
            `"right"` for horizontal bars.
        bulge_frac: Bow height as a fraction of the axis range. Raise it if the
            arc clips a tall bar between the two endpoints.
        invert: Report `dst/src` instead of `src/dst` (use for "higher is
            better" metrics such as throughput).
        boxed: Put the label on a white pill. Use when it lands over data.

    Returns:
        The ratio that was drawn, so you can assert on it or reuse it in text.
    """
    fontsize = fontsize or rel_fontsize(REL["callout"])
    (x0, y0), (x1, y1) = src, dst
    a, b = (y0, y1) if bulge == "up" else (x0, x1)
    ratio = (b / a) if invert else (a / b)
    text = label if label is not None else fmt.format(ratio)

    if style == "bracket":
        # across at the source level, then a short arrow down onto the target.
        ax.plot([x0, x1], [y0, y0], color=color, lw=lw * 0.7, solid_capstyle="butt")
        ax.annotate("", xy=(x1, y1), xytext=(x1, y0),
                    arrowprops=dict(arrowstyle="-|>", color=color, lw=lw))
        anchor, ha, va = (x1, y0), "left", "bottom"
        off = (5, 3)
    elif style == "straight":
        ax.annotate("", xy=(x1, y1), xytext=(x0, y0),
                    arrowprops=dict(arrowstyle="-|>", color=color, lw=lw))
        anchor, ha, va = ((x0 + x1) / 2, (y0 + y1) / 2), "center", "bottom"
        off = label_offset
    else:  # arc
        if bulge == "up":
            span = abs(np.diff(ax.get_ylim())[0])
            ctrl = ((x0 + x1) / 2, max(y0, y1) + span * bulge_frac)
            ha, va, off = "center", "bottom", label_offset
        else:  # bulge right, for horizontal bars
            span = abs(np.diff(ax.get_xlim())[0])
            ctrl = (max(x0, x1) + span * bulge_frac, (y0 + y1) / 2)
            ha, va, off = "left", "center", (4, 0)
        pts = _bezier(src, ctrl, dst)
        ax.plot(pts[:, 0], pts[:, 1], color=color, lw=lw, solid_capstyle="round")
        ax.annotate("", xy=(x1, y1), xytext=(pts[-6, 0], pts[-6, 1]),
                    arrowprops=dict(arrowstyle="-|>", color=color, lw=lw))
        anchor = ctrl

    bbox = dict(boxstyle="round,pad=0.18", fc="white", ec="none", alpha=0.85) if boxed else None
    ax.annotate(text, anchor, xytext=off, textcoords="offset points",
                ha=ha, va=va, fontsize=fontsize, fontweight="bold", color=color,
                bbox=bbox)
    return ratio


def speedup_between_bars(ax, bars, i: int, j: int, *, horizontal: bool = False,
                         **kwargs) -> float:
    """`speedup()` addressed by bar index instead of coordinates.

    Saves you from recomputing bar centers::

        bars = ax.bar(x, values, ...)
        fk.speedup_between_bars(ax, bars, 0, 2)   # bar 0 -> bar 2
    """
    def point(k):
        bar = bars[k]
        if horizontal:
            return (bar.get_width(), bar.get_y() + bar.get_height() / 2)
        return (bar.get_x() + bar.get_width() / 2, bar.get_height())

    kwargs.setdefault("bulge", "right" if horizontal else "up")
    return speedup(ax, point(i), point(j), **kwargs)


def cascade(ax, values: Sequence[float], *, horizontal: bool = True,
            positions: Sequence[float] | None = None, fmt: str = "{:.2f}x",
            color: str = "#555555", label_color: str = _CALLOUT,
            rad: float = -0.45, lw: float = 2.0, fontsize: int | None = None,
            label_pad: float = 0.03, boxed: bool = True) -> list[float]:
    """Chain of arcs down a ladder of cumulative improvements.

    The canonical "technique breakdown" figure: baseline at the top, one bar
    per technique added, an arc from each bar to the next labelled with the
    incremental gain. Assumes `values` is ordered from worst to best and that
    the bars were drawn reversed (worst on top) -- which is what
    `figkit.charts.hbar(order="top_down")` does.

    Args:
        values: Ordered worst -> best.
        rad: Arc curvature. Negative bows away from the bars.
        label_pad: Where the ratio label sits, as a fraction of the value axis
            past the end of the longer of the two bars -- i.e. always in the
            whitespace to the right, never on top of a bar or its value label.
            This needs ~20% headroom on that axis; see `headroom()`.

    Returns:
        The per-step ratios.
    """
    fontsize = fontsize or rel_fontsize(REL["callout"])
    n = len(values)
    pos = list(positions) if positions is not None else [n - 1 - i for i in range(n)]
    ratios: list[float] = []
    for i in range(n - 1):
        v0, v1 = values[i], values[i + 1]
        p0, p1 = pos[i], pos[i + 1]
        start = (v0, p0) if horizontal else (p0, v0)
        end = (v1, p1) if horizontal else (p1, v1)
        ax.add_patch(mpatches.FancyArrowPatch(
            start, end, connectionstyle=f"arc3,rad={rad}", color=color,
            arrowstyle="->", mutation_scale=16, lw=lw))
        ratios.append(v0 / v1)
        vrange = abs(np.diff(ax.get_xlim() if horizontal else ax.get_ylim())[0])
        tx = max(v0, v1) + label_pad * vrange
        ty = p1 + 0.32
        bbox = dict(boxstyle="round,pad=0.2", fc="white", ec="none", alpha=0.85) if boxed else None
        ax.text(*( (tx, ty) if horizontal else (ty, tx) ), fmt.format(ratios[-1]),
                ha="center", va="center", fontsize=fontsize, fontweight="bold",
                color=label_color, bbox=bbox)
    return ratios


def total_arrow(ax, start: float, end: float, offset: float, *,
                label: str | None = None, fmt: str = "Total: {:.2f}x",
                horizontal: bool = True, color: str = _CALLOUT,
                lw: float = 2.2, fontsize: int | None = None) -> float:
    """A single arrow summarising the whole cascade, drawn outside the bars.

    Args:
        start / end: First and last value of the cascade.
        offset: Position on the *category* axis, outside the bars
            (e.g. `-0.62` to sit just below the bottom bar).
    """
    fontsize = fontsize or rel_fontsize(REL["callout"])
    ratio = start / end
    p_from = (start, offset) if horizontal else (offset, start)
    p_to = (end, offset) if horizontal else (offset, end)
    ax.annotate(label or fmt.format(ratio), xy=p_to, xytext=p_from,
                arrowprops=dict(arrowstyle="-|>", color=color, lw=lw),
                ha="center", va="center", fontsize=fontsize, fontweight="bold",
                color=color, bbox=dict(boxstyle="square,pad=0.3", fc="white", ec="none"))
    return ratio


def reference_line(ax, value: float, *, horizontal: bool = True,
                   label: str | None = None, color: str = "gray",
                   ls: str = "--", lw: float = 1.3, alpha: float = 0.5) -> None:
    """Dashed baseline marker, so "how far from the baseline" is readable at a glance."""
    line = ax.axvline if horizontal else ax.axhline
    line(value, color=color, ls=ls, lw=lw, alpha=alpha)
    if label:
        lo, hi = (ax.get_ylim() if horizontal else ax.get_xlim())
        at = hi - (hi - lo) * 0.04
        pos = (value, at) if horizontal else (at, value)
        ax.annotate(label, pos, xytext=(4, 0), textcoords="offset points",
                    fontsize=rel_fontsize(REL["value"]),
                    color=color, fontweight="bold", va="top")


def legend_below(fig, handles=None, labels=None, *, ncol: int = 3,
                 y: float = -0.02, **kwargs):
    """Shared legend under the whole figure.

    In a multi-panel figure a per-axis legend repeats itself and steals plot
    area. One legend below the panels reads once and applies to all of them.
    """
    kwargs.setdefault("frameon", False)
    kwargs.setdefault("prop", {"weight": "bold"})
    if handles is None:
        handles, labels = fig.axes[0].get_legend_handles_labels()
    return fig.legend(handles=handles, labels=labels, loc="lower center",
                      bbox_to_anchor=(0.5, y), ncol=ncol, **kwargs)


def patch_handles(colors: Sequence[str], labels: Sequence[str],
                  edgecolor: str = "black", **kwargs) -> list:
    """Build legend handles by hand, for legends that no artist owns."""
    return [mpatches.Patch(facecolor=c, edgecolor=edgecolor, label=l, **kwargs)
            for c, l in zip(colors, labels)]
