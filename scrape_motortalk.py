"""Scrape motor-talk.de boards for the target models.

1. Read listing pages of each board in BOARDS (40 threads per request).
   Every thread is assigned to a model by its car tag, falling back to its
   title, and recorded in threads_scanned (http_status NULL = listed only).
   This listed count is the denominator for normalization.
2. Read up to THREADS_PER_MODEL threads per model, preferring threads
   whose title already contains a trigger keyword or part word, then newest.

Usage: python scrape_motortalk.py [threads_per_model] [max_listing_pages]
"""

import json
import re
import sys
from datetime import datetime, timezone

import db
import motortalk
from fetch import Fetcher

# brand -> boards to scan, picked from discover_boards.py output (boards.json)
_F = "https://www.motor-talk.de/forum/"
BOARDS = {
    "BMW": [_F + b for b in ("bmw-3er-e21-e30-b55.html", "bmw-5er-e34-b276.html", "bmw-3er-e36-b56.html",
                             "bmw-5er-e39-b277.html", "bmw-youngtimer-oldtimer-b1118.html",
                             "bmw-6er-7er-8er-klassiker-b1119.html")],
    "Mercedes": [_F + b for b in ("mercedes-e-klasse-w124-b153.html", "mercedes-190er-b150.html",
                                  "mercedes-s-klasse-c140-w108-w109-w116-w126-w140-b1098.html",
                                  "mercedes-sl-b74.html", "mercedes-youngtimer-oldtimer-b893.html")],
    "Audi": [_F + b for b in ("audi-80-90-100-200-v8-b158.html", "audi-a6-4a-b307.html",
                              "audi-a4-b5-b305.html", "audi-a8-d2-b310.html")],
    "Porsche": [_F + "porsche-b26.html"],
    "VW": [_F + b for b in ("vw-golf-1-2-b145.html", "vw-golf-3-b146.html", "vw-scirocco-1-2-corrado-b723.html",
                            "vw-t1-t2-t3-b218.html")],
}

MAX_THREAD_PAGES = 3  # long threads: read the first pages only


def compile_models(conn):
    by_brand = {}
    for m in conn.execute("SELECT id, brand FROM models ORDER BY id"):
        aliases = [r["alias"] for r in conn.execute("SELECT alias FROM model_aliases WHERE model_id = ?", (m["id"],))]
        by_brand.setdefault(m["brand"], []).append((m["id"], [re.compile(a, re.IGNORECASE) for a in aliases]))
    return by_brand


def resolve_model(models, car_tag, title):
    # Fall back to the title only for vague tags like "BMW" or "BMW 3er",
    # not for specific ones of untracked models like "BMW 3er E21"
    vague = len(car_tag.split()) <= 2 and "(" not in car_tag
    for text in (car_tag, title) if vague else (car_tag,):
        for model_id, patterns in models:
            if text and any(p.search(text) for p in patterns):
                return model_id
    return None


def hint_pattern(conn):
    words = [r["phrase"] for r in conn.execute("SELECT phrase FROM keywords")]
    words += [r["alias"] for r in conn.execute("SELECT alias FROM part_aliases")]
    words += ["ersatzteil", "gesucht", "nachbau", "3d"]
    return re.compile(r"\b(" + "|".join(re.escape(w) for w in words) + r")", re.IGNORECASE)


def main(threads_per_model=20, max_listing_pages=10):
    conn = db.connect()
    source_id = conn.execute("SELECT id FROM sources WHERE domain = 'motor-talk.de'").fetchone()["id"]
    models = compile_models(conn)
    hints = hint_pattern(conn)
    fetcher = Fetcher(scrub=motortalk.scrub)
    now = lambda: datetime.now(timezone.utc).isoformat(timespec="seconds")

    candidates = {}  # model_id -> {url: (has_hint, last_post)}
    for brand, boards in BOARDS.items():
        for board in boards:
            page, last_page = 1, 1
            while page <= min(last_page, max_listing_pages):
                status, body = fetcher.get(f"{board}?page={page}" if page > 1 else board)
                if status != 200:
                    print(f"listing {status} {board} p{page}", file=sys.stderr)
                    break
                data = json.loads(body)
                last_page = data["last_page"]
                for t in data["threads"]:
                    model_id = resolve_model(models[brand], t["car_tag"], t["title"])
                    if model_id is None:
                        continue
                    conn.execute(
                        "INSERT OR IGNORE INTO threads_scanned (url, source_id, model_id, fetched_at) VALUES (?, ?, ?, ?)",
                        (t["url"], source_id, model_id, now()),
                    )
                    candidates.setdefault(model_id, {})[t["url"]] = (bool(hints.search(t["title"])), t["last_post"])
                conn.commit()
                print(f"{brand} {board} p{page}/{last_page} requests={fetcher.network_requests}", flush=True)
                page += 1

    for model_id, threads in candidates.items():
        done = conn.execute(
            "SELECT COUNT(*) FROM threads_scanned WHERE model_id = ? AND http_status = 200", (model_id,)
        ).fetchone()[0]
        ordered = sorted(threads.items(), key=lambda kv: kv[1], reverse=True)
        for url, _ in ordered:
            if done >= threads_per_model:
                break
            row = conn.execute("SELECT http_status FROM threads_scanned WHERE url = ?", (url,)).fetchone()
            if row["http_status"] == 200:
                continue
            status, body = fetcher.get(url)
            if status == 200:
                last = min(json.loads(body)["last_page"], MAX_THREAD_PAGES)
                for p in range(2, last + 1):
                    fetcher.get(f"{url}?page={p}")
                done += 1
            conn.execute("UPDATE threads_scanned SET http_status = ?, fetched_at = ? WHERE url = ?", (status, now(), url))
            conn.commit()
        print(f"model {model_id}: {done} threads read, {len(threads)} listed, requests={fetcher.network_requests}", flush=True)


if __name__ == "__main__":
    args = [int(a) for a in sys.argv[1:]]
    main(*args)
