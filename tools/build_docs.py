"""Regenerate the README gallery and the RECIPES table from examples/*.py.

Adding a figure kind is a one-file operation: drop a script in `examples/` with
a `META` dict and a `# >>> data` / `# <<< data` block, run `make docs`, and it
appears in the gallery, the recipes table and the repo's table of contents.
Nothing is hand-maintained, so the docs cannot drift from the code.

The data snippet is sliced out of the script itself rather than copied into
META -- the README therefore always shows the data that actually produced the
image next to it.
"""

from __future__ import annotations

import ast
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
EXAMPLES = ROOT / "examples"
GALLERY = "docs/gallery"

BEGIN_G, END_G = "<!-- BEGIN GALLERY -->", "<!-- END GALLERY -->"
BEGIN_R, END_R = "<!-- BEGIN RECIPES -->", "<!-- END RECIPES -->"

REQUIRED = ("title", "claim", "use", "helpers", "notes")


class Example:
    """One `examples/*.py`, parsed without importing it (so no matplotlib)."""

    def __init__(self, path: Path) -> None:
        self.path = path
        self.name = path.stem
        source = path.read_text()
        self.meta = self._meta(source)
        self.data = self._data(source)

    def _meta(self, source: str) -> dict:
        for node in ast.parse(source).body:
            if isinstance(node, ast.Assign) and any(
                    getattr(t, "id", None) == "META" for t in node.targets):
                meta = ast.literal_eval(node.value)
                missing = [k for k in REQUIRED if k not in meta]
                if missing:
                    raise SystemExit(f"{self.path.name}: META missing {missing}")
                return meta
        raise SystemExit(f"{self.path.name}: no META dict (see templates/new_figure.py)")

    def _data(self, source: str) -> str:
        match = re.search(r"^# >>> data\n(.*?)^# <<< data", source, re.S | re.M)
        return match.group(1).strip("\n") if match else ""

    @property
    def image(self) -> str:
        return f"{GALLERY}/{self.name}.png"

    def gallery_entry(self) -> str:
        parts = [f"### {self.meta['title']} — [`{self.path.name}`](examples/{self.path.name})",
                 "",
                 f"> **Claim:** {self.meta['claim']}",
                 ""]
        if self.data:
            parts += ["```python", self.data, "```", ""]
        if (ROOT / self.image).exists():
            parts += [f"![]({self.image})", ""]
        parts += [self.meta["notes"].strip(), "", "---", ""]
        return "\n".join(parts)

    def recipe_row(self) -> str:
        return (f"| {self.meta['claim']} | {self.meta['title']} | "
                f"{self.meta['helpers']} | [{self.name.split('_')[0]}]"
                f"(../examples/{self.path.name}) |")


def splice(text: str, begin: str, end: str, body: str, where: Path) -> str:
    if begin not in text or end not in text:
        raise SystemExit(f"{where.name}: missing {begin} / {end} markers")
    head, rest = text.split(begin, 1)
    _, tail = rest.split(end, 1)
    return f"{head}{begin}\n{body}\n{end}{tail}"


def main() -> int:
    examples = [Example(p) for p in sorted(EXAMPLES.glob("*.py"))]
    if not examples:
        raise SystemExit("no examples found")

    readme_path = ROOT / "README.md"
    readme = readme_path.read_text()
    readme = splice(readme, BEGIN_G, END_G,
                    "\n".join(e.gallery_entry() for e in examples), readme_path)
    readme_path.write_text(readme)

    recipes_path = ROOT / "docs" / "RECIPES.md"
    recipes = recipes_path.read_text()
    table = ["| Your claim | Figure | Helper | Example |", "|---|---|---|---|"]
    table += [e.recipe_row() for e in examples if e.data]
    recipes = splice(recipes, BEGIN_R, END_R, "\n".join(table), recipes_path)
    recipes_path.write_text(recipes)

    missing = [e.name for e in examples if not (ROOT / e.image).exists()]
    print(f"[docs] {len(examples)} examples -> README gallery + RECIPES table")
    if missing:
        print(f"[docs] no gallery image yet for: {', '.join(missing)}"
              f" (run `make gallery`)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
