---
name: paper-figure
description: Create publication-quality matplotlib figures for systems/ML papers using the figkit library in this repository. Use when asked to make, edit, or restyle a figure for a paper, poster, or talk.
---

# Paper figure

Build figures with `figkit` (this repo's `figkit/` package). Do not write raw
matplotlib style code, and do not invent colors or font sizes.

## Procedure

1. **Get the claim.** One sentence the reader should repeat after two seconds.
   If the user did not give one, ask — it determines the figure shape. Put it in
   the script docstring as `CLAIM`.
2. **Pick the shape** from `docs/RECIPES.md` (claim -> figure -> helper). Copy
   the closest `examples/*.py` rather than starting blank.
3. **Size the canvas** with `fk.plan(layout, aspect, target_pt)`. Never pick
   `figsize` and `font_size` independently. `figure` -> `*-col` layout,
   `figure*` -> `*-text`. Target 8pt; 7pt is the floor.
4. **Draw** with one `figkit.charts` call.
5. **Set limits, then annotate.** `fk.headroom()` before `fk.speedup()` /
   `fk.cascade()` — connectors size their curvature from the current limits.
6. **Save** with `fk.save(fig, name, plan=p)`.
7. **Run the script and look at `out/previews/<name>.png`.** Check for
   overlapping labels, arrowheads landing on text, and the on-page point size
   printed by `save()`. Fix and re-run before reporting done.

## Rules

- Colors come from roles: `fk.C.ours`, `.best_baseline`, `.other_baseline`,
  `.ablation`, `.highlight`. Never a raw hex in a figure script. Degrees of one
  method use `fk.shades(fk.C.ours, n)`.
- Label sizes are relative (`fk.rel_fontsize`, `figkit.style.REL`), never
  absolute — unless fixing a specific collision.
- Bar axes start at zero. Line axes may be truncated.
- Units in every axis label. Panel letters via `fk.panel_titles` if the caption
  will cite "(a)".
- One shared legend below a multi-panel figure (`fk.legend_below`); delete a
  legend that repeats an axis label.
- `fk.apply_style()` inside each figure function — rcParams are global.
- Data as literals at the top of the script or loaded from `data/`; never
  computed inline inside the plotting code.

## Adding a new figure kind

`make new NAME=10_x` scaffolds from `templates/new_figure.py`. Fill in the
`META` dict (title, claim, use, helpers, notes) and put the data between the
`# >>> data` / `# <<< data` markers — `tools/build_docs.py` lifts both into the
README gallery and `docs/RECIPES.md`. Then `make gallery`. Never hand-edit the
generated sections.

Example data must be synthetic. Do not copy real measurements from an
unpublished paper into this repo.

## Extending the library

If a shape is genuinely new, add it to `figkit/charts.py` with a docstring that
says *what claim it makes* and *when to use it*, export it from
`figkit/__init__.py`, and add an example. Do not copy-paste a variant into a
figure script.
