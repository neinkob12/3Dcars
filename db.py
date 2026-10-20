"""SQLite schema and connection helper (schema approved in docs/PHASE1_PROPOSAL.md)."""

import sqlite3
from pathlib import Path

DB_PATH = Path(__file__).parent / "research.sqlite"

SCHEMA = """
CREATE TABLE IF NOT EXISTS models (
  id            INTEGER PRIMARY KEY,
  brand         TEXT NOT NULL,
  model_name    TEXT NOT NULL,
  chassis_code  TEXT NOT NULL,
  year_from     INTEGER,
  year_to       INTEGER,
  UNIQUE (brand, chassis_code)
);
CREATE TABLE IF NOT EXISTS model_aliases (
  model_id  INTEGER NOT NULL REFERENCES models(id),
  alias     TEXT NOT NULL,              -- regex, matched against car tag and thread title
  UNIQUE (model_id, alias)
);
CREATE TABLE IF NOT EXISTS parts (
  id                  INTEGER PRIMARY KEY,
  canonical_name      TEXT NOT NULL UNIQUE,
  category            TEXT,
  oem_part_number     TEXT,
  model_id            INTEGER REFERENCES models(id),
  is_safety_relevant  INTEGER NOT NULL DEFAULT 0,
  size_class          TEXT,
  visible_surface     INTEGER
);
CREATE TABLE IF NOT EXISTS part_aliases (
  part_id  INTEGER NOT NULL REFERENCES parts(id),
  alias    TEXT NOT NULL,
  lang     TEXT NOT NULL,
  UNIQUE (part_id, alias)
);
CREATE TABLE IF NOT EXISTS keywords (
  id      INTEGER PRIMARY KEY,
  phrase  TEXT NOT NULL UNIQUE,
  lang    TEXT NOT NULL,
  kind    TEXT NOT NULL                 -- nla / broken / searching
);
CREATE TABLE IF NOT EXISTS sources (
  id                INTEGER PRIMARY KEY,
  domain            TEXT NOT NULL UNIQUE,
  robots_checked_at TEXT,
  terms_note        TEXT
);
CREATE TABLE IF NOT EXISTS threads_scanned (
  url         TEXT PRIMARY KEY,
  source_id   INTEGER NOT NULL REFERENCES sources(id),
  model_id    INTEGER REFERENCES models(id),
  fetched_at  TEXT NOT NULL,
  http_status INTEGER
);
CREATE TABLE IF NOT EXISTS mentions (
  id              INTEGER PRIMARY KEY,
  source_id       INTEGER NOT NULL REFERENCES sources(id),
  url             TEXT NOT NULL,
  post_date       TEXT,
  model_id        INTEGER REFERENCES models(id),
  part_id         INTEGER REFERENCES parts(id),
  oem_pn_found    TEXT,
  matched_phrase  TEXT NOT NULL,
  UNIQUE (url, matched_phrase, part_id)
);
CREATE TABLE IF NOT EXISTS scores (
  part_id         INTEGER NOT NULL REFERENCES parts(id),
  model_id        INTEGER NOT NULL REFERENCES models(id),
  mentions        INTEGER,
  mentions_recent INTEGER,
  threads_scanned INTEGER,
  volume          REAL,
  price_signal    REAL,
  unsolved        REAL,
  printability    REAL,
  score           REAL,
  computed_at     TEXT,
  PRIMARY KEY (part_id, model_id)
);
"""


def connect(path=DB_PATH):
    conn = sqlite3.connect(path)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    conn.executescript(SCHEMA)
    return conn
