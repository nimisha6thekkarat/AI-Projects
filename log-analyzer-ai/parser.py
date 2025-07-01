# parser.py
import re
import json
import io
from analyser import analyze_entries

def parse_log_file(file_obj):
    title_urls = set()
    core_api_map = {}
    detail_items = []
    retry_failures = {}
    buffer = []
    
    collecting_json = False   
    open_braces = 0
    for line in file_obj:
        line = line.strip()

        # Title URLs
        if "Adding additional url" in line:
            match = re.search(r'(https?://[^\s]+)', line)
            if match:
                title_urls.add(match.group(1))
        # CORE API entry
        elif 'CORE API ENTRY #' in line:
            try:
                json_lines = []
                # Keep reading lines until the JSON array ends
                while True:
                    next_line = next(file_obj).strip()
                    json_lines.append(next_line)
                    if next_line == "]":
                        break
                entry = json.loads("\n".join(json_lines))
                core_api_map[entry[3]] = {
                    "pid": entry[4],
                    "title": entry[1]
                }
            except Exception as e:
                print(f"Error parsing entry: {e}")
                continue
        # Retry failure
        elif "Gave up retrying <GET" in line:
            try:
                # Split to extract URL between <GET ...>
                start = line.index("<GET ") + 5
                end = line.index(">", start)
                url = line[start:end]

                # Extract reason after the last colon
                if ":" in line:
                    reason = line.rsplit(":", 1)[-1].strip()
                else:
                    reason = "unknown"

                retry_failures[url] = {
                    "url": url,
                    "reason": reason
                }

            except Exception as e:
                print(f"[Retry Parse Error] Line: {line} — {e}")

        # Start of DetailItem block
        if "scrapy.core.scraper" in line and "Scraped from" in line:
            buffer = []
            collecting_json = False  # Wait until '{'
            open_braces = 0
            continue

        # Start of JSON
        if not collecting_json and line.startswith("{"):
            collecting_json = True
            open_braces = 1
            buffer.append(line)
            continue

        # Collecting JSON lines
        if collecting_json:
            buffer.append(line)
            open_braces += line.count("{")
            open_braces -= line.count("}")
            if open_braces == 0:
                try:
                    raw_json = "\n".join(buffer)
                    item = json.loads(raw_json)
                    if item.get("_type") == "DetailItem":
                        detail_items.append(item)
                except json.JSONDecodeError as e:
                    print(f"Failed to parse DetailItem JSON: {e}")
                buffer = []
                collecting_json = False
    summary = {
        "total_urls": len(title_urls),
        "core_api_mapped": len(core_api_map),
        "detail_items": len(detail_items),
        "retry_failures": len(retry_failures)
    }

    return {
        "title_urls": title_urls,
        "core_api_map": core_api_map,
        "detail_items": detail_items,
        "retry_failures": retry_failures,
        "summary": summary
    }

# Local test block
if __name__ == "__main__":
    file_path = "log_amazon.de_discovery_615.txt"  # Update if needed
    with open(file_path, "r", encoding="utf-8") as f:
        content = f.read()
    file_obj = io.StringIO(content)
    parsed_data = parse_log_file(file_obj)
    report = analyze_entries(parsed_data)
    import pprint
    pprint.pprint(parsed_data["summary"])
    pprint.pprint(report)

