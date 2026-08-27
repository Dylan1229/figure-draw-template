"""figkit -- a small, opinionated layer over matplotlib for paper figures.

    import figkit as fk

    fk.apply_style("paper")
    fig, ax = plt.subplots(figsize=fk.figsize(9, 0.32))
    fk.grouped_bar(ax, ["2K", "4K"], [baseline, ours], ["Baseline", "Ours"],
                   colors=[fk.C.other_baseline, fk.C.ours])
    fk.headroom(ax, 0.35)
    fk.speedup(ax, (0 - 0.18, baseline[0]), (0 + 0.18, ours[0]))
    fk.save(fig, "e2e_latency")

Four ideas, and that is the whole library:
  1. Color means a role (`fk.C.ours` is always the same blue).
  2. Style is global and set once (`fk.apply_style`).
  3. Annotate the claim, not the data (`fk.speedup`, `fk.cascade`).
  4. Know how small it prints (`fk.save` tells you; `figkit.sizing` explains).
"""

from __future__ import annotations

from .annotate import (
    bar_labels,
    cascade,
    headroom,
    legend_below,
    panel_titles,
    patch_handles,
    reference_line,
    speedup,
    speedup_between_bars,
    total_arrow,
)
from .charts import (
    grouped_bar,
    hbar,
    heatmap,
    mirror_bars,
    paired_bar,
    scaling_lines,
    side_table,
    stacked_hbar,
)
from .io import finalize_figure, output_dirs, quiet, save, set_output_dir
from .palette import (
    C,
    DEFAULT_COLORS,
    ORDINAL_BLUE,
    PALETTE,
    RICE,
    diverging_cmap,
    sequential_cmap,
    shades,
    text_on,
)
from .sizing import (
    LAYOUTS,
    Plan,
    plan,
    effective_pt,
    figsize,
    font_size_for,
    get_layout,
    page_width,
    report,
    set_layout,
)
from .upstream import find_upstream, load_upstream, upstream_root
from .style import (
    PRESETS,
    REL,
    rel_fontsize,
    FigureStyle,
    apply_publication_style,
    apply_style,
    bold_ticks,
    despine,
    grid,
)

__version__ = "0.1.0"

__all__ = [
    # style
    "FigureStyle", "PRESETS", "apply_style", "apply_publication_style",
    "bold_ticks", "grid", "despine", "REL", "rel_fontsize",
    # palette
    "C", "RICE", "PALETTE", "DEFAULT_COLORS", "ORDINAL_BLUE",
    "sequential_cmap", "diverging_cmap", "shades", "text_on",
    # sizing
    "LAYOUTS", "Plan", "plan", "figsize", "effective_pt", "font_size_for", "page_width",
    "report", "set_layout", "get_layout",
    # charts
    "grouped_bar", "hbar", "paired_bar", "stacked_hbar", "scaling_lines",
    "heatmap", "mirror_bars", "side_table",
    # annotate
    "bar_labels", "speedup", "speedup_between_bars", "cascade", "total_arrow",
    "headroom", "panel_titles", "legend_below", "patch_handles", "reference_line",
    # io
    "save", "set_output_dir", "output_dirs", "quiet", "finalize_figure",
    # upstream bridge
    "load_upstream", "find_upstream", "upstream_root",
]
