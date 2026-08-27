"""How big will this actually be on the printed page?

The single most common figure bug in systems papers: you draw a beautiful
12-inch-wide panel with 18pt labels, LaTeX shrinks it into a 3.3-inch column,
and the reviewer is reading 5pt text on paper.

    effective_pt = font_size * (page_width_in / fig_width_in)

`figkit.io.save()` prints this number for every figure it writes, and warns
when it drops below `MIN_READABLE_PT`.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Final

#: Printable widths in inches. Measure yours with `\the\columnwidth` /
#: `\the\textwidth` in LaTeX (divide the pt value by 72.27) if in doubt.
LAYOUTS: Final[dict[str, float]] = {
    "acm-sigplan-col":  3.33,   # acmart [sigplan] one column (PPoPP, PLDI, ASPLOS)
    "acm-sigplan-text": 7.00,   # acmart [sigplan] full width (figure*)
    "acm-sigconf-col":  3.33,
    "acm-sigconf-text": 7.00,
    "ieee-col":         3.50,   # IEEEtran two-column
    "ieee-text":        7.16,
    "usenix-col":       3.30,
    "usenix-text":      7.00,
    "neurips":          5.50,   # single-column ML venues
    "icml":             6.75,
    "a4-single":        6.30,
    "slide-16x9":      13.33,
}

#: Below this, text is uncomfortable in print. Venues rarely hard-enforce it,
#: reviewers always notice it.
MIN_READABLE_PT: Final[float] = 6.0
#: What to aim for in a camera-ready.
GOOD_PT: Final[float] = 7.5

_DEFAULT_LAYOUT = "acm-sigplan-col"


def set_layout(name: str) -> None:
    """Set the layout that `save()` reports against, once per project."""
    global _DEFAULT_LAYOUT
    if name not in LAYOUTS:
        raise ValueError(f"Unknown layout {name!r}. Available: {sorted(LAYOUTS)}")
    _DEFAULT_LAYOUT = name


def get_layout() -> str:
    return _DEFAULT_LAYOUT


def page_width(layout: str | float | None = None, frac: float = 1.0) -> float:
    """Printed width in inches for a layout name (or a raw inch value)."""
    if isinstance(layout, (int, float)):
        return float(layout) * frac
    return LAYOUTS[layout or _DEFAULT_LAYOUT] * frac


def effective_pt(font_size: float, fig_width_in: float,
                 layout: str | float | None = None, frac: float = 1.0) -> float:
    """Point size the reader actually sees.

    Args:
        font_size: The rcParam font size used to draw.
        fig_width_in: `figsize[0]` of the canvas.
        layout: Layout key or explicit printed width in inches.
        frac: The `width=` fraction in `\\includegraphics` (0.9 for
            `width=0.9\\linewidth`).
    """
    return font_size * page_width(layout, frac) / fig_width_in


def font_size_for(target_pt: float, fig_width_in: float,
                  layout: str | float | None = None, frac: float = 1.0) -> float:
    """Inverse of `effective_pt`: the rcParam size that prints at `target_pt`.

    Example:
        >>> round(font_size_for(8.0, fig_width_in=12, layout="acm-sigplan-text"))
        14
    """
    return target_pt * fig_width_in / page_width(layout, frac)


def figsize(width_in: float, aspect: float = 0.30) -> tuple[float, float]:
    """`(w, h)` with height as a fraction of width.

    Wide-and-short (aspect 0.25-0.35) is the workhorse shape for paper
    figures: it fills a column without eating vertical space you need for text.
    """
    return (width_in, width_in * aspect)


def report(font_size: float, fig_width_in: float,
           layout: str | float | None = None, frac: float = 1.0) -> str:
    """One-line human-readable readability verdict."""
    pt = effective_pt(font_size, fig_width_in, layout, frac)
    lay = layout if isinstance(layout, str) else (layout or _DEFAULT_LAYOUT)
    scale = page_width(layout, frac) / fig_width_in
    verdict = "ok" if pt >= GOOD_PT else ("tight" if pt >= MIN_READABLE_PT else "TOO SMALL")
    return (f"{font_size:g}pt on a {fig_width_in:g}in canvas -> {pt:.1f}pt "
            f"at {frac:g}x{lay} (scale {scale:.2f}) [{verdict}]")


# --------------------------------------------------------------------------
# Planning a canvas backwards from the printed page
# --------------------------------------------------------------------------

@dataclass(frozen=True)
class Plan:
    """A canvas sized so its text lands at a chosen point size on the page.

    Attributes:
        figsize: Pass straight to `plt.subplots(figsize=...)`.
        font_size: Pass to `FigureStyle(font_size=...)`.
        layout / frac: Remembered so `save()` can report against them.
    """

    figsize: tuple[float, float]
    font_size: float
    layout: str
    frac: float
    target_pt: float

    def __str__(self) -> str:
        return report(self.font_size, self.figsize[0], self.layout, self.frac)


def plan(layout: str = "acm-sigplan-col", *, aspect: float = 0.35,
         target_pt: float = 8.0, oversample: float = 2.0,
         frac: float = 1.0, round_font: bool = True) -> Plan:
    """Work backwards from "I want 8pt text in a 3.33in column".

    Args:
        layout: Where the figure will land. See `LAYOUTS`. Use the `-text`
            variant for a `figure*` that spans both columns.
        aspect: height / width of the canvas. 0.25-0.35 for a wide eval strip,
            0.55-0.75 for a single square-ish panel.
        target_pt: Point size the reader sees. 8 is comfortable, 7 is the floor
            for a camera-ready, 9+ for a figure that carries the whole story.
        oversample: How much bigger than the printed size to draw. Only affects
            the numbers you type; the on-page result is identical. 2.0 keeps
            figsize/linewidths in familiar ranges.
        frac: The `width=` fraction you will use in `\\includegraphics`.

    Example:
        >>> p = plan("acm-sigplan-text", aspect=0.27, target_pt=8.5)
        >>> print(p)                                    # doctest: +SKIP
        17pt on a 14in canvas -> 8.5pt at 1xacm-sigplan-text (scale 0.50) [ok]
    """
    width = page_width(layout, frac) * oversample
    size = target_pt * oversample
    if round_font:
        size = round(size)
    return Plan(figsize=(round(width, 2), round(width * aspect, 2)),
                font_size=size, layout=layout, frac=frac, target_pt=target_pt)
