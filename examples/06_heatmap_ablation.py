"""Two-parameter sweep: paired heatmaps.

CLAIM  "Accuracy is flat across the sweep, so pick the configuration that is
        fastest." Two heatmaps side by side make that a one-glance argument.
USE    A hyperparameter grid where you must show BOTH what you gain and what
       you pay. One heatmap alone always invites "but what did it cost?".

DESIGN NOTES
  * Each panel uses a white-to-role-color ramp from `sequential_cmap`, so the
    heatmaps stay inside the paper's color language instead of importing
    `viridis` and its unrelated meaning.
  * Cell values are printed: color carries the trend, the number lets a
    reviewer quote your result.
  * Cell text color is computed from the rendered cell color, so a mid-tone
    cell keeps dark text instead of vanishing.
  * Two different quantities => two different colormaps => two colorbars. Never
    share a colorbar across incompatible units.
"""
import sys, pathlib; sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1]))

import matplotlib.pyplot as plt
import numpy as np

import figkit as fk

META = {
    "title": "6. Paired heatmaps",
    "claim": '"Accuracy is flat across the sweep, so pick the configuration that is fastest."',
    "use": "a two-parameter grid where gain and cost must both be shown",
    "helpers": "`heatmap` + `sequential_cmap`",
    "notes": ("A two-parameter sweep showing what you gain *and* what you pay -- "
              "one heatmap alone always invites \"but what did it cost?\". "
              "White-to-role-color ramps keep it inside the paper's color language; "
              "cell text flips black/white automatically."),
}

# >>> data
THRESHOLDS = [0.02, 0.04, 0.06, 0.08, 0.10]     # rows: reuse threshold
RATIOS     = [0.15, 0.25, 0.35, 0.45, 0.55]     # columns: chunk ratio

ACCURACY = np.array([                            # %
    78.42, 78.36, 78.29, 78.44, 78.43,
    78.55, 78.27, 78.45, 78.40, 78.42,
    78.52, 78.51, 78.41, 78.57, 78.33,
    78.38, 78.46, 78.42, 78.44, 78.41,
    78.60, 78.44, 78.18, 78.47, 78.48,
]).reshape(5, 5)
LATENCY = np.array([                             # seconds
    148, 148, 145, 145, 141,
    141, 141, 141, 135, 132,
    135, 138, 125, 122, 118,
    125, 118, 125, 125, 109,
    128, 132, 115, 112, 112,
]).reshape(5, 5)
# <<< data


def main() -> None:
    p = fk.plan("acm-sigplan-text", aspect=0.34, target_pt=7.5, oversample=1.6)
    fk.apply_style(fk.FigureStyle(font_size=p.font_size, axes_linewidth=1.2))
    fig, axes = plt.subplots(1, 2, figsize=p.figsize)

    panels = [
        (axes[0], ACCURACY, "Accuracy (%)", fk.sequential_cmap(fk.C.ours), "{:.1f}"),
        (axes[1], LATENCY, "Latency (s)", fk.sequential_cmap(fk.C.ablation), "{:.0f}"),
    ]
    for ax, matrix, title, cmap, fmt in panels:
        fk.heatmap(ax, matrix, RATIOS, THRESHOLDS, cmap=cmap, fmt=fmt,
                   xlabel="Chunk Ratio", ylabel="Reuse Threshold", title=title)

    fig.subplots_adjust(wspace=0.4)
    fk.save(fig, "06_heatmap_ablation", plan=p)


if __name__ == "__main__":
    main()
