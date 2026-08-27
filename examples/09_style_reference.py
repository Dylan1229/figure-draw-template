"""Figure 9 -- The style card: every color and every annotator in one image.

Not a paper figure. Print it, pin it next to your desk, and pick from it
instead of inventing a new color or a new arrow for each new plot.

Run it after changing `figkit/palette.py` to see what you actually changed.
"""
import sys, pathlib; sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1]))

import matplotlib.pyplot as plt
import numpy as np

import figkit as fk

META = {
    "title": "9. Style card",
    "claim": "Not a paper figure: every color role and every annotator in one image.",
    "use": "reference",
    "helpers": "-",
    "notes": ("Not a paper figure: every color role and every annotator in one image "
              "(shown at the top of this README). Regenerate it after editing "
              "`figkit/palette.py` to see what you changed. Print it and pick from it "
              "instead of inventing a color per figure."),
}

ROLES = [
    ("C.ours", fk.C.ours, "proposed system / full method"),
    ("C.best_baseline", fk.C.best_baseline, "strongest competing baseline"),
    ("C.other_baseline", fk.C.other_baseline, "weak baseline / origin / w/o"),
    ("C.ablation", fk.C.ablation, "ablation, 2nd model, deltas"),
    ("C.highlight", fk.C.highlight, "callouts, secondary metric"),
]


def swatches(ax) -> None:
    ax.set_title("Color = role, not series index", fontweight="bold", loc="left")
    for i, (name, color, meaning) in enumerate(ROLES):
        y = len(ROLES) - i
        ax.add_patch(plt.Rectangle((0, y - 0.38), 1.1, 0.76, facecolor=color,
                                   edgecolor="black", lw=0.8))
        ax.text(0.55, y, color.upper(), ha="center", va="center",
                color=fk.text_on(color), fontweight="bold",
                fontsize=fk.rel_fontsize(0.62))
        ax.text(1.3, y + 0.14, name, va="center", fontweight="bold",
                fontsize=fk.rel_fontsize(0.8))
        ax.text(1.3, y - 0.24, meaning, va="center", color="#555555",
                fontsize=fk.rel_fontsize(0.68))
    ramp = fk.shades(fk.C.ours, 5)
    for k, color in enumerate(ramp):
        ax.add_patch(plt.Rectangle((0 + k * 0.24, -0.38), 0.22, 0.6,
                                   facecolor=color, edgecolor="black", lw=0.6))
    ax.text(1.3, -0.08, "shades(C.ours, 5)", va="center", fontweight="bold",
            fontsize=fk.rel_fontsize(0.8))
    ax.text(1.3, -0.45, "ordered variants of one method (ablation depth)",
            va="center", color="#555555", fontsize=fk.rel_fontsize(0.68))
    ax.set_xlim(-0.1, 5.2)
    ax.set_ylim(-0.9, len(ROLES) + 0.8)
    ax.axis("off")


def annotators(ax) -> None:
    ax.set_title("Annotate the claim", fontweight="bold", loc="left")
    x = np.arange(4, dtype=float)
    values = [100.0, 62.0, 100.0, 41.0]
    colors = [fk.C.other_baseline, fk.C.ours, fk.C.other_baseline, fk.C.ours]
    bars = ax.bar(x, values, 0.6, color=colors, edgecolor="black", lw=0.8)
    fk.bar_labels(ax, bars, fmt="{:.0f}", where="mid")
    ax.set_ylim(0, 165)
    fk.speedup(ax, (x[0], values[0]), (x[1], values[1]), style="arc",
               fmt="{:.2f}x")
    fk.speedup(ax, (x[2], values[2]), (x[3], values[3]), style="bracket",
               fmt="{:.2f}x")
    ax.text(0.5, 150, 'style="arc"', ha="center", fontweight="bold",
            fontsize=fk.rel_fontsize(0.75))
    ax.text(2.5, 150, 'style="bracket"', ha="center", fontweight="bold",
            fontsize=fk.rel_fontsize(0.75))
    ax.set_xticks(x)
    ax.set_xticklabels(["w/o", "w/", "w/o", "w/"], fontweight="bold")
    ax.set_ylabel("Latency (s)", fontweight="bold")
    fk.grid(ax, axis="y")
    fk.bold_ticks(ax)


def main() -> None:
    p = fk.plan("acm-sigplan-text", aspect=0.34, target_pt=9.0, oversample=1.6)
    fk.apply_style(fk.FigureStyle(font_size=p.font_size, axes_linewidth=1.4))
    fig, axes = plt.subplots(1, 2, figsize=p.figsize,
                             gridspec_kw={"width_ratios": [1.5, 1.0]})
    swatches(axes[0])
    annotators(axes[1])
    fig.subplots_adjust(wspace=0.18)
    fk.save(fig, "09_style_reference", plan=p)


if __name__ == "__main__":
    main()
