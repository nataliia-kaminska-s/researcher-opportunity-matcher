"""Ingest normalized JSON samples into a local SQLite staging DB.

Usage:
  python backend/ingest/ingest_to_sqlite.py --db data/opportunities.db --data-dir data --pattern "*_sample_*.json"

This script is intentionally dependency-free (uses stdlib only) so it works in minimal environments.
"""
from __future__ import annotations

import json
import sqlite3
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, Iterable


DEFAULT_DB = Path(__file__).resolve().parents[2] / "data" / "opportunities.db"


def find_normalized_files(data_dir: Path, pattern: str) -> Iterable[Path]:
    for p in sorted(data_dir.glob(pattern)):
        if p.is_file():
            yield p


def load_normalized_from_file(path: Path) -> Iterable[Dict[str, Any]]:
    with open(path, "r", encoding="utf-8") as f:
        payload = json.load(f)

    # Support a few shapes: {"normalized": [...]}, {"normalized_results": [...]}, or a single object
    if isinstance(payload, dict):
        if "normalized" in payload and isinstance(payload["normalized"], list):
            for item in payload["normalized"]:
                yield item
            return
        if "normalized_results" in payload and isinstance(payload["normalized_results"], list):
            for item in payload["normalized_results"]:
                yield item
            return
        # If the dict itself looks like a normalized record (has 'source' and 'title')
        if "source" in payload and ("title" in payload or "summary_text" in payload):
            yield payload
            return

    if isinstance(payload, list):
        for item in payload:
            yield item


def ensure_table(conn: sqlite3.Connection, table: str) -> None:
    conn.execute(f"""
    CREATE TABLE IF NOT EXISTS {table} (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        source TEXT,
        source_id TEXT,
        title TEXT,
        description TEXT,
        link TEXT,
        attachments_json TEXT,
        raw_path TEXT,
        normalized_path TEXT,
        fetched_at TEXT,
        inserted_at TEXT
    )
    """)
    conn.commit()


def insert_record(conn: sqlite3.Connection, table: str, rec: Dict[str, Any], raw_path: str, normalized_path: str) -> None:
    now = datetime.utcnow().isoformat() + "Z"
    conn.execute(
        f"INSERT INTO {table} (source, source_id, title, description, link, attachments_json, raw_path, normalized_path, fetched_at, inserted_at) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
        (
            rec.get("source"),
            str(rec.get("source_id")) if rec.get("source_id") is not None else None,
            rec.get("title"),
            rec.get("description") or rec.get("summary_text"),
            rec.get("link") or None,
            json.dumps(rec.get("attachments") or rec.get("resources") or [], ensure_ascii=False),
            raw_path,
            normalized_path,
            rec.get("date") or rec.get("fetched_at") or None,
            now,
        ),
    )


def ingest(db_path: Path, data_dir: Path, pattern: str = "*_sample_*.json", table: str = "staging_opportunities") -> None:
    data_dir = data_dir.resolve()
    db_path.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(str(db_path))
    ensure_table(conn, table)

    files = list(find_normalized_files(data_dir, pattern))
    if not files:
        print(f"No files matching {pattern} in {data_dir}")
        return

    for nf in files:
        print(f"Processing {nf}")
        # Try to find an accompanying raw file if present (ckan_raw.json / nrfu_wp_raw.json)
        raw_candidates = [nf.parent / "ckan_raw.json", nf.parent / "nrfu_wp_raw.json", nf.parent / "nrfu_contests_page_links.json"]
        raw_path = None
        for c in raw_candidates:
            if c.exists():
                raw_path = str(c)
                break

        for rec in load_normalized_from_file(nf):
            insert_record(conn, table, rec, raw_path, str(nf))
    conn.commit()
    conn.close()
    print(f"Ingested files into {db_path} (table: {table})")


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser()
    parser.add_argument("--db", default=str(DEFAULT_DB), help="Path to SQLite DB file")
    parser.add_argument("--data-dir", default=str(DEFAULT_DB.parent), help="Directory with normalized JSON files")
    parser.add_argument("--pattern", default="*_sample_*.json", help="Glob pattern to match normalized files")
    parser.add_argument("--table", default="staging_opportunities", help="DB table name to write to")
    args = parser.parse_args()
    ingest(Path(args.db), Path(args.data_dir), pattern=args.pattern, table=args.table)
