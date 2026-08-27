# Design guide

Why the defaults are what they are. Read once; then the checklist at the end is
enough.

## 1. A figure is an argument

Every figure should have one sentence attached to it before any code is
written. Write it in the script's docstring as `CLAIM:`. It decides everything
downstream: which shape, what to annotate, what to leave out.

The corollary is that raw numbers are rarely the claim. "Baseline 2391s, ours
432s" is data; "5.53x end to end" is the claim. That is why every annotator in
`figkit.annotate` draws a *relationship* between two data points and labels the
ratio. A reviewer skimming at 2am should get the claim from the figure alone.

## 2. Color is a global vocabulary

Across the whole paper:

| Role | Color | Meaning |
|---|---|---|
| `C.ours` | `#0A509E` deep blue | the proposed system, the full method |
| `C.best_baseline` | `#E0A494` warm salmon | the strongest competitor |
| `C.other_baseline` | `#7C7E7F` neutral gray | weak baselines, "origin", "w/o X" |
| `C.ablation` | `#C04829` brick red | ablation variants, second model, deltas |
| `C.highlight` | `#E9A139` amber | callouts, a secondary metric |

Blue is reserved for us, gray is what we beat, red/amber draw the eye to the
delta. A reader who has seen Figure 3 reads Figure 11 faster, because the color
mapping is already loaded.

Practical consequences:

- Never pick a color because it is "next in the cycle". Pick the role.
- Ablations that are *degrees of the same method* use `shades(C.ours, n)` —
  same hue, varying lightness — not five unrelated hues.
- A magnitude (1/2/4/8 GPUs) uses `ORDINAL_BLUE`, which reads as an ordering.
- Bar fills carry a black edge (`lw=0.8`). It survives grayscale printing and
  keeps adjacent bars distinct when two roles are close in lightness.
- In-bar and in-cell text color comes from `text_on(color)`, computed from
  luminance. Never hand-pick white vs. black.

Colorblind check: the palette separates blue from salmon/red mainly by hue,
which deuteranopia compresses. Where two adjacent bars could be confused, the
black edge and the printed value carry the information. For a figure that
*relies* on distinguishing salmon from red, add a hatch (`hatch="//"`) instead
of a new hue.

## 3. Size the canvas backwards from the page

The most common failure in a systems paper is a figure whose text prints at
5pt. See [LATEX.md](LATEX.md). `fk.plan()` does the arithmetic; `fk.save()`
reports the result on every run so it cannot silently regress.

The related rule: **all secondary label sizes are fractions of the base font**
(`figkit.style.REL`), never absolute numbers. Change `font_size` once and the
whole figure rescales in proportion.

## 4. Wide and short

Paper figures compete with text for vertical space, which is the scarce
resource. An aspect ratio of 0.25-0.35 fills the available width and costs
little page height. Multi-panel strips (1xN) beat grids (2x2) for the same
reason, until N > 4.

Corollaries:
- Put value labels *inside* bars where possible. They then cost no headroom.
- Share the y label across horizontally adjacent panels — set it on the leftmost
  panel only.
- One legend for the whole figure, below the panels (`legend_below`).

## 5. Ink discipline

- Top and right spines off. They enclose nothing.
- Grid: dashed, `alpha≈0.35`, on the value axis only, always behind the data
  (`axisbelow=True`). A grid under a bar chart's category axis is pure noise.
- Legends frameless. The box adds ink and separates the legend from what it
  describes.
- Bold labels: they survive the down-scaling to column width. This is why
  `bold_text=True` is the default, and it is the main reason these figures stay
  legible at 8pt.

## 6. Annotate deliberately

- Set axis limits **before** annotating. Curved connectors compute their bow
  from the current limits; annotate first and the arc will be the wrong size.
- Leave room: `headroom(ax, 0.30)` above bars you label, `0.45` on the value
  axis of horizontal bars whose arcs bow sideways.
- Watch collisions where an arrowhead lands on a bar that also carries a value
  label — nudge the label (`bar_labels(..., shift=(6, 3), ha="left")`), not the
  arrow.
- Boxed labels (`boxed=True`) for anything that lands over gridlines or data.

## 7. Reproducibility

One script per figure, data as literals at the top or loaded from `data/`.
No notebook state, no manual post-editing in Illustrator. If a number changes
after a reviewer question, the fix is a one-line edit plus `make figures`.

Notebooks are for exploring; once a figure is going in the paper, port it to a
script. The give-away that a figure came from a notebook is that nobody can
regenerate it six months later during the camera-ready.

## Merging two figures into one

When you are over the page limit, two 1x2 figures with the same y quantity
merge cleanly into a 2x2: keep both row titles, keep the y label on the left
column only, and use one shared legend below. That is usually 30-40% of the
vertical space of the two separate figures, including their captions.

## Checklist before you paste the PDF into the paper

- [ ] The docstring states a CLAIM, and the figure makes it visible.
- [ ] `fk.save()` reported >= 7pt (ideally >= 8pt) on-page text.
- [ ] Colors come from roles, and match the same roles in every other figure.
- [ ] Nothing overlaps: labels, arrowheads, legend, tick labels.
- [ ] Bar axes start at zero.
- [ ] Units on every axis label.
- [ ] Panel letters "(a) (b) (c)" if the caption cites them.
- [ ] `pdffonts` shows no Type-3 fonts.
- [ ] Legible printed in grayscale.
