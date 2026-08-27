"""Saving figures: vector PDF for the paper, PNG preview for your eyes.

Two outputs, always:
  * `<out>/<name>.pdf`          -> what LaTeX includes. Vector, Type-42 fonts.
  * `<out>/previews/<name>.png` -> what you open to check the figure. Raster,
    cheap, viewable over SSH, and safe to delete (it is regenerable).

Point `set_output_dir()` at your paper's `figures/` directory and the script
becomes the single source of truth for that PDF: re-run it, recompile, done.
"""

from __future__ import annotations

import warnings
from pathlib import Path
from typing import Final, Sequence

import matplotlib.pyplot as plt

from . import sizing

_VECTOR: Final[set[str]] = {"pdf", "svg", "eps"}
_RASTER: Final[set[str]] = {"png", "jpg", "jpeg", "tif", "tiff"}
_SUPPORTED: Final[set[str]] = _VECTOR | _RASTER

_REPO_ROOT: Final[Path] = Path(__file__).resolve().parent.parent
_OUT: Path = _REPO_ROOT / "out"
_PREVIEW: Path = _OUT / "previews"
_QUIET: bool = False


def set_output_dir(out_dir: str | Path, preview_dir: str | Path | None = None) -> None:
    """Redirect where `save()` writes.

    In a paper repo the usual call is::

        fk.set_output_dir("figures", "plots/previews")

    so the PDFs land next to the `.tex` files and the throwaway PNGs stay in
    the plotting directory (add them to `.gitignore`).
    """
    global _OUT, _PREVIEW
    _OUT = Path(out_dir).expanduser().resolve()
    _PREVIEW = Path(preview_dir).expanduser().resolve() if preview_dir else _OUT / "previews"


def output_dirs() -> tuple[Path, Path]:
    return _OUT, _PREVIEW


def quiet(on: bool = True) -> None:
    """Silence the per-figure report line."""
    global _QUIET
    _QUIET = on


def save(fig, name: str, *, formats: Sequence[str] = ("pdf",), dpi: int = 300,
         preview: bool = True, preview_dpi: int = 110, pad: float = 0.04,
         close: bool = True, layout: str | float | None = None,
         frac: float = 1.0, plan: "sizing.Plan | None" = None,
         **savefig_kwargs) -> list[Path]:
    """Write `fig` to the output dir(s) and report its on-page text size.

    Args:
        fig: The figure.
        name: Base filename, no extension. Match the `\\includegraphics` name.
        formats: Paper formats to write into the output dir. `pdf` unless you
            need `svg` for hand-editing or `eps` for an old submission system.
        dpi: Raster resolution for non-vector `formats`.
        preview: Also write a small PNG into the preview dir.
        pad: Inches of whitespace kept around the tight bounding box. Keep it
            small (0.02-0.06): LaTeX adds its own spacing, and generous padding
            inside the PDF is invisible margin you cannot remove later.
        close: Close the figure afterwards. Set False if you want to keep
            tweaking it interactively.
        layout / frac: For the readability report only; see `figkit.sizing`.
        plan: The `figkit.plan(...)` used to size this figure. Supplies
            `layout`/`frac` so the printed report matches reality.

    Returns:
        Paths written, previews included.
    """
    if plan is not None:
        layout, frac = plan.layout, plan.frac

    written: list[Path] = []
    _OUT.mkdir(parents=True, exist_ok=True)

    for ext in formats:
        ext = ext.lower().lstrip(".")
        if ext not in _SUPPORTED:
            raise ValueError(f"Unsupported format {ext!r}")
        target = _OUT / f"{name}.{ext}"
        kw = dict(format=ext, bbox_inches="tight", pad_inches=pad,
                  facecolor="white")
        if ext in _RASTER:
            kw["dpi"] = dpi
        kw.update(savefig_kwargs)
        fig.savefig(target, **kw)
        written.append(target)

    if preview:
        _PREVIEW.mkdir(parents=True, exist_ok=True)
        target = _PREVIEW / f"{name}.png"
        fig.savefig(target, format="png", dpi=preview_dpi, bbox_inches="tight",
                    pad_inches=pad, facecolor="white")
        written.append(target)

    if not _QUIET:
        w, h = fig.get_size_inches()
        base = plt.rcParams["font.size"]
        pt = sizing.effective_pt(base, w, layout, frac)
        flag = "" if pt >= sizing.GOOD_PT else (
            "  <-- tight" if pt >= sizing.MIN_READABLE_PT else "  <-- TOO SMALL, enlarge fonts or narrow the canvas")
        print(f"[figkit] {name:<34} {w:g}x{h:g}in  base {base:g}pt -> "
              f"{pt:.1f}pt on page{flag}")
        if pt < sizing.MIN_READABLE_PT:
            warnings.warn(
                f"{name}: body text prints at {pt:.1f}pt "
                f"(<{sizing.MIN_READABLE_PT}pt). Raise FigureStyle(font_size=...) "
                f"or shrink figsize width.", stacklevel=2)

    if close:
        plt.close(fig)
    return written


#: Backwards-compatible alias for scripts ported from `scientific_figure_pro`.
def finalize_figure(fig, out_path, formats=None, dpi: int = 300,
                    close: bool = True, pad: float = 0.05, **kwargs):
    """Legacy shim: takes a full path instead of a name + output dir."""
    path = Path(out_path)
    exts = list(formats) if formats else ([path.suffix.lstrip(".")] if path.suffix else ["pdf"])
    base = path.with_suffix("") if path.suffix else path
    base.parent.mkdir(parents=True, exist_ok=True)
    saved = []
    for ext in exts:
        ext = ext.lower().lstrip(".")
        kw = dict(format=ext, bbox_inches="tight", pad_inches=pad)
        if ext in _RASTER:
            kw["dpi"] = dpi
        kw.update(kwargs)
        target = base.with_suffix(f".{ext}")
        fig.savefig(target, **kw)
        saved.append(target)
    if close:
        plt.close(fig)
    return saved
