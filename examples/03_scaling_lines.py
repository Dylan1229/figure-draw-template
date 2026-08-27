"""Scaling lines with per-point speedup labels.

CLAIM  "We scale near-linearly to 4 GPUs and still gain at 8."
USE    One metric against a scaling knob (GPUs, batch size, sequence length).

DESIGN NOTES
  * Each point is labelled with its speedup over that series' first point.
    A raw latency curve makes the reader divide numbers in their head; the
    ratio labels are the actual claim.
  * Series may have different x support -- the 8-GPU point exists only for the
    long-sequence workload, and that is fine.
  * Color + marker + linestyle all vary together, so the figure survives
    grayscale printing and colorblind readers.
  * `set_xticks` on the real GPU counts (1, 2, 4, 8), never matplotlib's
    automatic 0, 2, 4, 6, 8.
"""
import sys, pathlib; sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1]))

import matplotlib.pyplot as plt

import figkit as fk

META = {
    "title": "3. Scaling lines + ratio labels",
    "claim": '"We scale near-linearly to 4 GPUs and still gain at 8."',
    "use": "one metric against a scaling knob",
    "helpers": "`scaling_lines`",
    "notes": ("Each point is labelled with its speedup over that series' first "
              "point, so the reader never has to divide numbers in their head. "
              "Series may have different x support -- the 8-GPU point exists only "
              "for the long-sequence workload, and that is fine."),
}

# >>> data
MODEL_A = {"4K tok":  {1: 488, 2: 251,  4: 129},          # {workload: {gpus: seconds}}
           "16K tok": {1: 1622, 2: 795, 4: 447, 8: 302}}
MODEL_B = {"4K tok":  {1: 872, 2: 451,  4: 233},
           "16K tok": {1: 2480, 2: 1310, 4: 762, 8: 498}}
# <<< data

COLORS = [fk.C.ours, fk.C.ablation]


def main() -> None:
    p = fk.plan("acm-sigplan-text", aspect=0.27, target_pt=8.5)
    fk.apply_style(fk.FigureStyle(font_size=p.font_size, axes_linewidth=1.6))
    fig, axes = plt.subplots(1, 2, figsize=p.figsize)

    for ax, data, title, ylab in ((axes[0], MODEL_A, "Model-A", True),
                                  (axes[1], MODEL_B, "Model-B", False)):
        fk.scaling_lines(ax, data, colors=COLORS,
                         xlabel="Number of GPUs",
                         ylabel="Latency (s)" if ylab else None,
                         annotate_ratio=True, fmt="{:.1f}x",
                         xticks=[1, 2, 4, 8])
        ax.set_title(title, fontweight="bold")
        ax.set_xlim(0.5, 8.7)
        fk.headroom(ax, 0.12)
        ax.legend(prop={"weight": "bold"}, loc="upper right")

    fig.subplots_adjust(wspace=0.22)
    fk.save(fig, "03_scaling_lines", plan=p)


if __name__ == "__main__":
    main()
