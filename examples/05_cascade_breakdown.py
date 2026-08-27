"""Technique breakdown: a cascade of cumulative gains.

CLAIM  "Here is where the 6.0x comes from, technique by technique."
USE    The single most persuasive systems figure: it decomposes one headline
       number into contributions and shows none of them is doing all the work.

DESIGN NOTES
  * Baseline on top, best at the bottom: the eye reads top-to-bottom as
    "adding things", and the bars visibly shrink.
  * Curved arrows chain bar i to bar i+1, each labelled with the incremental
    ratio; a boxed label survives landing on a gridline.
  * A dashed reference line at the baseline makes the total shrink legible
    without arithmetic.
  * One `total_arrow` under the bars carries the headline number -- the one
    figure element a reader is allowed to quote out of context.
  * Long technique names go on the y axis (they never fit under vertical bars),
    so the left spine is dropped: the labels already anchor the rows.
  * Wide and short on purpose: tall rows would leave the arcs nowhere to bow,
    and the ratio labels would land on top of the bars.
"""
import sys, pathlib; sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1]))

import matplotlib.pyplot as plt

import figkit as fk

META = {
    "title": "5. Cascade breakdown",
    "claim": '"Here is where the 6.0x comes from, technique by technique."',
    "use": "decompose a headline number into contributions",
    "helpers": "`hbar` + `cascade` + `total_arrow`",
    "notes": ("The most persuasive figure in a systems paper: it decomposes the "
              "headline number and shows no single trick is doing all the work. "
              "`cascade()` chains the arcs; `total_arrow()` carries the number "
              "people will quote."),
}

# >>> data
STEPS   = ["Baseline", "+ Operator Fusion", "+ Parallelism\n(4 GPUs)",
           "+ Cache Reuse", "+ Load Balancing"]
LATENCY = [2400, 1810, 610, 505, 402]          # seconds, worst -> best
# <<< data


def main() -> None:
    p = fk.plan("acm-sigplan-text", aspect=0.32, target_pt=8.5)
    fk.apply_style(fk.FigureStyle(font_size=p.font_size, axes_linewidth=1.6))
    fig, ax = plt.subplots(figsize=p.figsize)

    # `order="top_down"` puts STEPS[0] (the baseline) on the top row, which is
    # what `cascade` assumes.
    _, bars = fk.hbar(ax, STEPS, LATENCY, color=fk.C.ours,
                      xlabel="Latency (s)", annotate="inside", fmt="{:.0f}")
    ax.set_xlim(0, max(LATENCY) * 1.24)
    fk.despine(ax, left=True)
    fk.reference_line(ax, LATENCY[0])

    fk.cascade(ax, LATENCY, fmt="{:.2f}x")
    fk.total_arrow(ax, LATENCY[0], LATENCY[-1], offset=-0.62)
    ax.set_ylim(-1.1, len(STEPS) - 0.4)

    fk.save(fig, "05_cascade_breakdown", plan=p)


if __name__ == "__main__":
    main()
