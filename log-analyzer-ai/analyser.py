def analyze_entries(parsed_data):
    title_urls = parsed_data["title_urls"]
    core_api_map = parsed_data["core_api_map"]
    detail_items_list = parsed_data["detail_items"]
    retry_failures = parsed_data["retry_failures"]

    # Key detail items by their "url" field
    detail_items_by_url = {
        item.get("url"): item for item in detail_items_list if item.get("url")
    }

    matched = []
    missing = []

    for url in title_urls:
        entry = core_api_map.get(url)
        if not entry:
            missing.append({
                "url": url,
                "pid": None,
                "reason": "PID not found in CORE API entry"
            })
            continue

        pid = entry.get("pid")
        title = entry.get("title", "N/A")

        detail = detail_items_by_url.get(url)
        new_list=[]
        if not detail:
            reason = "No DetailItem generated"
            if url in retry_failures:
                reason = retry_failures[url]["reason"]
            missing.append({
                "url": url,
                "pid": pid,
                "title": title,
                "reason": reason
            })
        else:
            matched.append({
                "url": url,
                "pid": pid,
                "title": detail.get("name", title)
            })

    summary = {
        "total_urls": len(title_urls),
        "urls_with_pid": len(core_api_map),
        "titles_with_detail_item": len(detail_items_by_url),
        "retry_failures": len(retry_failures),
        "missing": len(missing),
        "matched": len(matched),
    }

    return {
        "matched": matched,
        "missing": missing,
        "summary": summary,
    }
    
