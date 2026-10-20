# Phase 1 Proposal (tasks 2 and 3)

Status: approved on 2026-10-20, with these changes:

* Models expanded from 15 to 30 (see table, second block).
* Source: motor-talk.de. Its terms (section 3.4) allow private use only and need consent from gutefrage for commercial use. The founder decided to run a low-volume test anyway.
* No contact email in the user agent.
* Test run: 20 threads per model.
* Normalization denominator is threads *listed* per model (from listing pages, 40 per request), not threads read. Threads read are picked title-first (titles that already hint at a part or NLA), so dividing by threads read would inflate every model equally and hide real differences.

## Task 2: SQLite schema

```sql
-- Target vehicles
CREATE TABLE models (
  id            INTEGER PRIMARY KEY,
  brand         TEXT NOT NULL,          -- BMW, Mercedes, Audi, Porsche, VW
  model_name    TEXT NOT NULL,          -- "3er", "E-Klasse", "944"
  chassis_code  TEXT NOT NULL,          -- E30, W124, 944
  year_from     INTEGER,
  year_to       INTEGER,
  UNIQUE (brand, chassis_code)
);

-- Spellings people use in posts: "E30", "3er E30", "190E" -> W201
CREATE TABLE model_aliases (
  model_id  INTEGER NOT NULL REFERENCES models(id),
  alias     TEXT NOT NULL,
  UNIQUE (model_id, alias)
);

-- Canonical parts
CREATE TABLE parts (
  id                  INTEGER PRIMARY KEY,
  canonical_name      TEXT NOT NULL,     -- "Schalterblende Mittelkonsole"
  category            TEXT,              -- clip, cover, vent, knob, holder, trim
  oem_part_number     TEXT,              -- NULL until known
  model_id            INTEGER REFERENCES models(id),  -- NULL = generic part type
  is_safety_relevant  INTEGER NOT NULL DEFAULT 0,
  size_class          TEXT,              -- S / M / L
  visible_surface     INTEGER,           -- 1 = finish critical
  UNIQUE (canonical_name, model_id)
);

-- DE/EN words that map to a part: "Lüftungsgitter", "air vent", "Luftdüse"
CREATE TABLE part_aliases (
  part_id  INTEGER NOT NULL REFERENCES parts(id),
  alias    TEXT NOT NULL,
  lang     TEXT NOT NULL,                -- de / en
  UNIQUE (part_id, alias)
);

-- Trigger phrases
CREATE TABLE keywords (
  id      INTEGER PRIMARY KEY,
  phrase  TEXT NOT NULL UNIQUE,          -- "nicht mehr lieferbar", "NLA"
  lang    TEXT NOT NULL,
  kind    TEXT NOT NULL                  -- nla / broken / searching
);

CREATE TABLE sources (
  id                INTEGER PRIMARY KEY,
  domain            TEXT NOT NULL UNIQUE,
  robots_checked_at TEXT,
  terms_note        TEXT
);

-- Crawl bookkeeping, also the denominator for normalization
CREATE TABLE threads_scanned (
  url         TEXT PRIMARY KEY,
  source_id   INTEGER NOT NULL REFERENCES sources(id),
  model_id    INTEGER REFERENCES models(id),
  fetched_at  TEXT NOT NULL,
  http_status INTEGER
);

-- One row per (post, matched phrase). No usernames, no profile links, no post text.
CREATE TABLE mentions (
  id              INTEGER PRIMARY KEY,
  source_id       INTEGER NOT NULL REFERENCES sources(id),
  url             TEXT NOT NULL,        -- thread URL + post anchor
  post_date       TEXT,                 -- ISO date
  model_id        INTEGER REFERENCES models(id),
  part_id         INTEGER REFERENCES parts(id),   -- NULL = NLA hit, part not recognized
  oem_pn_found    TEXT,                 -- OEM number matched by regex, if any
  matched_phrase  TEXT NOT NULL,
  UNIQUE (url, matched_phrase, part_id)
);

-- Output of the scoring script (rebuilt each run)
CREATE TABLE scores (
  part_id         INTEGER NOT NULL REFERENCES parts(id),
  model_id        INTEGER NOT NULL REFERENCES models(id),
  mentions        INTEGER,
  mentions_recent INTEGER,              -- last 5 years
  threads_scanned INTEGER,
  volume          REAL,
  price_signal    REAL,                 -- Phase 2, default 1.0
  unsolved        REAL,                 -- Phase 2, default 1.0
  printability    REAL,
  score           REAL,
  computed_at     TEXT,
  PRIMARY KEY (part_id, model_id)
);
```

How a mention gets created:

1. Post text contains a keyword (e.g. "nicht mehr lieferbar").
2. Model comes from the subforum the thread lives in (most reliable), aliases as fallback.
3. Part comes from the part alias dictionary in the same post, plus regex for OEM number formats (BMW `51 41 1 234 567`, Mercedes `A 124 680 12 34`, VW/Audi `443 867 171 A`).
4. If no part is recognized, the mention is still stored with `part_id = NULL` so I can review them and grow the alias list.

## Task 2: Scoring formula

```
volume       = (mentions + 1.0 * mentions_recent) / threads_scanned_for_model * 1000
printability = 0 if safety relevant
               else size factor (S 1.0, M 0.8, L 0.4) * (0.7 if visible_surface else 1.0)
price_signal = 1.0   (Phase 2: eBay used prices)
unsolved     = 1.0   (Phase 2: competitor catalog check)

score = volume * price_signal * unsolved * printability
```

Notes:

* Recent mentions count double, because a part that was NLA in 2009 may be back in stock now.
* Normalizing by threads scanned stops the huge E30/Golf communities from winning just by size.
* A minimum of 3 mentions is required to be ranked, so single posts do not top the list.

`ranked_parts.csv` columns:

`rank, brand, chassis_code, part, oem_part_number, mentions, mentions_recent, threads_scanned, volume, printability, price_signal, unsolved, score, example_urls`

## Task 3: Keyword list (seed)

| Kind | German | English |
|---|---|---|
| nla | nicht mehr lieferbar, nicht lieferbar, NLA, entfallen, ersatzlos entfallen, nicht mehr erhältlich, gibt es nicht mehr, Teil ausgelaufen | no longer available, NLA, discontinued, not available anymore, out of production |
| broken | abgebrochen, gebrochen, Clip gebrochen, Halter gebrochen, Nase abgebrochen, zerbröselt, porös, gerissen | broken, snapped, cracked, crumbled, brittle |
| searching | Ersatzteil gesucht, suche, wo bekomme ich, Bezugsquelle, hat jemand noch | looking for, where to find, anyone have, source for |

Matching rule: a post must contain at least one `nla` phrase, OR one `broken` plus one `searching` phrase. A `broken` hit alone is too noisy (people break parts that are still available).

## Task 3: 15 target models

Three per brand, chosen for mid to upper tier enthusiast cars with lots of interior plastic.

| Brand | Chassis | Model | Years |
|---|---|---|---|
| BMW | E30 | 3er | 1982 to 1994 |
| BMW | E34 | 5er | 1988 to 1996 |
| BMW | E36 | 3er (incl. M3, Compact) | 1990 to 2000 |
| Mercedes | W124 | E-Klasse / 200 to 300 | 1984 to 1997 |
| Mercedes | W201 | 190 / 190E | 1982 to 1993 |
| Mercedes | W126 | S-Klasse | 1979 to 1991 |
| Audi | B3/B4 | 80, 90, Coupé, Cabrio | 1986 to 2000 |
| Audi | Typ 44 | 100 / 200 | 1982 to 1991 |
| Audi | C4 | 100 / A6 | 1990 to 1997 |
| Porsche | 944/968 | 944, 968 | 1982 to 1995 |
| Porsche | 964 | 911 | 1989 to 1994 |
| Porsche | 928 | 928 | 1977 to 1995 |
| VW | Golf 2 | Golf / Jetta 2 (GTI, G60) | 1983 to 1992 |
| VW | Corrado | Corrado | 1988 to 1995 |
| VW | T3 | Transporter / Bulli | 1979 to 1992 |

Added after approval:

| Brand | Chassis | Model | Years |
|---|---|---|---|
| BMW | E28 | 5er | 1981 to 1988 |
| BMW | E24 | 6er | 1976 to 1989 |
| BMW | E39 | 5er | 1995 to 2004 |
| Mercedes | R129 | SL | 1989 to 2001 |
| Mercedes | W140 | S-Klasse | 1991 to 1998 |
| Mercedes | R107 | SL | 1971 to 1989 |
| Audi | B5 | A4 | 1994 to 2001 |
| Audi | Typ 85 | Coupé / Ur-quattro | 1980 to 1991 |
| Audi | D2 | A8 | 1994 to 2002 |
| Porsche | 993 | 911 | 1993 to 1998 |
| Porsche | 986 | Boxster | 1996 to 2004 |
| Porsche | 924 | 924 | 1976 to 1988 |
| VW | Golf 1 | Golf 1 / Cabrio | 1974 to 1993 |
| VW | Golf 3 | Golf 3 / Vento | 1991 to 1999 |
| VW | Scirocco 2 | Scirocco | 1981 to 1992 |

BMW stays in as a benchmark: if BMW shows high demand but is already served by Treedy/DoviWorks, that calibrates what "high" means for the others.

## Task 3: Candidate forum sources

Checked on 2026-10-20.

| Source | Coverage | robots.txt | Terms | Verdict |
|---|---|---|---|---|
| **motor-talk.de** | German, all 5 brands, one subforum per model | `User-agent: *` allowed except `/suche.html` (site search) and `/out`. Blocks GPTBot and a list of SEO bots. | Could not verify automatically. Founder should read the Nutzungsbedingungen before the first run. | **Recommended PoC.** One scraper covers all 15 models in the same format, so cross-brand comparison is fair. We crawl subforum listings, never the search page. |
| forums.pelicanparts.com | English, Porsche heavy, also BMW/Mercedes/VW | Allows all. Crawl-delay 2 for Claude agents. | Not readable: site sits behind a Cloudflare bot challenge. | **Not for Phase 1.** Getting past the challenge would mean circumventing bot protection. Good Phase 2 option if Pelican grants permission. |
| w124-board.de | German, W124 only | Generic crawlers allowed, but **ClaudeBot and Claude-Web are explicitly `Disallow: /`**. | Not checked. | **Excluded.** The operator clearly does not want Claude-related crawling, so we respect that even with our own user agent. |

Also checked and excluded: benzworld.org and vwvortex.com (same network) explicitly block anthropic-ai and ClaudeBot. rennlist.com returns 403 to non-browser clients.

## Crawl plan for motor-talk.de

* User agent that names the project and a contact email.
* 1 request every 5 seconds, single thread, back off on 429/5xx.
* Disk cache keyed by URL, so reruns never refetch. Author blocks are stripped from the HTML before it is cached, so no usernames land on disk.
* Budget: newest 200 threads per model subforum = about 3,000 thread pages plus listing pages. At 5 s each that is roughly 4 to 5 hours, runnable overnight and resumable.

## Questions for you

1. Approve the schema and the scoring formula?
2. Approve the 15 models, or swap any (e.g. R129 SL instead of W126, Golf 1 Cabrio instead of T3)?
3. Approve motor-talk.de as the single PoC source, and will you read its Nutzungsbedingungen first?
4. Contact email for the scraper's user agent?
5. Is 200 threads per model a good first budget, or do you want a smaller smoke test first (e.g. 20 per model)?
