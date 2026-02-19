"""Simple wrapper to run available connector harvests and write timestamped raw+normalized files.

Usage:
  python backend/run_connectors.py

This calls `ckan_connector.save_raw_and_normalized` and `nrfu_scraper.save_samples` and ensures outputs are timestamped.
"""
from __future__ import annotations

from datetime import datetime


def run_all():
    stamp = datetime.utcnow().isoformat().replace(':', '-')
    print(f"Running connectors (timestamp {stamp})")
    try:
        from backend.connectors import ckan_connector
        # ckan_connector.save_raw_and_normalized writes to data/ckan_raw.json and sample file
        ckan_connector.save_raw_and_normalized(q="грант", rows=20)
        print("CKAN connector finished")
    except Exception as e:
        print("CKAN connector failed:", e)

    try:
        from backend.connectors import nrfu_scraper
        nrfu_scraper.save_samples()
        print("NRFU scraper finished")
    except Exception as e:
        print("NRFU scraper failed:", e)


if __name__ == "__main__":
    run_all()
