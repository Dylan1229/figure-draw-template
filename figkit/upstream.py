"""Bridge to the upstream `figures4papers` repository.

`third_party/figures4papers` is a git submodule of
https://github.com/ChenLiu-1996/figures4papers (Chen Liu, Yale) -- the
repository this template's style conventions come from. It is *referenced*, not
copied: it carries no license file, so its code stays where its author
published it and you get it straight from the source.

    git submodule update --init --recursive

What is in there:
  * `scientific-figure-making/` -- the current skill: design theory, an API
    reference, common patterns, tutorials. Read these; they are the prose
    behind figkit's defaults.
  * `figure_*/` -- one directory per paper, each a standalone plotting script.
    Good hunting ground when you need a shape figkit does not have yet.
  * `skills/scientific-figure-pro/scripts/scientific_figure_pro.py` -- the
    original helper module (`make_grouped_bar`, `make_trend`, `make_heatmap`,
    `make_sphere_illustration`, ...). Present in revisions up to `58628f6`;
    later revisions restructured it away. `load_upstream()` finds it if your
    checkout has it.

figkit and the upstream helpers mix freely -- they configure the same global
rcParams and draw on plain matplotlib axes:

    import figkit as fk
    sfp = fk.load_upstream()

    fk.apply_style("paper")                  # figkit sets the style
    fig, ax = plt.subplots(figsize=(9, 4))
    sfp.make_sphere_illustration(ax)         # upstream draws
    fk.save(fig, "illustration")             # figkit saves

figkit also keeps `apply_publication_style` and `finalize_figure` as aliases, so
scripts written directly against `scientific_figure_pro` run unchanged.
"""

from __future__ import annotations

import importlib.util
import sys
from pathlib import Path
from types import ModuleType

_ROOT = Path(__file__).resolve().parent.parent
SUBMODULE = _ROOT / "third_party" / "figures4papers"

#: Where the helper module has lived across upstream layouts, newest first.
_CANDIDATES = (
    SUBMODULE / "scientific-figure-making" / "scripts" / "scientific_figure_pro.py",
    SUBMODULE / "skills" / "scientific-figure-pro" / "scripts" / "scientific_figure_pro.py",
)

#: Last upstream revision known to ship the standalone helper module.
MODULE_REVISION = "58628f6"

_cache: dict[str, ModuleType] = {}


def upstream_root() -> Path:
    """Path to the submodule checkout (may not exist yet)."""
    return SUBMODULE


def find_upstream() -> Path | None:
    """First existing `scientific_figure_pro.py` across known layouts."""
    return next((p for p in _CANDIDATES if p.exists()), None)


def load_upstream(path: str | Path | None = None,
                  name: str = "scientific_figure_pro") -> ModuleType:
    """Import the upstream helper module by file path.

    Args:
        path: Explicit location. Defaults to searching the submodule checkout.
        name: Name to register in `sys.modules`.

    Returns:
        The loaded module; repeat calls return the cached instance.

    Raises:
        FileNotFoundError: If the submodule is missing, or its checked-out
            revision does not ship the module. The message says how to fix it.
    """
    target = Path(path) if path else find_upstream()

    if target is None or not target.exists():
        if not SUBMODULE.exists() or not any(SUBMODULE.iterdir()):
            raise FileNotFoundError(
                f"{SUBMODULE} is empty. Fetch the submodule:\n"
                "    git submodule update --init --recursive")
        raise FileNotFoundError(
            "scientific_figure_pro.py is not in the checked-out revision of "
            f"{SUBMODULE.name} (upstream restructured it away).\n"
            "Either check out a revision that has it:\n"
            f"    git -C {SUBMODULE} checkout {MODULE_REVISION}\n"
            "or pass an explicit path: fk.load_upstream('/path/to/"
            "scientific_figure_pro.py')\n"
            "Most of what it provides is already in figkit -- see the API table "
            "in README.md.")

    key = str(target)
    if key in _cache:
        return _cache[key]

    spec = importlib.util.spec_from_file_location(name, target)
    if spec is None or spec.loader is None:
        raise ImportError(f"could not load a module from {target}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    _cache[key] = module
    return module
