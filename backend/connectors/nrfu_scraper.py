"""
NRFU extractor prototype.

Usage:
    python nrfu_scraper.py

Behavior:
  - Tries WP REST API: https://nrfu.org.ua/wp-json/wp/v2/posts?per_page=5&search=конкурс
  - If REST is not reachable or returns unexpected data, falls back to scraping https://nrfu.org.ua/contests/current-calls/
  - Saves raw JSON / HTML and writes normalized sample(s) to `data/`.

Be polite: this is a simple prototype. For production use add retries, rate-limiting and caching.
"""
from __future__ import annotations

"""NRFU extractor prototype with deferred imports for HTTP libs and BS4.

Design:
- Network calls import requests inside functions.
- Normalization logic is lightweight and can be tested separately.
"""

import json
import re
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List


WP_API = "https://nrfu.org.ua/wp-json/wp/v2/posts"
CONTESTS_PAGE = "https://nrfu.org.ua/contests/current-calls/"
DATA_DIR = Path(__file__).resolve().parents[2] / "data"
DATA_DIR.mkdir(parents=True, exist_ok=True)


def _make_session_with_retries():
    import requests
    from requests.adapters import HTTPAdapter
    from urllib3.util.retry import Retry

    session = requests.Session()
    retries = Retry(total=3, backoff_factor=0.5, status_forcelist=(500, 502, 503, 504))
    adapter = HTTPAdapter(max_retries=retries)
    session.mount("https://", adapter)
    session.mount("http://", adapter)
    session.headers.update({"User-Agent": "nrfu-harvester/0.1 (+https://example.org)"})
    return session


def fetch_wp_posts(search: str = "конкурс", per_page: int = 5) -> List[Dict[str, Any]]:
    params = {"per_page": per_page, "search": search}
    session = _make_session_with_retries()
    resp = session.get(WP_API, params=params, timeout=20)
    resp.raise_for_status()
    return resp.json()


def scrape_contests_page() -> List[Dict[str, Any]]:
    import requests
    from bs4 import BeautifulSoup

    resp = requests.get(CONTESTS_PAGE, timeout=20)
    resp.raise_for_status()
    html = resp.text
    soup = BeautifulSoup(html, "lxml")
    # Look for links to PDFs or contest detail pages
    links = []
    for a in soup.select("a[href]"):
        href = a["href"]
        if re.search(r"umovy|umovy_konkursu|wp-content/.+\.pdf|grants", href, re.I):
            links.append({"text": a.get_text(strip=True), "href": href})
    # Build minimal records
    records = []
    for l in links[:5]:
        records.append({"title": l.get("text") or "contest", "link": l.get("href")})
    return records


def _strip_html_to_text(html: str) -> str:
    # Lightweight HTML stripper that does not require heavy parsing when bs4 isn't available.
    # Used as a fallback inside normalize_wp_post. For full parsing, BeautifulSoup is used when available.
    text = re.sub(r"<[^>]+>", "", html)
    return re.sub(r"\s+", " ", text).strip()


def normalize_wp_post(post: Dict[str, Any]) -> Dict[str, Any]:
    # Try to extract rendered HTML safely; avoid importing bs4 at module import time.
    content = post.get("content", {}).get("rendered", "")
    attachments: List[str] = []
    text = _strip_html_to_text(content)
    try:
        # If bs4 is available, use it to find attachments and cleaner text
        from bs4 import BeautifulSoup

        soup = BeautifulSoup(content, "lxml")
        text = soup.get_text(separator="\n", strip=True)
        for a in soup.find_all("a", href=True):
            href = a["href"]
            if href.lower().endswith((".pdf", ".docx", ".doc")):
                attachments.append(href)
    except Exception:
        # bs4 not available — fallback to simple regex-based extraction of links
        for m in re.finditer(r"href=[\"']([^\"']+\.(?:pdf|docx|doc))[\"']", content, re.I):
            attachments.append(m.group(1))

    return {
        "source": "nrfu.org.ua",
        "source_id": post.get("id"),
        "title": post.get("title", {}).get("rendered"),
        "link": post.get("link"),
        "date": post.get("date"),
        "summary_text": text[:1000],
        "attachments": attachments,
    }


def save_samples():
    fetched_at = datetime.utcnow().isoformat() + "Z"
    try:
        posts = fetch_wp_posts(search="конкурс", per_page=5)
        raw_path = DATA_DIR / "nrfu_wp_raw.json"
        with open(raw_path, "w", encoding="utf-8") as f:
            json.dump({"fetched_at": fetched_at, "source_url": WP_API, "payload": posts}, f, ensure_ascii=False, indent=2)

        normalized = [normalize_wp_post(p) for p in posts]
        sample_path = DATA_DIR / "nrfu_contest_sample_wp.json"
        with open(sample_path, "w", encoding="utf-8") as f:
            json.dump({"fetched_at": fetched_at, "normalized": normalized}, f, ensure_ascii=False, indent=2)
        print(f"Saved WP API samples -> {sample_path}")
    except Exception as e:
        print("WP REST API fetch failed, falling back to HTML scraping:", e)
        records = scrape_contests_page()
        raw_path = DATA_DIR / "nrfu_contests_page_links.json"
        with open(raw_path, "w", encoding="utf-8") as f:
            json.dump({"fetched_at": fetched_at, "source_url": CONTESTS_PAGE, "links": records}, f, ensure_ascii=False, indent=2)
        # Turn the links into normalized stubs
        normalized = []
        for r in records:
            normalized.append({"source": "nrfu.org.ua", "title": r.get("title"), "link": r.get("link")})
        sample_path = DATA_DIR / "nrfu_contest_sample_scraped.json"
        with open(sample_path, "w", encoding="utf-8") as f:
            json.dump({"fetched_at": fetched_at, "normalized": normalized}, f, ensure_ascii=False, indent=2)
        print(f"Saved scraped samples -> {sample_path}")


if __name__ == "__main__":
    save_samples()
