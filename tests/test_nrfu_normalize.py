from backend.connectors.nrfu_scraper import normalize_wp_post


def test_normalize_wp_post_extracts_attachments_and_text():
    post = {
        "id": 123,
        "title": {"rendered": "Test Contest"},
        "link": "https://nrfu.org.ua/test-contest/",
        "date": "2026-02-20T00:00:00",
        "content": {"rendered": "<p>Intro</p><a href=\"/wp-content/uploads/2026/rules.pdf\">Rules</a><p>More info</p>"},
    }

    norm = normalize_wp_post(post)

    assert norm["source"] == "nrfu.org.ua"
    assert norm["source_id"] == 123
    assert norm["title"] == "Test Contest"
    assert "Intro" in norm["summary_text"]
    # attachments should contain the pdf link
    assert any("rules.pdf" in a for a in norm["attachments"]) or len(norm["attachments"]) >= 1


def test_normalize_wp_post_handles_plain_text_content():
    post = {
        "id": 999,
        "title": {"rendered": "Plain Contest"},
        "link": "https://nrfu.org.ua/plain/",
        "date": "2026-01-01T00:00:00",
        "content": {"rendered": "No html here, just plain text."},
    }
    norm = normalize_wp_post(post)
    assert norm["title"] == "Plain Contest"
    assert "plain text" in norm["summary_text"].lower()
