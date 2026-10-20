"""motor-talk.de page parsers.

`scrub` turns a raw page into a small JSON document before it is cached.
Only titles, car tags, post ids, post dates and post text are kept: no
usernames, avatars or profile links. Quoted replies are dropped because
they start with "Zitat von <name>".
"""

import json
import re

from selectolax.parser import HTMLParser

BASE = "https://www.motor-talk.de"


def _last_page(tree):
    pages = [1]
    for a in tree.css(".Pagination a, a.PaginationButton"):
        m = re.search(r"[?&]page=(\d+)", a.attributes.get("href") or "")
        if m:
            pages.append(int(m.group(1)))
    return max(pages)


def _abs(href):
    return BASE + href if href.startswith("/") else href


def _car_tag(node):
    tag = node.css_first(".CarTag .Tag-text") if node else None
    return re.sub(r"\s+", " ", tag.text()).strip() if tag else ""


def parse_board(tree):
    boards = []
    for a in tree.css("a.BoardLink"):
        href = a.attributes.get("href") or ""
        title = a.css_first(".BoardItem-title")
        counters = [c.text(strip=True) for c in a.css(".BoardItem-counter")]
        boards.append({
            "url": _abs(href),
            "title": title.text(strip=True) if title else "",
            "counts": counters,
        })
    threads = []
    for a in tree.css('a[data-testid="thread-list-item"]'):
        href = a.attributes.get("href") or ""
        title = a.css_first(".ThreadListItem-title")
        time = a.css_first("time")
        threads.append({
            "url": _abs(href.split("?")[0]),
            "title": title.text(strip=True) if title else "",
            "car_tag": _car_tag(a),
            "last_post": time.attributes.get("datetime", "") if time else "",
        })
    return {"kind": "board", "boards": boards, "threads": threads, "last_page": _last_page(tree)}


def parse_thread(tree):
    title = tree.css_first(".DiscussionThreadHeader-headline")
    posts = []
    for post in tree.css("section.Post"):
        body = post.css_first(".PostBody")
        if body is None:
            continue
        for quote in body.css("blockquote"):
            quote.decompose()
        date = post.css_first('meta[itemprop="datePublished"]')
        posts.append({
            "id": post.attributes.get("id", ""),
            "date": (date.attributes.get("content", "") if date else "")[:10],
            "text": body.text(separator=" ", strip=True),
        })
    crumbs = [b.text(strip=True) for b in tree.css(".Breadcrumbs .BreadcrumbItem")]
    return {
        "kind": "thread",
        "title": title.text(strip=True) if title else "",
        "car_tag": _car_tag(tree.body),
        "crumbs": list(dict.fromkeys(crumbs)),
        "posts": posts,
        "last_page": _last_page(tree),
    }


def scrub(html):
    tree = HTMLParser(html)
    if tree.css_first("section.Post"):
        return json.dumps(parse_thread(tree), ensure_ascii=False)
    return json.dumps(parse_board(tree), ensure_ascii=False)
