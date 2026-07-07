import re
from typing import Any, Dict, List, Optional

_CARET_TAG_RE = re.compile(r"<i[^>]*></i>")
_SUBSCRIBER_SPAN_RE = re.compile(
    r'<span class="(?P<status>active|inactive)">\s*<i[^>]*></i>\s*(?P<inner>.*?)</span>',
    re.DOTALL,
)


def parse_category_breadcrumb(raw: Optional[str]) -> List[str]:
    """Splits the upstream API's HTML breadcrumb string into a clean list of names.

    Upstream returns category as e.g. 'Generic <i class="fa fa-caret-right"></i> ...' -
    presentation markup that has no business being in a JSON API response.
    """
    if not raw:
        return []
    parts = _CARET_TAG_RE.split(raw)
    return [p.strip() for p in parts if p.strip()]


def parse_subscribers(raw: Optional[str]) -> List[Dict[str, Any]]:
    """Parses upstream's HTML subscriber list into structured records.

    Upstream returns e.g. '<span class="active"><i class="fa-solid fa-circle"></i>
    Company <i class="fa fa-caret-right"></i> username</span>' blocks, optionally
    joined by <br> - again, markup that belongs in a UI layer, not a data API.
    """
    if not raw:
        return []
    subscribers = []
    for match in _SUBSCRIBER_SPAN_RE.finditer(raw):
        inner_parts = [p.strip() for p in _CARET_TAG_RE.split(match.group("inner")) if p.strip()]
        subscribers.append(
            {
                "status": match.group("status"),
                "company": inner_parts[0] if inner_parts else None,
                "username": inner_parts[1] if len(inner_parts) > 1 else None,
            }
        )
    return subscribers


def enrich_category_and_subscribers(items: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """Adds category_path / subscribers alongside the raw fields, in place."""
    for item in items:
        if "category" in item:
            item["category_path"] = parse_category_breadcrumb(item["category"])
        if "subscriptions" in item:
            item["subscribers"] = parse_subscribers(item["subscriptions"])
    return items
