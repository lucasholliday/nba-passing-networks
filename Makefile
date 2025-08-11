.PHONY: help setup sample render

help:
	@echo "make setup   # create venv and install Python deps"
	@echo "make render  # render analysis/SNAP_Analysis.qmd to docs/index.html"
	@echo "make sample  # (placeholder) manage sample data"

setup:
	python -m venv .venv && . .venv/bin/activate && pip install -r python/requirements.txt

sample:
	@echo "Using sample CSVs in data/sample"

render:
	R -q -e "if(!'quarto' %in% installed.packages()) install.packages('quarto'); quarto::quarto_render('analysis/SNAP_Analysis.qmd', output_dir='docs', output_file='index.html')"
