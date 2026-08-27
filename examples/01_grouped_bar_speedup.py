"""Grouped bars + speedup arcs.

CLAIM  "Our full system is 6.2x faster than the unoptimized baseline, and both
        optimizations pull their weight."
USE    2-4 systems compared across 2-4 settings. The workhorse eval figure.

DESIGN NOTES
  * `fk.plan(...)` sizes the canvas backwards from "8.5pt text in a figure* that
    spans both columns". Never pick figsize and font size independently.
  * Wide and short (aspect 0.27): fills the page width without eating the
    vertical space your text needs.
  * One shared legend below both panels -- a per-panel legend repeats itself
    and steals plot area.
  * The speedup arc bows *upward*, over the bars, so it never crosses data.
    `headroom` / `set_ylim` must come BEFORE `speedup`: the arc sizes its bow
    from the current limits.
  * Collision hygiene: the arrowhead lands exactly where the winning bar's
    value label wants to sit, so that one label is nudged right.
"""
# Makes `figkit` importable without installing anything. Delete if you ran
# `pip install -e .`.
import sys, pathlib; sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1]))

import matplotlib.pyplot as plt

import figkit as fk

META = {
    "title": "1. Grouped bars + speedup arcs",
    "claim": '"Our full system is 6.2x faster than the baseline, and both optimizations pull their weight."',
    "use": "2-4 systems across 2-4 settings",
    "helpers": "`grouped_bar` + `speedup_between_bars`",
    "notes": ("The workhorse end-to-end figure: 2-4 systems across 2-4 settings, "
              "one arc per setting carrying the headline ratio, one shared legend "
              "below both panels."),
}

# Example data. Literals at the top, in the units the axis will show, so anyone
# can check a number against the paper text in five seconds. For a sweep, load
# from ../data/*.json instead -- but keep it out of the plotting code either way.
# >>> data
SETTINGS = ["4K tok", "16K tok"]
VARIANTS = ["Baseline", "+Parallelism", "+Parallelism +Cache"]
MODEL_A  = {"4K tok": [512, 236, 198],  "16K tok": [1840, 611, 297]}   # seconds
MODEL_B  = {"4K tok": [903, 402, 351],  "16K tok": [2760, 1024, 486]}
# <<< data

COLORS = [fk.C.other_baseline, fk.C.best_baseline, fk.C.ours]


def main() -> None:
    p = fk.plan("acm-sigplan-text", aspect=0.27, target_pt=8.5)
    fk.apply_style(fk.FigureStyle(font_size=p.font_size, axes_linewidth=1.6))
    fig, axes = plt.subplots(1, 2, figsize=p.figsize)

    for ax, data, title, ylab in ((axes[0], MODEL_A, "Model-A", True),
                                  (axes[1], MODEL_B, "Model-B", False)):
        series = [[data[s][i] for s in SETTINGS] for i in range(len(VARIANTS))]
        _, bars = fk.grouped_bar(
            ax, SETTINGS, series, labels=VARIANTS, colors=COLORS,
            annotate=None, fmt="{:.0f}",
            ylabel="E2E Latency (s)" if ylab else None,
        )
        # Label every bar, but slide the winning bar's number up-and-right so
        # it clears the speedup arrowhead that lands on the same bar top.
        for k, container in enumerate(bars):
            last = k == len(bars) - 1
            fk.bar_labels(ax, container, fmt="{:.0f}", where="outside",
                          shift=(6, 3) if last else None,
                          ha="left" if last else None)
        ax.set_title(title, fontweight="bold")
        fk.headroom(ax, 0.34)          # room for value labels *and* the arc

        # One arc per setting: worst variant -> best variant.
        for i in range(len(SETTINGS)):
            fk.speedup_between_bars(ax, [bars[0][i], bars[-1][i]], 0, 1,
                                    fmt="{:.1f}x", bulge_frac=0.10)

    fk.legend_below(fig, fk.patch_handles(COLORS, VARIANTS), VARIANTS,
                    ncol=3, y=-0.14)
    fig.subplots_adjust(wspace=0.22)
    fk.save(fig, "01_grouped_bar_speedup", plan=p)


if __name__ == "__main__":
    main()
