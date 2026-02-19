"""CKAN connector — safe-to-import normalizer + simple session helper.

Design goals:
- Keep normalization logic free of heavy external deps so unit tests can import it
  without installing HTTP/HTML libraries.
- Use a small requests.Session with retries for live fetches.
"""

from __future__ import annotations

import json
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List


BASE_URL = "https://data.gov.ua/api/3/action/package_search"
DATA_DIR = Path(__file__).resolve().parents[2] / "data"
DATA_DIR.mkdir(parents=True, exist_ok=True)


def _make_session_with_retries():
    # Deferred import to avoid requiring requests at import time for unit tests.
    import requests
    from requests.adapters import HTTPAdapter
    from urllib3.util.retry import Retry

    session = requests.Session()
    retries = Retry(total=3, backoff_factor=0.5, status_forcelist=(500, 502, 503, 504))
    adapter = HTTPAdapter(max_retries=retries)
    session.mount("https://", adapter)
    session.mount("http://", adapter)
    session.headers.update({"User-Agent": "grant-harvester/0.1 (+https://example.org)"})
    return session


def search_ckan(q: str, rows: int = 20) -> Dict[str, Any]:
    """Run a CKAN package_search (uses `q` parameter).

    Raises requests.HTTPError on non-200 responses.
    """
    # Deferred import so callers can import normalize_ckan_result without requests installed.
    params = {"q": q, "rows": rows}
    session = _make_session_with_retries()
    resp = session.get(BASE_URL, params=params, timeout=30)
    resp.raise_for_status()
    return resp.json()


def normalize_ckan_result(payload: Dict[str, Any]) -> List[Dict[str, Any]]:
    """Normalize CKAN package_search result into a simple opportunity-like shape.

    This function has no external runtime deps so it is easy to unit-test.
    """
    res: List[Dict[str, Any]] = []
    result = payload.get("result", {})
    packages = result.get("results", [])
    for pkg in packages:
        normalized = {
            "source": "data.gov.ua",
            "source_id": pkg.get("id"),
            "title": pkg.get("title"),
            "description": pkg.get("notes"),
            "tags": [t.get("name") for t in pkg.get("tags", [])],
            "resources": [r.get("url") or r.get("cache_url") for r in pkg.get("resources", []) if r.get("url") or r.get("cache_url")],
            "metadata_modified": pkg.get("metadata_modified"),
        }
        res.append(normalized)
    return res


def save_raw_and_normalized(q: str, rows: int = 20) -> None:
    fetched_at = datetime.utcnow().isoformat() + "Z"
    payload = search_ckan(q, rows=rows)

    raw_path = DATA_DIR / "ckan_raw.json"
    sample_path = DATA_DIR / "ckan_sample_normalized.json"

    with open(raw_path, "w", encoding="utf-8") as f:
        json.dump({"fetched_at": fetched_at, "source_url": BASE_URL, "params": {"q": q, "rows": rows}, "payload": payload}, f, ensure_ascii=False, indent=2)

    normalized = normalize_ckan_result(payload)
    with open(sample_path, "w", encoding="utf-8") as f:
        json.dump({"fetched_at": fetched_at, "source": "data.gov.ua", "query": q, "normalized_results": normalized}, f, ensure_ascii=False, indent=2)


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser()
    parser.add_argument("--q", default="грант", help="CKAN search query (q)")
    parser.add_argument("--rows", type=int, default=20)
    args = parser.parse_args()
    print(f"Running CKAN query q={args.q} rows={args.rows} -> saving to {DATA_DIR}")
    save_raw_and_normalized(args.q, rows=args.rows)
