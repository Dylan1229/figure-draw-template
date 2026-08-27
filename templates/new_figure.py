"""<FIGURE NAME> -- one line saying what the reader should conclude.

CLAIM  The sentence you want a reviewer to repeat after two seconds of looking.
       If you cannot write it, the figure is not ready to be drawn.
USE    When this figure shape is the right one. See docs/RECIPES.md.

Scaffold a copy with `make new NAME=10_my_figure`, then fill in the five
numbered sections below.

Run:  python examples/10_my_figure.py
"""
import sys, pathlib; sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1]))

import matplotlib.pyplot as plt

import figkit as fk

# ------------------------------------------------------------------- 0. META
# Read by tools/build_docs.py to generate this figure's README gallery entry
# and its row in docs/RECIPES.md. Must be a plain literal (it is parsed, not
# imported). `make docs` regenerates both.
META = {
    "title": "N. Short name of the figure kind",
    "claim": '"The one sentence this figure argues."',
    "use": "when to reach for this shape",
    "helpers": "`chart_helper` + `annotator`",
    "notes": "Two or three lines for the README: why this shape, what to watch for.",
}

# ------------------------------------------------------------------- 1. data
# Literals in the units the axis will show. Everything between the two markers
# is lifted verbatim into the README, so keep it readable and commented.
# >>> data
CATEGORIES = ["Setting A", "Setting B"]
BASELINE   = [100.0, 210.0]        # seconds
OURS       = [42.0, 78.0]
# <<< data


def main() -> None:
    # ------------------------------------------------------------ 2. canvas
    # Size the canvas backwards from the printed page. "acm-sigplan-col" for a
    # `figure`, "acm-sigplan-text" for a `figure*` that spans both columns.
    p = fk.plan("acm-sigplan-col", aspect=0.62, target_pt=8.0)
    fk.apply_style(fk.FigureStyle(font_size=p.font_size, axes_linewidth=1.6))
    fig, ax = plt.subplots(figsize=p.figsize)

    # -------------------------------------------------------------- 3. draw
    _, bars = fk.grouped_bar(
        ax, CATEGORIES, [BASELINE, OURS], labels=["Baseline", "Ours"],
        colors=[fk.C.other_baseline, fk.C.ours],
        ylabel="Latency (s)", annotate="outside", fmt="{:.0f}",
    )

    # ---------------------------------------------------------- 4. annotate
    # Limits BEFORE annotations: connectors size their curvature from them.
    fk.headroom(ax, 0.34)
    for i in range(len(CATEGORIES)):
        fk.speedup_between_bars(ax, [bars[0][i], bars[1][i]], 0, 1, fmt="{:.2f}x")
    ax.legend(prop={"weight": "bold"})

    # ------------------------------------------------------------- 5. save
    # Writes out/<name>.pdf plus out/previews/<name>.png, and prints the point
    # size your text will actually have on the page.
    fk.save(fig, "new_figure", plan=p)


if __name__ == "__main__":
    main()
