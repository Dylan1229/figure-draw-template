# Regenerate every figure. `make` alone does the same.
PY      ?= python
EXAMPLES = $(sort $(wildcard examples/*.py))

.PHONY: all figures docs gallery new check clean help

all: gallery

## figures: run every script in examples/ -> out/*.pdf + out/previews/*.png
figures:
	@for f in $(EXAMPLES); do echo "--- $$f"; $(PY) $$f || exit 1; done

## docs: regenerate the README gallery + RECIPES table from examples/*.py META
docs:
	@$(PY) tools/build_docs.py

## gallery: figures -> refresh docs/gallery/ -> regenerate the docs
gallery: figures
	@mkdir -p docs/gallery
	@cp out/previews/*.png docs/gallery/
	@echo "docs/gallery updated ($$(ls docs/gallery | wc -l) images)"
	@$(MAKE) --no-print-directory docs

## new: scaffold a figure, e.g. `make new NAME=10_throughput`
new:
	@test -n "$(NAME)" || { echo "usage: make new NAME=10_my_figure"; exit 1; }
	@test ! -e examples/$(NAME).py || { echo "examples/$(NAME).py exists"; exit 1; }
	@sed 's/new_figure/$(NAME)/g' templates/new_figure.py > examples/$(NAME).py
	@echo "created examples/$(NAME).py"
	@echo "next: fill in META + the data block, then \`make gallery\`"

## check: import the library and render the style card only
check:
	@$(PY) -c "import figkit as fk; print('figkit', fk.__version__, 'ok')"
	@$(PY) examples/09_style_reference.py
	@$(PY) tools/build_docs.py

## clean: delete generated output (never touches docs/gallery)
clean:
	rm -rf out
	find . -name '__pycache__' -type d -prune -exec rm -rf {} +

## help: list targets
help:
	@grep -E '^## ' Makefile | sed 's/## /  /'
