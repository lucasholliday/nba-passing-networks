.PHONY: setup sample render

setup:
	python -m venv .venv && . .venv/bin/activate && pip install -r python/requirements.txt

sample:
	@echo "Using sample CSVs in data/sample"

render:
	R -q -e "if(!'quarto'%in%installed.packages()) install.packages('quarto'); quarto::quarto_render('analysis/Team21_SNAP_Final.qmd', output_dir='docs', output_file='index.html')"
