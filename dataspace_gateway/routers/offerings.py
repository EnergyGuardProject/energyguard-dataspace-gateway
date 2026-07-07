from typing import Any, List

from fastapi import APIRouter, Depends

from dataspace_gateway.config import settings
from dataspace_gateway.dependencies import get_authorization_header
from dataspace_gateway.formatting import enrich_category_and_subscribers
from dataspace_gateway.schemas import DataOfferingCreate, IdResponse
from dataspace_gateway.upstream_client import upstream_request

router = APIRouter(prefix="/offerings", tags=["Data Offerings"])


@router.post(
    "",
    response_model=IdResponse,
    summary="Create a new Data Offering service",
    description="Creates a Data Offering under a chosen Category/Sub-Category/Business Object.",
)
async def create_offering(
    payload: DataOfferingCreate, authorization: str = Depends(get_authorization_header)
) -> IdResponse:
    body = {"data_catalog_data_offerings": {"id": None, **payload.model_dump()}}
    response = await upstream_request(
        "POST",
        settings.enpower_base_url,
        "/api/dataset/v2/my_offered_services",
        authorization=authorization,
        json=body,
    )
    return response.json()


@router.get(
    "/mine",
    summary="List my own Data Offering services",
    description="Returns the Data Offerings you have created, with their IDs and statuses.",
)
async def list_my_offerings(authorization: str = Depends(get_authorization_header)) -> List[Any]:
    response = await upstream_request(
        "GET", settings.enpower_base_url, "/api/datalist/my_offered_services", authorization=authorization
    )
    return enrich_category_and_subscribers(response.json())


@router.get(
    "/catalog",
    summary="List predefined service types (Category / Sub-Category / Business Object)",
    description="Returns the available Business Objects to use when creating a new Data Offering.",
)
async def list_business_objects(authorization: str = Depends(get_authorization_header)) -> List[Any]:
    response = await upstream_request(
        "GET", settings.enpower_base_url, "/api/datalist/cross_platform_service", authorization=authorization
    )
    return response.json()


@router.get(
    "/available",
    summary="Discover Data Offering services available from other participants",
    description="Returns the full catalog of Data Offerings published by other Data Space participants.",
)
async def list_available_offerings(authorization: str = Depends(get_authorization_header)) -> List[Any]:
    response = await upstream_request(
        "GET", settings.enpower_base_url, "/api/datalist/my_catalog", authorization=authorization
    )
    return enrich_category_and_subscribers(response.json())
