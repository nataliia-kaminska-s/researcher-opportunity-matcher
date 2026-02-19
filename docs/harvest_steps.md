# Harvest sources, steps and links

This document lists the programmatic sources, example endpoints and step-by-step reproduction notes used by the prototype ingestion work for Ukrainian grants and contests.

## CKAN (data.gov.ua / opendata.gov.ua)

- Primary API (CKAN package_search):
  - Example: https://data.gov.ua/api/3/action/package_search?q=грант&rows=20
  - Help: https://data.gov.ua/api/3/action/help_show?name=package_search
- What we extract:
  - package id, title, notes (description), metadata_modified, tags, resources (CSV/XLS/PDF links)
- Repro steps:
  1. Call package_search with `q` (not `query`) and `rows` to limit results.
  2. Inspect `result.results` for dataset packages and `resources` array for files.
  3. Follow `resources[].url` (or `cache_url`) to download attachments.

## NRFU (nrfu.org.ua)

- WP REST endpoints exposed on the main site:
  - Example: https://nrfu.org.ua/wp-json/wp/v2/posts?per_page=5&search=конкурс
- Contest list page (HTML):
  - https://nrfu.org.ua/contests/current-calls/
- Observed artifacts:
  - Many contests link to PDF/DOCX under `/wp-content/uploads/...` — these are good canonical attachments.
- Repro steps:
  1. Try WP REST: GET `/wp-json/wp/v2/posts` with `search` or `categories` to find contest posts.
  2. If REST not available for a subsite (e.g., grants portal), fetch the contest listing page and parse anchor tags for PDF/DOC links and detail pages.
  3. Extract title, date, description (strip HTML), and attachments; store provenance (source URL, fetch timestamp, extraction method).

## Notes and civility

- Respect robots.txt and site terms. Throttle requests (sleep 1–2s between hits) and add a descriptive User-Agent.
- For high-volume or frequent harvesting contact the site administrators and negotiate an API key / feed where possible.

## Files added by this run

- `backend/connectors/ckan_connector.py` — prototype CKAN search + normalizer.
- `backend/connectors/nrfu_scraper.py` — WP REST first, HTML fallback scraper.
- `data/ckan_sample_normalized.json` — normalized sample from CKAN.
- `data/nrfu_contest_sample_wp.json` or `data/nrfu_contest_sample_scraped.json` — NRFU sample results (depending on availability).

## How to run (Windows PowerShell)

Install dependencies (recommended virtualenv):

```powershell
python -m venv .venv; .\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

Run CKAN connector:

```powershell
python backend\connectors\ckan_connector.py --q "грант" --rows 20
```

Run NRFU scraper:

```powershell
python backend\connectors\nrfu_scraper.py
```

## Links referenced during discovery

- CKAN / data.gov.ua API: https://data.gov.ua/api/3/action/
- Example CKAN query used: https://data.gov.ua/api/3/action/package_search?q=грант&rows=20
- NRFU contests page: https://nrfu.org.ua/contests/current-calls/
- NRFU WP REST index (manifest): https://nrfu.org.ua/wp-json/

Keep this doc under `docs/` and extend it as you add connectors for other sources (EURAXESS, CORDIS, institutional sites).
