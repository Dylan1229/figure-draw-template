"""Quality/cost trade-off: mirrored bars + a settings table.

CLAIM  "Past 8 shards you buy little latency and pay real accuracy, so 8 is the
        sweet spot." A trade-off figure earns its space by making the *knee*
        visible instead of asking the reader to align two charts.
USE    One knob, two metrics that move in opposite directions.

DESIGN NOTES
  * Accuracy grows upward, latency downward, sharing one x axis. Each half has
    its own value range, chosen deliberately: `up_range`/`down_range` decide
    what "a big difference" looks like, and a too-wide range flattens the
    effect you are arguing for.
  * The y tick labels show the real values on both halves, so nothing about
    the shared axis is a trick. Round range endpoints -> round tick labels.
  * No legend: the rotated axis labels already name the two halves.
  * The configuration detail ("what shard size is #shards=12?") goes in a small
    table pinned beside the panel via `width_ratios` -- it belongs with the
    figure, and it would bloat the caption.
"""
import sys, pathlib; sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1]))

import matplotlib.pyplot as plt
import numpy as np

import figkit as fk

META = {
    "title": "8. Trade-off, mirrored",
    "claim": '"Past 8 shards you pay real accuracy for little speed."',
    "use": "one knob, two metrics moving in opposite directions",
    "helpers": "`mirror_bars` + `side_table`",
    "notes": ("Accuracy up, cost down, one shared x axis, so the *knee* is visible "
              "instead of the reader having to align two charts. The settings table "
              "is pinned beside the panel for the detail that would bloat the "
              "caption."),
}

# >>> data
DATA = {
    "4K tok":  {"shards": [4, 8, 16], "accuracy": [78.42, 77.91, 75.63],
                "latency": [152, 113, 94],
                "shard_size": ["1024x256", "512x256", "256x256"]},
    "16K tok": {"shards": [9, 12, 15, 25], "accuracy": [77.55, 77.02, 76.21, 74.38],
                "latency": [447, 301, 288, 241],
                "shard_size": ["1024x256", "768x256", "1024x154", "614x154"]},
}
BASE_SHARD     = {"4K tok": "2048x512", "16K tok": "3072x768"}
ACCURACY_RANGE = (70, 80)      # round endpoints -> round tick labels
LATENCY_RANGE  = (0, 500)
# <<< data


def main() -> None:
    p = fk.plan("acm-sigplan-text", aspect=0.40, target_pt=8.0, oversample=1.5)
    fk.apply_style(fk.FigureStyle(font_size=p.font_size, axes_linewidth=1.4))
    fig, (ax, ax_table) = plt.subplots(
        1, 2, figsize=p.figsize,
        gridspec_kw={"width_ratios": [4.3, 1.3], "wspace": 0.15})

    # Lay the two workload groups out with a gap between them.
    positions, ticks, group_centers, cursor = [], [], [], 0.0
    for name, d in DATA.items():
        group = np.arange(len(d["shards"])) + cursor
        positions.extend(group)
        ticks.extend(str(t) for t in d["shards"])
        group_centers.append((group[0] + group[-1]) / 2)
        cursor = group[-1] + 2.0

    fk.mirror_bars(
        ax, positions,
        up_values=[q for d in DATA.values() for q in d["accuracy"]],
        down_values=[l for d in DATA.values() for l in d["latency"]],
        up_range=ACCURACY_RANGE, down_range=LATENCY_RANGE,
        up_label="Accuracy (%)", down_label="Latency (s)",
        up_color=fk.C.highlight, down_color=fk.C.ours,
        up_nticks=6, down_nticks=6,
    )
    ax.set_xticks(positions)
    ax.set_xticklabels(ticks, fontweight="bold")
    ax.set_xlabel("Number of Shards", fontweight="bold")

    # Group badges below the downward bars, where nothing else lives.
    span = ACCURACY_RANGE[1] - ACCURACY_RANGE[0]
    for name, cx in zip(DATA, group_centers):
        ax.text(cx, -span * 1.12, name, ha="center", va="center",
                fontweight="bold", fontsize=fk.rel_fontsize(1.0),
                bbox=dict(boxstyle="round,pad=0.25", facecolor="lightgray", alpha=0.8))

    rows, header_rows = [], []
    for name, d in DATA.items():
        header_rows.append(len(rows))
        rows.append([name, BASE_SHARD[name]])
        rows.extend([str(t), s] for t, s in zip(d["shards"], d["shard_size"]))
    fk.side_table(ax_table, rows, ["#Shards", "Shard Size"],
                  title="Shard Settings", header_rows=header_rows,
                  col_widths=[0.45, 0.8])

    fk.save(fig, "08_tradeoff_mirror", plan=p)


if __name__ == "__main__":
    main()
