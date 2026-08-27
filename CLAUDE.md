# CLAUDE.md

Guidance for Claude Code working in this repository.

## What this repo is

A template for publication-quality paper figures. `figkit/` is the library,
`examples/` are worked figures, `docs/` holds the design rules.

## Making a figure

Follow `skills/paper-figure/SKILL.md`. In short: get the claim, copy the closest
`examples/*.py`, size the canvas with `fk.plan()`, draw with one `figkit.charts`
call, set limits before annotating, `fk.save()`, then **run the script and look
at the preview PNG** before reporting done.

## Commands

```bash
make new NAME=10_x   # scaffold examples/10_x.py from templates/new_figure.py
make figures         # regenerate everything into out/
make docs            # rebuild README gallery + docs/RECIPES.md from examples/*.py META
make gallery         # figures + refresh docs/gallery/ + docs   <- the usual one
make check           # import figkit, render the style card, rebuild docs
make clean
```

Use a Python with matplotlib and numpy: `pip install -r requirements.txt`.

## Conventions that matter

- Colors by role (`fk.C.ours`), never raw hex in a figure script.
- `fk.plan()` for canvas sizing; never pick `figsize` and `font_size` separately.
- `fk.apply_style()` inside each figure function — rcParams are global and sticky.
- Axis limits before annotations.
- Docstring of every figure script starts with the `CLAIM` it makes.

## Adding a figure kind

`make new NAME=...`, fill in the `META` dict and the `# >>> data` / `# <<< data`
block, then `make gallery`. The README gallery and the RECIPES table are
GENERATED from those blocks by `tools/build_docs.py` — never hand-edit the text
between the `<!-- BEGIN GALLERY -->` / `<!-- BEGIN RECIPES -->` markers.

## When editing the library

New chart shapes go in `figkit/charts.py`, new annotators in
`figkit/annotate.py`, exported from `figkit/__init__.py`, with an example added
under `examples/` and a row in the API table in README.

## Upstream submodule

`third_party/figures4papers` is a git submodule (not vendored — it has no
license file). Fetch with `git submodule update --init --recursive`. Load its
helper module through `fk.load_upstream()`, never by hardcoding a path. Do not
copy files out of it into this repo.

## Example data is synthetic

Everything under `examples/` and `data/` is invented. Do not commit real
measurements from an unpublished paper into this repo.
