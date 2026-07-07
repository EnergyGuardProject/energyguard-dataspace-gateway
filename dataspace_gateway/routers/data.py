import base64
import re
from typing import Any, List, Optional

from fastapi import APIRouter, Depends, HTTPException, Query, Response

from dataspace_gateway.config import settings
from dataspace_gateway.dependencies import get_authorization_header, get_download_authorization
from dataspace_gateway.schemas import ProvideDataRequest, ProvideDataResponse
from dataspace_gateway.upstream_client import upstream_request

router = APIRouter(prefix="/data", tags=["Data Provide / Consume"])

_DATA_URI_RE = re.compile(r"^data:(?P<mime>[^;]+);base64,(?P<data>.+)$", re.DOTALL)


@router.post(
    "/provide",
    response_model=ProvideDataResponse,
    summary="Provide (upload) a data file for a Data Offering",
    description="Sends a Data Entity to the True Connector local API for a given Data Offering.",
)
async def provide_data(
    payload: ProvideDataRequest, authorization: str = Depends(get_authorization_header)
) -> ProvideDataResponse:
    response = await upstream_request(
        "POST",
        settings.connector_base_url,
        "/api/provide-data",
        authorization=authorization,
        json=payload.model_dump(),
    )
    return response.json()


@router.get(
    "/consumed",
    summary="List Data Entities published under my subscriptions",
)
async def list_consumed_data(authorization: str = Depends(get_authorization_header)) -> List[Any]:
    response = await upstream_request(
        "GET", settings.enpower_base_url, "/api/datalist/data_consumed", authorization=authorization
    )
    return response.json()


@router.get(
    "/consumed/{entity_id}",
    summary="Download a Data Entity by its ID",
    description=(
        "Returns the actual decoded file content of a consumed Data Entity. "
        "The connector's own response wraps the file as a base64 data URI in JSON - "
        "this endpoint decodes that and returns the real bytes with the right content type. "
        "Accepts the access token either as a normal Authorization header or as a "
        "?token= query parameter, so this one endpoint can be used as a plain download "
        "link (e.g. `<a href>`) without attaching a custom header."
    ),
)
async def consume_data_by_id(
    entity_id: str,
    filename: Optional[str] = Query(
        None, description="Optional filename (e.g. from GET /data/consumed) to set on the download"
    ),
    authorization: str = Depends(get_download_authorization),
) -> Response:
    response = await upstream_request(
        "GET",
        settings.connector_base_url,
        "/api/consume-data/by-id",
        authorization=authorization,
        params={"id": entity_id},
    )

    try:
        body = response.json()
    except ValueError:
        body = None

    if isinstance(body, dict) and "filedata" in body:
        match = _DATA_URI_RE.match(body["filedata"] or "")
        if not match:
            raise HTTPException(
                status_code=502, detail="Connector returned an unrecognized filedata format"
            )
        content = base64.b64decode(match.group("data"))
        media_type = match.group("mime")
    else:
        # Fallback in case a connector version returns the raw file directly.
        content = response.content
        media_type = response.headers.get("content-type", "application/octet-stream")

    headers = {}
    if filename:
        headers["Content-Disposition"] = f'attachment; filename="{filename}"'
    return Response(content=content, media_type=media_type, headers=headers)
