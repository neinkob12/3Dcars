# 3Dcars

Research tooling for a 3D printed replacement car parts platform: find which discontinued (NLA) plastic parts have the most unmet demand.

Context: `car-parts-3d-cc-handoff.md`. Phase 1 decisions: `docs/PHASE1_PROPOSAL.md`.

## Setup

```sh
uv venv .venv --python 3.12
uv pip install --python .venv/bin/python -r requirements.txt
```

## Run

```sh
.venv/bin/python seed.py                    # models, keywords, parts into research.sqlite
.venv/bin/python discover_boards.py         # map motor-talk.de subforums -> boards.json
.venv/bin/python scrape_motortalk.py 20 10  # 20 threads per model, up to 10 listing pages per board
.venv/bin/python extract.py                 # rebuild mentions from the cache
.venv/bin/python score.py 3                 # ranked_parts.csv + model_summary.csv
.venv/bin/python -m pytest -q
```

Scraping is resumable: every page is cached in `cache/` (gitignored), and reruns never refetch.

## Rules the code follows

* robots.txt is checked before every new host. One request every 5 seconds per domain, backoff on 429/5xx.
* Pages are reduced to title, car tag, post id, post date and post text before caching. No usernames, avatars or profile links are stored anywhere.
* The database stores only source URL, date, model, part, OEM number and matched phrase.
