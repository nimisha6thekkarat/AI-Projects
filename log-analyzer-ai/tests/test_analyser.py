import pytest
from analyser import analyze_entries  # Replace with actual module path

@pytest.fixture
def mock_ai(monkeypatch):
    monkeypatch.setattr(
        "analyser.diagnose_missing_url",
        lambda url, reason: f"AI-DIAGNOSED: {reason} @ {url}"
    )

@pytest.mark.usefixtures("mock_ai")
def test_analyze_entries_basic_case():
    parsed_data = {
        "title_urls": ["url-a", "url-b", "url-c"],
        "core_api_map": {
            "url-a": {"pid": "p1", "title": "Title A"},
            "url-b": {"pid": "p2", "title": "Title B"},
        },
        "detail_items": [
            {"url": "url-a", "name": "Detail A"},
        ],
        "retry_failures": {
            "url-b": {"reason": "Timeout"}
        }
    }

    result = analyze_entries(parsed_data)

    # Summary checks
    assert result["summary"] == {
        "total_urls": 3,
        "urls_with_pid": 2,
        "titles_with_detail_item": 1,
        "retry_failures": 1,
        "missing": 2,
        "matched": 1,
    }

    # Matched entry
    assert result["matched"] == [{
        "url": "url-a",
        "pid": "p1",
        "title": "Detail A"
    }]

    # Missing entries
    missing_urls = {entry["url"] for entry in result["missing"]}
    assert missing_urls == {"url-b", "url-c"}

    for entry in result["missing"]:
        assert "ai_reason" in entry
        assert entry["ai_reason"].startswith("AI-DIAGNOSED:")

    # Retry reason override
    assert any(entry["reason"] == "Timeout" for entry in result["missing"] if entry["url"] == "url-b")
    assert any(entry["reason"] == "PID not found in CORE API entry" for entry in result["missing"] if entry["url"] == "url-c")
