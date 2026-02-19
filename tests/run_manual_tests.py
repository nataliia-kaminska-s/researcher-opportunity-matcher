from backend.connectors.ckan_connector import normalize_ckan_result


def run():
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
    print("MANUAL TESTS: PASS")


if __name__ == "__main__":
    run()
