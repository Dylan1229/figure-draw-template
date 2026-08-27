"""Paired bars with bracket deltas: with vs. without one technique.

CLAIM  "Load balancing wins at every GPU count, and the win grows."
USE    A single ablation toggled across a few configurations. Two bars per
       group is the clearest possible form -- resist adding a third.

DESIGN NOTES
  * `style="bracket"` instead of an arc: the two bars are adjacent, so an
    L-shaped connector (across at the old height, then down onto the new one)
    reads as "this much was removed".
  * Values sit *mid-bar* in white -- there is no room above them once the
    bracket is drawn.
  * Gray = the thing without our technique, blue = with. Same role-to-color
    mapping as every other figure in the paper.
"""
import sys, pathlib; sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1]))

import matplotlib.pyplot as plt

import figkit as fk

META = {
    "title": "4. Paired bars + bracket deltas",
    "claim": '"Load balancing wins at every GPU count, and the win grows."',
    "use": "one ablation toggled across configurations",
    "helpers": '`paired_bar` + `speedup(style="bracket")`',
    "notes": ("The single-ablation figure. An L-shaped bracket reads as \"this "
              "much was removed\" in a way a curved arc does not; values sit "
              "mid-bar because the bracket occupies the space above."),
}

# >>> data
GROUPS  = ["2 GPUs", "4 GPUs", "8 GPUs"]
MODEL_A = {"w/o": [578, 371, 286], "w/": [491, 268, 201]}   # seconds
MODEL_B = {"w/o": [1042, 628, 447], "w/": [884, 470, 312]}
# <<< data


def main() -> None:
    p = fk.plan("acm-sigplan-text", aspect=0.27, target_pt=8.5)
    fk.apply_style(fk.FigureStyle(font_size=p.font_size, axes_linewidth=1.6))
    fig, axes = plt.subplots(1, 2, figsize=p.figsize)

    for ax, data, title, ylab in ((axes[0], MODEL_A, "Model-A (16K tok)", True),
                                  (axes[1], MODEL_B, "Model-B (16K tok)", False)):
        x, b0, b1 = fk.paired_bar(
            ax, GROUPS, data["w/o"], data["w/"],
            labels=("w/o balancing", "w/ balancing"),
            colors=(fk.C.other_baseline, fk.C.ours),
            annotate="mid", fmt="{:.0f}",
            ylabel="Latency (s)" if ylab else None,
        )
        ax.set_title(title, fontweight="bold")
        fk.headroom(ax, 0.32)
        for i in range(len(GROUPS)):
            fk.speedup_between_bars(ax, [b0[i], b1[i]], 0, 1, style="bracket",
                                    fmt="{:.2f}x")
        ax.legend(prop={"weight": "bold"})

    fig.subplots_adjust(wspace=0.22)
    fk.save(fig, "04_paired_bars_delta", plan=p)


if __name__ == "__main__":
    main()
