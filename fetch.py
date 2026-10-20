"""Polite HTTP fetcher: robots.txt check, per-domain rate limit, gzip disk cache.

Pages are passed through a source-specific `scrub` function before they are
cached, so author names and profile links never touch the disk.
"""

import gzip
import hashlib
import time
import urllib.robotparser
from pathlib import Path
from urllib.parse import urlparse

import httpx

USER_AGENT = "3Dcars-research/0.1 (NLA parts demand study; low volume)"
DELAY_SECONDS = 5.0
CACHE_DIR = Path(__file__).parent / "cache"


class Fetcher:
    def __init__(self, scrub=None, delay=DELAY_SECONDS, cache_dir=CACHE_DIR):
        self.scrub = scrub or (lambda html: html)
        self.delay = delay
        self.cache_dir = Path(cache_dir)
        self.cache_dir.mkdir(exist_ok=True)
        self.client = httpx.Client(
            headers={"User-Agent": USER_AGENT, "Accept-Language": "de,en;q=0.8"},
            timeout=30,
            follow_redirects=True,
        )
        self._robots = {}
        self._last_request = {}
        self.network_requests = 0

    def _cache_path(self, url):
        return self.cache_dir / (hashlib.sha256(url.encode()).hexdigest()[:32] + ".html.gz")

    def allowed(self, url):
        host = urlparse(url).netloc
        if host not in self._robots:
            rp = urllib.robotparser.RobotFileParser()
            self._wait(host)
            resp = self.client.get(f"https://{host}/robots.txt")
            rp.parse(resp.text.splitlines() if resp.status_code == 200 else [])
            self._robots[host] = rp
        return self._robots[host].can_fetch(USER_AGENT, url)

    def _wait(self, host):
        elapsed = time.monotonic() - self._last_request.get(host, 0)
        if elapsed < self.delay:
            time.sleep(self.delay - elapsed)
        self._last_request[host] = time.monotonic()
        self.network_requests += 1

    def cached(self, url):
        """Return the cached page or None, never touching the network."""
        path = self._cache_path(url)
        return gzip.decompress(path.read_bytes()).decode("utf-8") if path.exists() else None

    def get(self, url):
        """Return (status, html). Cached pages return status 200 without a request."""
        cached = self.cached(url)
        if cached is not None:
            return 200, cached
        path = self._cache_path(url)
        if not self.allowed(url):
            return 999, ""  # blocked by robots.txt
        host = urlparse(url).netloc
        for attempt in range(4):
            self._wait(host)
            try:
                resp = self.client.get(url)
            except httpx.TransportError:
                time.sleep(self.delay * 2 ** (attempt + 1))
                continue
            if resp.status_code == 429 or resp.status_code >= 500:
                time.sleep(self.delay * 2 ** (attempt + 1))
                continue
            if resp.status_code != 200:
                return resp.status_code, ""
            html = self.scrub(resp.text)
            path.write_bytes(gzip.compress(html.encode("utf-8")))
            return 200, html
        return 0, ""
