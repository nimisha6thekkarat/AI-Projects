# 📄 Log Analysis App Design Document

**Title:**  
Title URL Validation & DetailItem Check for Crawler Logs

**Author:**  
Nimisha Thekkarath

**Date:**  
June 26, 2025

---

## 1. 🧭 Objective
The purpose of this app is to analyze crawler log files (`.txt` format) to ensure data consistency in the following areas:

- All requested title URLs are captured and uniquely tracked.
- Each title URL/PID results in a `DetailItem` entry creation.
- Missing or malformed entries are identified and reported.

---

## 2. 📂 Input Specification

**Log File Format:**  
Plaintext `.txt` file generated from crawl logs.

**Key Patterns:**

- **Title URLs:**
  ```
  Adding additional url https://www.primevideo.com/detail/<pid>
  ```

- **Request Count:**
  ```
  1077 request(s) generated.
  ```

- **Core API Entries:**
  ```
  CORE API ENTRY
  ["<uuid>", "<title>", "<platform>", "<url>", "<pid>"]
  ```

- **DetailItem Block:**
  ```json
  {
    "_type": "DetailItem",
    ...
    "id": "<pid>",
    "url": "https://www.primevideo.com/detail/<pid>"
  }
  ```

- **Retry Failures:**
  ```
  Retry limit reached for Title: "<title>", URL: <url>, PID <pid>
  ```

---

## 3. ⚙️ System Architecture

```
        ┌────────────────┐
        │  Log (.txt)    │
        └──────┬─────────┘
               │
      ┌────────▼────────┐
      │   Parser Module │◄────────┐
      └────────┬────────┘         │
               │                  │
   ┌───────────▼───────────┐      │
   │    Analyzer Module    │      │
   └───────────┬───────────┘      │
               │                  │
       ┌───────▼────────┐         │
       │ Report Module  │         │
       └────────────────┘         │
               │                  │
        ┌──────▼───────┐          │
        │ JSON / CSV   │◄─────────┘
        └──────────────┘
```

---

## 4. 🧱 Module Breakdown

### 4.1 `main.py`
- CLI or GUI entry point
- Accepts input `.txt` file
- Invokes parser, analyzer, and report

### 4.2 `parser.py`
Responsible for:
- Extracting:
  - Title URLs
  - Request count
  - PID entries (from CORE API ENTRY)
  - DetailItem JSON blocks
  - Retry limit failures

Technologies: `re`, `json`, stateful line-by-line iteration

### 4.3 `analyzer.py`
Performs checks:
- Every title URL has a corresponding PID
- Every PID exists in a `DetailItem` block
- Flags missing/malformed entries

Creates:
- List of `unmatched_urls`
- `summary` dictionary with counts

### 4.4 `report.py`
Formats results into:
- JSON
- CSV (optional)

Report includes:
- `url`, `pid`, `matched`, `reason`
- Aggregated stats

---

## 5. 📌 Data Flow

- **Input:** Raw `.txt` file

- **Parser Output:**
  ```python
  title_urls = set()
  pid_map = {url: pid}
  detail_items = {pid: metadata}
  retry_failures = {pid: {"url": ..., "title": ..., "reason": ...}}
  ```

- **Analyzer Output:**
  ```python
  report = {"matched": [...], "missing": [...], "summary": {...}}
  ```

- **Report Output:** `analysis_report.json`

---

## 6. 📊 Output Examples

```json
{
  "summary": {
    "total_urls": 1077,
    "urls_with_pid": 1068,
    "pids_with_detail_item": 1060,
    "missing": 17
  },
  "missing_entries": [
    {
      "url": "https://www.primevideo.com/detail/XYZ",
      "reason": "PID not found in CORE API entry"
    },
    {
      "pid": "ABC123",
      "reason": "No DetailItem generated"
    }
  ]
}
```

---

## 7. 🧪 Testing Plan

- Use sample logs with known inconsistencies
- Unit tests per module using `pytest`
- Edge cases:
  - Repeated URLs
  - Malformed `DetailItem`s
  - Incomplete entries
  - Retry failures with correct format

---

## 8. 🧰 Tech Stack

| Component    | Technology             |
|--------------|------------------------|
| Language     | Python 3.10+           |
| Dependencies | `re`, `json`, `csv`, `argparse`, `typing` |
| Output       | JSON (default), CSV    |
| CLI Tool     | Optional via `argparse` or `click` |
| GUI          | Streamlit              |
| AI Layer     | OpenAI / Local LLM     |

---

## 9. 🚀 Future Enhancements

- Streamlit-based interactive UI
- Visual dashboards or graphs (for match/failure distribution)
- Support for bulk log folders
- Template support for different content platforms (e.g., Netflix, Disney+)
- Natural language interface using LangChain or ChatGPT

---

## 10. 🏁 Conclusion

This log analyzer app enables robust validation of crawl pipeline health by ensuring URL-to-DetailItem consistency, with retry failure analysis and AI-powered summarization. It reduces manual inspection, increases transparency, and provides actionable insights to improve ingestion reliability.

---
