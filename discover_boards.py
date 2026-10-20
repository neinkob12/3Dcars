"""Map the motor-talk.de subforum tree under the five brand boards.

Reads only board index pages (first page each). Writes boards.json with
each board's url, title, depth and parent, plus the car tags seen on its
first page of threads, which tells us how threads are tagged per model.

Usage: python discover_boards.py [max_depth]
"""

import json
import re
import sys
from collections import Counter

import motortalk
from fetch import Fetcher

ROOTS = {
    "BMW": "https://www.motor-talk.de/forum/bmw-b4.html",
    "Mercedes": "https://www.motor-talk.de/forum/mercedes-b20.html",
    "Audi": "https://www.motor-talk.de/forum/audi-b40.html",
    "Porsche": "https://www.motor-talk.de/forum/porsche-b26.html",
    "VW": "https://www.motor-talk.de/forum/volkswagen-b22.html",
}
# Series boards that can contain our target models (depth 1)
SERIES = ("bmw-3er", "bmw-5er", "bmw-6er-7er-8er", "youngtimer", "mercedes-e-klasse", "mercedes-s-klasse",
          "mercedes-sl-b", "mercedes-c-klasse", "audi-80-90", "audi-a4", "audi-a6", "audi-a8", "vw-golf",
          "vw-scirocco-corrado", "vw-transporter", "vw-nutzfahrzeuge")
# Chassis sub-boards worth descending into (depth 2+), matched on url slug and title
CHASSIS = re.compile(r"e ?(24|28|30|34|36|39)\b|[wr] ?(107|124|126|129|140|201)\b|\b(b ?[345]|c ?4|d ?2|typ ?(44|85))\b"
                     r"|golf[- ]?(1|2|3|i{1,3})\b|\bt ?3\b|corrado|scirocco|\b(80|90|100|200)\b", re.IGNORECASE)


def wanted(board, depth):
    if depth == 1:
        return any(s in board["url"] for s in SERIES)
    slug = re.sub(r"-b\d+\.html$", "", board["url"].rsplit("/", 1)[-1])
    return bool(CHASSIS.search(slug + " " + board["title"]))


def main(max_depth=3):
    fetcher = Fetcher(scrub=motortalk.scrub)
    seen, out = set(), []
    queue = [(url, brand, 0, None) for brand, url in ROOTS.items()]
    while queue:
        url, brand, depth, parent = queue.pop(0)
        if url in seen or "/forum/" not in url:
            continue
        seen.add(url)
        status, page = fetcher.get(url)
        if status != 200:
            print(f"skip {status} {url}", file=sys.stderr)
            continue
        data = json.loads(page)
        tags = Counter(t["car_tag"] for t in data["threads"])
        out.append({"brand": brand, "url": url, "depth": depth, "parent": parent,
                    "last_page": data["last_page"], "car_tags": dict(tags.most_common())})
        print(f"{'  ' * depth}{brand} d{depth} {url} pages={data['last_page']} tags={len(tags)}", flush=True)
        if depth < max_depth:
            for b in data["boards"]:
                if wanted(b, depth + 1) and b["url"] not in seen:
                    queue.append((b["url"], brand, depth + 1, url))
    with open("boards.json", "w") as f:
        json.dump(out, f, ensure_ascii=False, indent=1)
    print(f"done: {len(out)} boards, {fetcher.network_requests} requests", file=sys.stderr)


if __name__ == "__main__":
    main(int(sys.argv[1]) if len(sys.argv) > 1 else 3)
