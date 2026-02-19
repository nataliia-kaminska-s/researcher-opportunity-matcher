from backend.connectors.ckan_connector import normalize_ckan_result


def sample_ckan_payload():
    return {
        "result": {
            "results": [
                {
                    "id": "pkg-1",
                    "title": "Test Grant Dataset",
                    "notes": "Detailed description of grant",
                    "tags": [{"name": "грант"}, {"name": "конкурс"}],
                    "resources": [{"url": "https://example.org/file.pdf"}],
                    "metadata_modified": "2026-02-01T12:00:00",
                }
            ]
        }
    }


def test_normalize_ckan_result_basic():
    payload = sample_ckan_payload()
    normalized = normalize_ckan_result(payload)
    assert isinstance(normalized, list)
    assert len(normalized) == 1
    rec = normalized[0]
    assert rec["source"] == "data.gov.ua"
    assert rec["source_id"] == "pkg-1"
    assert rec["title"] == "Test Grant Dataset"
    assert "https://example.org/file.pdf" in rec["resources"]
import json

from backend.connectors.ckan_connector import normalize_ckan_result


def test_normalize_ckan_result_basic():
    sample_payload = {
        "result": {
            "results": [
                {
                    "id": "abc-123",
                    "title": "Test Dataset",
                    "notes": "Some description",
                    "tags": [{"name": "грант"}, {"name": "конкурс"}],
                    "resources": [{"url": "https://example.org/file.pdf"}],
                    "metadata_modified": "2026-01-01T00:00:00",
                }
            ]
        }
    }

    normalized = normalize_ckan_result(sample_payload)
    assert isinstance(normalized, list)
    assert len(normalized) == 1
    item = normalized[0]
    assert item["source_id"] == "abc-123"
    assert item["title"] == "Test Dataset"
    assert "https://example.org/file.pdf" in item["resources"]
