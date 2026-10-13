from dataspace_gateway.formatting import enrich_category_and_subscribers, parse_timestamp


def test_parse_timestamp_handles_both_upstream_formats():
    assert parse_timestamp("13/10/2026 09:47") == "2026-10-13T09:47:00Z"
    assert parse_timestamp("2026-10-13T09:47:14Z") == "2026-10-13T09:47:14Z"
    assert parse_timestamp("garbage") is None
    assert parse_timestamp(None) is None


def test_enrich_splits_requester_and_adds_created_at():
    item = {
        "created_on": "13/10/2026 09:47",
        "user_requesting": 'NTUA <i class="fa fa-caret-right"></i> atzort',
    }
    enrich_category_and_subscribers([item])
    assert item["created_at"] == "2026-10-13T09:47:00Z"
    assert item["requester_company"] == "NTUA"
    assert item["requester_username"] == "atzort"
