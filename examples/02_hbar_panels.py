"""Horizontal bars, multi-panel.

CLAIM  "Caching helps at every sequence length, and helps most where it costs
        most."
USE    Many settings with long names, one metric. Horizontal bars let
       "16K tok w/o cache" be a label instead of a rotated, truncated x-tick.

DESIGN NOTES
  * Panels of unequal width via `width_ratios` -- panel (c) has fewer bars, so
    it gets less space instead of being padded out with air.
  * Values printed *inside* the bars in white: costs no horizontal space and
    leaves the right margin free for the speedup arcs.
  * Arcs bow to the *right* (`bulge="right"`) into that reserved whitespace.
    `headroom(axis="x")` creates it.
  * Panel letters via `panel_titles` -- captions cite "(b)", so the figure must
    say "(b)".
"""
import sys, pathlib; sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1]))

import matplotlib.pyplot as plt

import figkit as fk

META = {
    "title": "2. Horizontal bars, multi-panel",
    "claim": '"Caching helps at every sequence length, and helps most where it costs most."',
    "use": "many settings with long names, one metric",
    "helpers": "`hbar` + `speedup(bulge=\"right\")`",
    "notes": ("Long setting names become y labels instead of rotated x-ticks. "
              "Values sit *inside* the bars; the arcs bow sideways into whitespace "
              "reserved by `headroom(axis=\"x\")`. Panels get unequal widths via "
              "`width_ratios`."),
}

# >>> data
SETTINGS   = ["1K tok", "4K w/o", "4K w/", "16K w/o", "16K w/"]
MODEL_A    = [126, 152, 121, 455, 348]         # seconds, 4 GPUs
MODEL_B    = [274, 289, 226, 812, 573]
SINGLE_GPU_LABELS = ["A 4K w/o", "A 4K w/", "B 4K w/o", "B 4K w/"]
SINGLE_GPU = [604, 401, 1088, 522]
# <<< data


def main() -> None:
    p = fk.plan("acm-sigplan-text", aspect=0.24, target_pt=8.0)
    fk.apply_style(fk.FigureStyle(font_size=p.font_size, axes_linewidth=1.6))
    fig, axes = plt.subplots(1, 3, figsize=p.figsize,
                             gridspec_kw={"width_ratios": [1.15, 1.15, 1.0]})

    panels = [
        (axes[0], SETTINGS, MODEL_A, fk.C.ours, [(1, 2), (3, 4)]),
        (axes[1], SETTINGS, MODEL_B, fk.C.ours, [(1, 2), (3, 4)]),
        (axes[2], SINGLE_GPU_LABELS, SINGLE_GPU, fk.C.ablation, [(0, 1), (2, 3)]),
    ]
    for ax, labels, values, color, pairs in panels:
        _, bars = fk.hbar(ax, labels, values, color=color,
                          xlabel="Latency (s)", annotate="inside", fmt="{:.0f}")
        fk.headroom(ax, 0.46, axis="x")        # whitespace for the arcs
        for i, j in pairs:
            fk.speedup_between_bars(ax, bars, i, j, horizontal=True,
                                    fmt="{:.2f}x", bulge_frac=0.11, lw=1.5)

    fk.panel_titles(axes, ["Model-A (4 GPU)", "Model-B (4 GPU)", "Single GPU"])
    fig.subplots_adjust(wspace=0.55)
    fk.save(fig, "02_hbar_panels", plan=p)


if __name__ == "__main__":
    main()
