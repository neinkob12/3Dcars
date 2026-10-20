"""Rebuild the mentions table from cached thread pages.

A post counts as a mention when it contains an `nla` phrase, or a `broken`
plus a `searching` phrase and a recognized part. Parts are looked up in a
window around the trigger phrase, falling back to the thread title.

Usage: python extract.py
"""

import json
import re

import db
import motortalk
from fetch import Fetcher
from seed_data import OEM_PATTERNS

WINDOW = 150  # characters on each side of the trigger phrase


def compile_keywords(conn):
    out = {"nla": [], "broken": [], "searching": []}
    for row in conn.execute("SELECT phrase, kind FROM keywords"):
        phrase = row["phrase"]
        # Short all-caps codes like NLA must match case-sensitively ("Anlage")
        flags = 0 if phrase.isupper() else re.IGNORECASE
        out[row["kind"]].append((phrase, re.compile(r"\b" + re.escape(phrase) + r"\b", flags)))
    for kind in out:  # longest phrase first, so "ersatzlos entfallen" beats "entfallen"
        out[kind].sort(key=lambda kw: -len(kw[0]))
    return out


def compile_parts(conn):
    parts = []
    for p in conn.execute("SELECT id, canonical_name FROM parts"):
        aliases = [r["alias"] for r in conn.execute("SELECT alias FROM part_aliases WHERE part_id = ?", (p["id"],))]
        pattern = re.compile(r"\b(" + "|".join(re.escape(a) for a in aliases) + r")", re.IGNORECASE)
        parts.append((p["id"], "(allgemein)" in p["canonical_name"], pattern))
    return parts


def find_parts(parts, text):
    found = [(pid, generic) for pid, generic, pattern in parts if pattern.search(text)]
    specific = [pid for pid, generic in found if not generic]
    return specific or [pid for pid, _ in found]


def first_hit(keywords, text):
    for phrase, pattern in keywords:
        m = pattern.search(text)
        if m:
            return phrase, m
    return None, None


def post_mentions(text, title, keywords, parts, oem_pattern):
    """Return [(matched_phrase, part_id or None, oem_pn or None)] for one post."""
    phrase, m = first_hit(keywords["nla"], text)
    require_part = False
    if not phrase:
        broken, m = first_hit(keywords["broken"], text)
        searching, _ = first_hit(keywords["searching"], text)
        if not (broken and searching):
            return []
        phrase, require_part = f"{broken} + {searching}", True
    window = text[max(0, m.start() - WINDOW): m.end() + WINDOW]
    part_ids = find_parts(parts, window) or find_parts(parts, title)
    if require_part and not part_ids:
        return []
    oem = re.search(oem_pattern, window) if oem_pattern else None
    oem_pn = re.sub(r"[ .-]", "", oem.group(0)) if oem else None
    return [(phrase, pid, oem_pn) for pid in (part_ids or [None])]


def main():
    conn = db.connect()
    keywords, parts = compile_keywords(conn), compile_parts(conn)
    brands = {r["id"]: r["brand"] for r in conn.execute("SELECT id, brand FROM models")}
    source_id = conn.execute("SELECT id FROM sources WHERE domain = 'motor-talk.de'").fetchone()["id"]
    fetcher = Fetcher(scrub=motortalk.scrub)
    conn.execute("DELETE FROM mentions")
    threads = conn.execute(
        "SELECT url, model_id FROM threads_scanned WHERE http_status = 200 AND source_id = ?", (source_id,)
    ).fetchall()
    rows = 0
    for t in threads:
        oem_pattern = OEM_PATTERNS.get(brands.get(t["model_id"]))
        page_url, page_no = t["url"], 1
        while True:
            cached = fetcher.cached(page_url)
            if cached is None:
                break
            data = json.loads(cached)
            for i, post in enumerate(data["posts"]):
                text = (data["title"] + ". " if page_no == 1 and i == 0 else "") + post["text"]
                for phrase, part_id, oem_pn in post_mentions(text, data["title"], keywords, parts, oem_pattern):
                    conn.execute(
                        "INSERT OR IGNORE INTO mentions (source_id, url, post_date, model_id, part_id, oem_pn_found, matched_phrase)"
                        " VALUES (?, ?, ?, ?, ?, ?, ?)",
                        (source_id, f"{t['url']}#{post['id']}", post["date"], t["model_id"], part_id, oem_pn, phrase),
                    )
                    rows += 1
            page_no += 1
            if page_no > data["last_page"]:
                break
            page_url = f"{t['url']}?page={page_no}"
    conn.commit()
    print(f"{len(threads)} threads, {rows} mentions")


if __name__ == "__main__":
    main()
