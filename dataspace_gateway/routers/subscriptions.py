from typing import Any, List

from fastapi import APIRouter, Depends, HTTPException

from dataspace_gateway.config import settings
from dataspace_gateway.dependencies import get_authorization_header
from dataspace_gateway.formatting import enrich_category_and_subscribers
from dataspace_gateway.schemas import IdResponse, RespondToRequest, SubscriptionCreate
from dataspace_gateway.upstream_client import upstream_request

router = APIRouter(prefix="/subscriptions", tags=["Subscriptions"])


@router.get(
    "/mine",
    summary="List Data Offering services I'm subscribed to",
)
async def list_my_subscriptions(authorization: str = Depends(get_authorization_header)) -> List[Any]:
    response = await upstream_request(
        "GET", settings.enpower_base_url, "/api/datalist/my_subscriptions", authorization=authorization
    )
    return response.json()


@router.post(
    "",
    response_model=IdResponse,
    summary="Subscribe to a Data Offering service",
    description="Creates a pending subscription request for a Data Offering owned by another participant.",
)
async def create_subscription(
    payload: SubscriptionCreate, authorization: str = Depends(get_authorization_header)
) -> IdResponse:
    body = {"data_catalog_data_requests": {"id": None, **payload.model_dump()}}
    # The Middleware's POST /my_subscriptions is what actually creates the request;
    # the documented POST /new_subscription always 500s with "Form does not exist".
    response = await upstream_request(
        "POST",
        settings.enpower_base_url,
        "/api/dataset/v2/my_subscriptions",
        authorization=authorization,
        json=body,
    )
    return response.json()


@router.get(
    "/requests",
    summary="List subscription requests received on my Data Offerings",
    description="Returns requests from other participants asking to subscribe to your Data Offerings.",
)
async def list_incoming_requests(authorization: str = Depends(get_authorization_header)) -> List[Any]:
    response = await upstream_request(
        "GET",
        settings.enpower_base_url,
        "/api/datalist/requests_on_offered_services",
        authorization=authorization,
    )
    return enrich_category_and_subscribers(response.json())


@router.post(
    "/requests/{request_id}/respond",
    response_model=IdResponse,
    summary="Accept or reject a pending subscription request",
    description=(
        "Set `status` to `accept` or `reject`. Any additional fields from the request row "
        "(as returned by GET /subscriptions/requests) may be included and are forwarded as-is."
    ),
)
async def respond_to_request(
    request_id: str,
    payload: RespondToRequest,
    authorization: str = Depends(get_authorization_header),
) -> IdResponse:
    body = {"data_catalog_data_requests": payload.model_dump()}
    response = await upstream_request(
        "POST",
        settings.enpower_base_url,
        "/api/dataset/v2/requests_on_offered_services",
        authorization=authorization,
        params={"id": request_id},
        json=body,
    )
    result = response.json()

    # The Middleware has been observed returning a 200 here while silently
    # leaving the request's status unchanged - re-read it back and only report
    # success if the status actually took, instead of trusting the response.
    verify_response = await upstream_request(
        "GET",
        settings.enpower_base_url,
        "/api/datalist/requests_on_offered_services",
        authorization=authorization,
    )
    not_applied = any(
        row.get("request_id") == request_id and row.get("status") != payload.status
        for row in verify_response.json()
    )
    if not_applied:
        raise HTTPException(
            status_code=502,
            detail={
                "error_code": "upstream_response_not_applied",
                "message": (
                    "The dataspace Middleware accepted this response but didn't actually "
                    "update the request's status - contact the dataspace operator."
                ),
            },
        )
    return result
