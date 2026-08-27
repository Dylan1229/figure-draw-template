# Putting the figure in the paper

## The one number that matters

LaTeX scales your PDF to fit the width you ask for. Text scales with it:

```
effective_pt = font_size * (target_width_in / figsize_width_in)
```

An 18pt label on a 12-inch canvas placed in a 3.33-inch ACM column prints at
**5pt**. That is why `figkit.plan()` exists — it inverts the formula, and
`fk.save()` prints the result for every figure:

```
[figkit] 01_grouped_bar_speedup   14x3.78in  base 17pt -> 8.5pt on page
```

Aim for **8pt**; **7pt** is the floor for a camera-ready; below 6pt figkit warns.

## Column widths

`figkit.LAYOUTS` ships the common ones. Verify yours once — put this in your
document and read the log:

```latex
\typeout{COLUMNWIDTH=\the\columnwidth}
\typeout{TEXTWIDTH=\the\textwidth}
```

Divide by 72.27 to get inches, then either pick the closest `LAYOUTS` key or
pass the number directly: `fk.plan(3.33, aspect=0.6)`.

## Includes

Single column (fits in one column of a two-column layout):

```latex
\begin{figure}[t]
  \centering
  \includegraphics[width=\linewidth]{figures/04_paired_bars_delta.pdf}
  \caption{Workload rebalancing reduces latency by up to 1.42$\times$...}
  \label{fig:rebalance}
\end{figure}
```

Full width (spans both columns — use for wide multi-panel strips):

```latex
\begin{figure*}[t]
  \centering
  \includegraphics[width=\linewidth]{figures/01_grouped_bar_speedup.pdf}
  \caption{...}
  \label{fig:e2e}
\end{figure*}
```

Match the `plan()` layout to the environment: `figure` -> `*-col`,
`figure*` -> `*-text`. If you use `width=0.9\linewidth`, pass `frac=0.9` to
`plan()` so the report stays honest.

## Wiring the scripts to the paper

Point the output directory at the paper and the script becomes the source of
truth for that PDF:

```python
fk.set_output_dir("../paper/figures", "previews")
```

Then `make figures && latexmk -pdf main.tex` is the whole loop. Add the plotting
directory to the paper repo so a co-author can regenerate anything, and
`.gitignore` the previews.

## Space, when the paper is over the page limit

In order of what to try first:

1. **Shrink the caption spacing**, not the figure:
   `\setlength{\abovecaptionskip}{4pt}` / `\belowcaptionskip`.
2. **Flatten the aspect ratio.** `aspect=0.24` instead of `0.32` costs no
   readability if the fonts are re-planned.
3. **Merge two figures into one** with shared axis labels — two 2-panel figures
   become one 2x2 (see the note in `docs/DESIGN_GUIDE.md` on merging).
4. **Drop the panel title** and say it in the caption, if the panel letters are
   enough.
5. Only then consider cutting a figure.

Do not scale a figure with `width=0.8\linewidth` to save space — that shrinks
the text below readable size. Re-plan the canvas instead.

## Fonts

`pdf.fonttype = 42` is set for you: figures embed TrueType, not Type-3. ACM and
IEEE both reject Type-3 fonts at camera-ready, and the usual culprit is a
matplotlib figure made without this setting. Verify:

```bash
pdffonts figures/01_grouped_bar_speedup.pdf   # 'Type 3' must not appear
```

If you turn on `use_tex=True`, everything renders through LaTeX and text will
match the paper body exactly — at roughly 3x the render time, and it needs a
working local TeX install.
