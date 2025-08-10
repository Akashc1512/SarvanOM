from __future__ import annotations

import re
from typing import Any, Dict, List

import requests


WIKIPEDIA_API_URL = "https://en.wikipedia.org/w/api.php"


def _strip_html(html_snippet: str) -> str:
    """
    Remove HTML tags and decode basic entities from MediaWiki snippets.

    Args:
        html_snippet: HTML snippet returned by MediaWiki search results

    Returns:
        Plain text string
    """
    # Remove HTML tags
    text = re.sub(r"<[^>]+>", "", html_snippet or "")
    # Replace common HTML entities
    text = (
        text.replace("&quot;", '"')
        .replace("&apos;", "'")
        .replace("&amp;", "&")
        .replace("&lt;", "<")
        .replace("&gt;", ">")
    )
    # Collapse whitespace
    text = re.sub(r"\s+", " ", text).strip()
    return text


def _normalize_result(item: Dict[str, Any]) -> Dict[str, str]:
    """
    Normalize a MediaWiki search item into {title, url, snippet}.
    """
    title: str = item.get("title", "").strip()
    url_title = title.replace(" ", "_")
    url = f"https://en.wikipedia.org/wiki/{url_title}" if title else ""
    snippet_html: str = item.get("snippet", "")
    snippet = _strip_html(snippet_html)
    return {"title": title, "url": url, "snippet": snippet}


def search_wikipedia(query: str, top_k: int = 5, timeout_seconds: float = 8.0) -> List[Dict[str, str]]:
    """
    Search Wikipedia via MediaWiki API and return top results.

    - No API key required
    - Deduplicates by title
    - Ranks primarily by wordcount (desc) then index order

    Args:
        query: Search query string
        top_k: Max number of results to return
        timeout_seconds: HTTP request timeout

    Returns:
        List of dicts with keys: title, url, snippet (up to top_k entries). Empty list on failure.
    """
    if not query or not query.strip():
        return []

    params = {
        "action": "query",
        "list": "search",
        "srsearch": query.strip(),
        "srlimit": min(max(top_k * 3, 10), 50),  # over-fetch, then rank/dedupe
        "format": "json",
        "utf8": 1,
        "origin": "*",  # CORS-friendly when used from browsers (harmless here)
    }

    try:
        resp = requests.get(WIKIPEDIA_API_URL, params=params, timeout=timeout_seconds)
        if not resp.ok:
            return []
        data = resp.json() or {}
        search_items = (data.get("query", {}).get("search", []) or [])
        if not search_items:
            return []

        # Rank: prefer larger wordcount, keep original order as tiebreaker
        ranked = sorted(
            search_items,
            key=lambda it: (it.get("wordcount", 0), -it.get("size", 0)),
            reverse=True,
        )

        # Normalize and dedupe by lowercase title
        seen: set[str] = set()
        results: List[Dict[str, str]] = []
        for item in ranked:
            norm = _normalize_result(item)
            title_key = norm["title"].lower()
            if not norm["title"] or title_key in seen:
                continue
            seen.add(title_key)
            results.append(norm)
            if len(results) >= top_k:
                break

        return results
    except Exception:
        # Graceful failure
        return []


