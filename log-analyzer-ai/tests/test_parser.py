import io
import os
import sys
import pytest
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from parser import parse_log_file

@pytest.fixture
def sample_file_obj():
    file_path = os.path.join(os.path.dirname(__file__), "test_input.txt")
    with open(file_path, "r", encoding="utf-8") as f:
        content = f.read()
    return io.StringIO(content)  # Mimics uploaded_file.getvalue().decode("utf-8")

def test_summary_counts(sample_file_obj):
    result = parse_log_file(sample_file_obj)
    summary = result["summary"]

    assert summary["total_urls"] == 3
    assert summary["core_api_mapped"] == 3
    assert summary["detail_items"] == 2
    assert summary["retry_failures"] == 1

def test_detail_item_contents(sample_file_obj):
    result = parse_log_file(sample_file_obj)
    detail_items = result["detail_items"]

    assert len(detail_items) == 2
    item = detail_items[0]
    assert item["id"] == "B00OU7BZ62"
    assert item["url"].startswith("https://www.amazon.de/")
