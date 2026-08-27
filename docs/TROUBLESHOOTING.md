# Troubleshooting

**`ModuleNotFoundError: No module named 'figkit'`**
Run the script from the repo root, or keep the two-line `sys.path` bootstrap at
the top of each example, or `pip install -e .`.

**`fk.save()` warns "TOO SMALL"**
Your canvas is much wider than the printed width. Use `fk.plan()` to size it
rather than picking `figsize` and `font_size` independently. See
[LATEX.md](LATEX.md).

**A speedup arc has the wrong curvature, or leaves the panel**
The arc bows by a fraction of the current axis range, so it must be drawn after
the limits are final. Move `headroom()` / `set_ylim()` above the `speedup()`
call, and raise `bulge_frac` if a tall bar sits between the endpoints.

**Labels overlap the arrowheads**
The arrowhead lands on the bar top, exactly where an "outside" value label
sits. Nudge the label: `bar_labels(ax, bars, shift=(6, 3), ha="left")`. See
`examples/01_grouped_bar_speedup.py`.

**Cascade ratio labels sit on top of the bars**
`cascade` places each label past the end of the longer bar, which needs
headroom on the value axis. Set `ax.set_xlim(0, max(values) * 1.24)` and keep
the panel wide and short — tall rows leave the arcs nowhere to bow.

**Mirror-bar tick labels are ugly (126, 202, 278...)**
`up_range`/`down_range` are being split into non-round steps. Pick round
endpoints and a matching tick count: `(0, 450)` with `down_nticks=4` gives
0/150/300/450.

**Fonts differ between machines**
`DejaVu Sans` ships with matplotlib and is the default first choice, so figures
are reproducible everywhere. If you put Helvetica/Arial first and a co-author
lacks it, matplotlib silently falls back and their PDF differs from yours.
Either commit to what everyone has, or check in the font.

**`pdffonts` reports Type-3 fonts**
Something reset `pdf.fonttype`. Call `fk.apply_style()` *after* any other
`rcParams` manipulation — it sets `pdf.fonttype = 42`.

**A figure looks fine on screen and cramped in the PDF**
`bbox_inches="tight"` crops to the ink, so on-screen margins are not what LaTeX
sees. Check the preview PNG (it is produced with the same crop), not the
notebook output.

**Text is clipped at the edges**
Raise `pad` in `fk.save(..., pad=0.08)`, or reduce `wspace` in
`fig.subplots_adjust`. Rotated y-axis labels on the leftmost panel are the
usual cause.

**The legend covers data**
Move it out: `fk.legend_below(fig, ...)` for a shared legend, or give the panel
more `headroom` and pin the legend to `loc="upper right"`.

**Everything is bold and you want it not to be**
`fk.apply_style(fk.FigureStyle(bold_text=False))`. Bold is the house default
because it survives down-scaling, but a single-column figure printed near full
size does not need it.

**rcParams leak between figures in one script**
They are global and sticky. Call `fk.apply_style(...)` at the top of *each*
figure function, not once at module level — the examples all do this.
