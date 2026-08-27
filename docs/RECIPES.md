# Recipes: which figure for which claim

Start from the sentence you want the reviewer to repeat. The sentence picks the
figure; the figure picks the helper.

<!-- BEGIN RECIPES -->
| Your claim | Figure | Helper | Example |
|---|---|---|---|
| "Our full system is 6.2x faster than the baseline, and both optimizations pull their weight." | 1. Grouped bars + speedup arcs | `grouped_bar` + `speedup_between_bars` | [01](../examples/01_grouped_bar_speedup.py) |
| "Caching helps at every sequence length, and helps most where it costs most." | 2. Horizontal bars, multi-panel | `hbar` + `speedup(bulge="right")` | [02](../examples/02_hbar_panels.py) |
| "We scale near-linearly to 4 GPUs and still gain at 8." | 3. Scaling lines + ratio labels | `scaling_lines` | [03](../examples/03_scaling_lines.py) |
| "Load balancing wins at every GPU count, and the win grows." | 4. Paired bars + bracket deltas | `paired_bar` + `speedup(style="bracket")` | [04](../examples/04_paired_bars_delta.py) |
| "Here is where the 6.0x comes from, technique by technique." | 5. Cascade breakdown | `hbar` + `cascade` + `total_arrow` | [05](../examples/05_cascade_breakdown.py) |
| "Accuracy is flat across the sweep, so pick the configuration that is fastest." | 6. Paired heatmaps | `heatmap` + `sequential_cmap` | [06](../examples/06_heatmap_ablation.py) |
| "Decode dominates, so that is what we optimized." | 7. Stacked breakdown | `stacked_hbar` | [07](../examples/07_stacked_breakdown.py) |
| "Past 8 shards you pay real accuracy for little speed." | 8. Trade-off, mirrored | `mirror_bars` + `side_table` | [08](../examples/08_tradeoff_mirror.py) |
<!-- END RECIPES -->

Generated from the `META` block of each `examples/*.py` by `make docs`.

## Choosing between shapes

**Vertical or horizontal bars?** Horizontal as soon as category names are
longer than about ten characters, or there are more than five of them.
Rotated x-tick labels are a smell; they cost vertical space and reading effort.

**Bars or lines?** Lines imply the x axis is continuous and that interpolating
between points is meaningful. GPU counts (1/2/4/8) are borderline — lines are
conventional for scaling and the trend is the point, so lines win. Model names
are categorical: bars.

**One panel or several?** Split by *model* or *dataset*, never by *metric* —
readers compare across panels, and comparing latency to accuracy is nonsense.
If two panels have the same y quantity, drop the second y label and let them
share.

**Stacked or grouped?** Stacked answers "what is the composition"; grouped
answers "which is bigger". Never stack more than four parts: the middle
segments become impossible to compare because they share no baseline.

**Heatmap or lines?** Heatmap for two parameters swept together. If one of the
two has fewer than four values, a line per value is easier to read and gives
you exact numbers on the axis.

## Anti-patterns

- **A figure without a claim.** If the caption is "Results for X", the figure is
  decoration. Cut it or find the claim.
- **Dual y-axes with different scales.** Two lines on incompatible axes can be
  made to tell any story by rescaling. Use `mirror_bars`, two panels, or
  normalize.
- **Truncated y-axis on bars.** Bars encode length from zero. Cutting the axis
  exaggerates differences and reviewers do notice. Truncate line-plot axes if
  you must; never bar axes.
- **Legend repeating the axis.** If the axis label already says it, delete the
  legend and use the space for data.
- **A new color per figure.** Color is a global vocabulary across the paper. Add
  a role to `figkit/palette.py`, don't hardcode `#FF7F0E` in one script.
- **Numbers only in the caption.** If you want a number quoted, print it *in*
  the figure. Captions get skimmed.
