
# NBA Passing Networks & Scoring (ALAAM/ERGM)

This repo builds directed, weighted **NBA player passing networks** and analyzes how
network structure relates to team wins and individual scoring (20+ PPG) using **ALAAM** and **ERGM**.
It includes a sample dataset so you can render the write-up without hitting external APIs.

## Repo map
```
analysis/   # Quarto .qmd (render to docs/index.html)
python/     # scrapers/utilities (nba_api, BeautifulSoup, pandas)
data/
  sample/   # tiny CSVs to run offline
  raw/      # your full pulls live here (gitignored)
docs/       # rendered HTML site (enable GitHub Pages from /docs)
slides/     # final presentation (PDF)
```
## Quickstart
```bash
# 1) Python env for scrapers (optional)
python -m venv .venv && source .venv/bin/activate
pip install -r python/requirements.txt

# 2) (Optional) pull fresh data
# python python/team_passes_scraper.py
# python python/ALAAM_attribute_player_data_scraper.py

# 3) R: restore packages and render Quarto to docs/
# Inside R:
# install.packages(c("renv","quarto","tidyverse","igraph","statnet"))
# renv::init(); renv::snapshot()   # or renv::restore() if lockfile present
# quarto::quarto_render("analysis/Team21_SNAP_Final.qmd", output_dir="docs", output_file="index.html")
```

## Data
The sample files in `data/sample/` include:
- Three team-level **passing networks** for 2024–25 (Warriors, Knicks, Blazers)
- One league-wide **ALAAM attribute** sample CSV for 2023–24

Use these to knit the paper quickly; place your larger pulls in `data/raw/` (gitignored).

## Results summary (from slides/paper)
- Lower **assist-network** average path length correlates with more team wins.
- **In-degree** (receiving from more teammates) is strongly associated with 20+ PPG (ALAAM).
- Evidence of **negative scoring contagion**: being closely tied to high scorers reduces odds of being a high scorer.
(See the presentation PDF in `slides/` and the paper for figures and full details.)

## License
MIT
