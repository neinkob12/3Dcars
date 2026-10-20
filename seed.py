"""Load seed_data.py into the database. Safe to rerun.

Usage: python seed.py
"""

import db
from seed_data import KEYWORDS, MODELS, PARTS


def main():
    conn = db.connect()
    for brand, name, chassis, y0, y1, aliases in MODELS:
        conn.execute(
            "INSERT OR IGNORE INTO models (brand, model_name, chassis_code, year_from, year_to) VALUES (?, ?, ?, ?, ?)",
            (brand, name, chassis, y0, y1),
        )
        model_id = conn.execute("SELECT id FROM models WHERE brand = ? AND chassis_code = ?", (brand, chassis)).fetchone()["id"]
        for alias in aliases:
            conn.execute("INSERT OR IGNORE INTO model_aliases (model_id, alias) VALUES (?, ?)", (model_id, alias))
    for phrase, lang, kind in KEYWORDS:
        conn.execute("INSERT OR IGNORE INTO keywords (phrase, lang, kind) VALUES (?, ?, ?)", (phrase, lang, kind))
    for name, category, size, visible, safety, aliases in PARTS:
        conn.execute(
            "INSERT OR IGNORE INTO parts (canonical_name, category, size_class, visible_surface, is_safety_relevant)"
            " VALUES (?, ?, ?, ?, ?)",
            (name, category, size, visible, safety),
        )
        part_id = conn.execute("SELECT id FROM parts WHERE canonical_name = ?", (name,)).fetchone()["id"]
        for alias, lang in aliases:
            conn.execute("INSERT OR IGNORE INTO part_aliases (part_id, alias, lang) VALUES (?, ?, ?)", (part_id, alias, lang))
    conn.execute(
        "INSERT OR IGNORE INTO sources (domain, robots_checked_at, terms_note) VALUES (?, ?, ?)",
        ("motor-talk.de", "2026-10-20",
         "robots.txt allows * except /suche.html and /out. Terms 3.4: private use only, "
         "commercial use needs consent from gutefrage. Founder chose to run a low-volume test anyway."),
    )
    conn.commit()
    counts = {t: conn.execute(f"SELECT COUNT(*) FROM {t}").fetchone()[0] for t in ("models", "keywords", "parts", "part_aliases")}
    print(counts)


if __name__ == "__main__":
    main()
