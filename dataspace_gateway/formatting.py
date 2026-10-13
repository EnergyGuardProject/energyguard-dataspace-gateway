import re
from datetime import datetime, timezone
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


def parse_timestamp(raw: Optional[str]) -> Optional[str]:
    """Normalizes upstream's mixed timestamp formats to ISO-8601 UTC.

    Some lists return '13/10/2026 09:47', others '2026-10-13T09:47:14Z' - both are UTC.
    Returns None for anything unrecognized rather than guessing.
    """
    if not raw:
        return None
    for fmt in ("%d/%m/%Y %H:%M", "%Y-%m-%dT%H:%M:%SZ"):
        try:
            parsed = datetime.strptime(raw, fmt).replace(tzinfo=timezone.utc)
        except ValueError:
            continue
        return parsed.isoformat().replace("+00:00", "Z")
    return None


def enrich_category_and_subscribers(items: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """Adds clean, structured fields alongside the raw upstream ones, in place.

    category_path / subscribers (from HTML markup), created_at (ISO timestamp) and
    requester_company / requester_username (split from 'Company <caret> user').
    """
    for item in items:
        if "created_on" in item:
            item["created_at"] = parse_timestamp(item["created_on"])
        if "user_requesting" in item:
            parts = parse_category_breadcrumb(item["user_requesting"])
            item["requester_company"] = parts[0] if parts else None
            item["requester_username"] = parts[1] if len(parts) > 1 else None
        if "category" in item:
            item["category_path"] = parse_category_breadcrumb(item["category"])
        if "subscriptions" in item:
            item["subscribers"] = parse_subscribers(item["subscriptions"])
    return items
