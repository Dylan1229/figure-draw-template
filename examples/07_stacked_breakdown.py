"""Composition breakdown: stacked bars with shares and totals.

CLAIM  "Decode dominates, so that is what we optimized." A motivation figure:
       it justifies the rest of the paper before you present a solution.
USE    Composition of one quantity across a handful of configurations.

DESIGN NOTES
  * Percentages inside the segments, absolute totals at the end of the bar.
    The figure then answers both "what dominates?" and "how big is it?"
    without a second panel.
  * Segments below ~6% are left unlabelled rather than rendered as colliding
    text. `min_pct` controls the cutoff.
  * White separators between segments instead of black outlines -- at this
    density black edges become the dominant visual texture.
  * The legend goes on top, horizontally: the reading order is
    legend -> bars, matching how a reader parses a stacked chart.
"""
import sys, pathlib; sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1]))

import matplotlib.pyplot as plt

import figkit as fk

META = {
    "title": "7. Stacked breakdown",
    "claim": '"Decode dominates, so that is what we optimized."',
    "use": "composition of one quantity across configurations",
    "helpers": "`stacked_hbar`",
    "notes": ("Percentages inside the segments, absolute totals at the end of the "
              "bar: answers \"what dominates?\" and \"how big is it?\" in one panel. "
              "A motivation figure -- it justifies the rest of the paper before you "
              "present a solution."),
}

# >>> data
CONFIGS   = ["4K tok\n(1 GPU)", "4K tok\n(4 GPUs)",
             "16K tok\n(1 GPU)", "16K tok\n(4 GPUs)"]
PARTS     = ["Prefill", "Transfer", "Decode"]
BREAKDOWN = [[168, 19, 121],       # seconds per part, one row per config
             [ 62, 19, 121],
             [168, 52, 437],
             [ 62, 52, 437]]
# <<< data

COLORS = [fk.C.best_baseline, fk.C.highlight, fk.C.ours]


def main() -> None:
    p = fk.plan("acm-sigplan-text", aspect=0.25, target_pt=8.0)
    fk.apply_style(fk.FigureStyle(font_size=p.font_size, axes_linewidth=1.4))
    fig, ax = plt.subplots(figsize=p.figsize)

    fk.stacked_hbar(ax, CONFIGS, BREAKDOWN, PARTS, colors=COLORS,
                    xlabel="Latency (s)", show_pct=True, min_pct=6.0,
                    show_totals=True, total_fmt="{:.0f} s")
    ax.legend(loc="upper center", bbox_to_anchor=(0.45, 1.18), ncol=3,
              frameon=False, handlelength=1.5, prop={"weight": "bold"})

    fk.save(fig, "07_stacked_breakdown", plan=p)


if __name__ == "__main__":
    main()
